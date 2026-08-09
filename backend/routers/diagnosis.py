"""
backend/routers/diagnosis.py
FastAPI router for circuit fault diagnosis, verification, CV analysis, GNN checks, and CAD outputs.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
import json
import os
import math
import numpy as np

from backend.services.fault_classifier import classify_faults
from backend.services.circuit_cv import analyze_breadboard_photo
from backend.services.circuit_gnn import predict_circuit_anomaly
from backend.services.waveform_cv import analyze_cro_waveform
from backend.services.diagram_generator import generate_and_save_cad_files

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

class PredictionRequest(BaseModel):
    experiment_id: str
    parameters: Dict[str, float]

class VerificationRequest(BaseModel):
    experiment_id: str
    measured_values: Dict[str, str]
    expected_values: Dict[str, str]
    symptom: Optional[str] = ""


# ── 1. Digital Twin Prediction (with Bode & Load Line Plotters) ──
@router.post("/predict-twin")
def predict_twin_values(req: PredictionRequest):
    """
    Acts as a Digital Twin for the electronics laboratory.
    Calculates expected output values, Bode frequency arrays, and DC load lines.
    """
    exp_id = req.experiment_id.lower()
    p = req.parameters
    predictions = {}
    
    try:
        if "cro_measurements" in exp_id:
            divs = p.get("divisions", 4.0)
            volts_div = p.get("volts_div", 1.0)
            predictions["Vp"] = divs * volts_div
            t_divs = p.get("time_divisions", 5.0)
            time_div = p.get("time_div_ms", 1.0)
            t = t_divs * time_div
            predictions["T_ms"] = t
            predictions["f_Hz"] = 1000.0 / t if t > 0 else 0.0

        elif "pn_junction" in exp_id:
            vd = p.get("Vd", 0.7)
            i0 = 1e-9
            vt = 0.026
            n = p.get("ideality_factor", 1.0)
            try:
                predictions["Id_mA"] = (i0 * (math.exp(vd / (n * vt)) - 1)) * 1000.0
            except OverflowError:
                predictions["Id_mA"] = 999.0
            predictions["dynamic_resistance_ohms"] = (n * vt) / (i0 * math.exp(vd / (n * vt)) + 1e-12)

        elif "zener" in exp_id:
            vin = p.get("Vin", 10.0)
            vz = p.get("Vz", 5.1)
            rs = p.get("Rs_ohms", 470.0)
            rl = p.get("RL_ohms", 1000.0)
            
            if vin > vz:
                i_s = (vin - vz) / rs
                i_l = vz / rl
                i_z = i_s - i_l
                predictions["Vout"] = vz
                predictions["Iz_mA"] = i_z * 1000.0
                predictions["IL_mA"] = i_l * 1000.0
                predictions["status"] = "Regulating" if i_z > 0.001 else "Unregulated (Starved)"
            else:
                v_out = vin * (rl / (rs + rl))
                predictions["Vout"] = v_out
                predictions["Iz_mA"] = 0.0
                predictions["IL_mA"] = (v_out / rl) * 1000.0
                predictions["status"] = "Unregulated (Below Breakdown)"

        elif "transistor_amplifier" in exp_id:
            vcc = p.get("Vcc", 12.0)
            r1 = p.get("R1_k", 33.0) * 1000.0
            r2 = p.get("R2_k", 10.0) * 1000.0
            rc = p.get("Rc_k", 3.3) * 1000.0
            re = p.get("Re_k", 1.0) * 1000.0
            beta = p.get("beta", 150.0)
            
            vb = vcc * (r2 / (r1 + r2))
            ve = vb - 0.7
            if ve < 0:
                ve = 0
            ic = ve / re
            vce = vcc - ic * (rc + re)
            
            vt = 0.026
            re_ac = vt / (ic + 1e-6)
            gain_with_bypass = rc / re_ac
            
            predictions["Q_Vbe"] = 0.7
            predictions["Q_Ic_mA"] = ic * 1000.0
            predictions["Q_Vce"] = max(vce, 0.2)
            predictions["Gain_with_CE"] = gain_with_bypass
            
            # Solve Frequency Response (Bode Plot)
            freqs = np.logspace(1, 6, 20)
            fl = 50.0   
            fh = 200000.0 
            
            bode_data = []
            for f in freqs:
                g = gain_with_bypass / (math.sqrt(1 + (fl / f)**2) * math.sqrt(1 + (f / fh)**2))
                g_db = 20 * math.log10(g + 1e-6)
                bode_data.append({"frequency_hz": float(f), "gain_db": float(g_db)})
            predictions["bode_plot"] = bode_data

            # Solve DC Load Line Plot (Ic vs Vce)
            # Ic_max = Vcc / (Rc + Re) when Vce = 0
            ic_max_ma = (vcc / (rc + re)) * 1000.0
            load_line_points = [
                {"Vce_V": 0.0, "Ic_mA": float(ic_max_ma)},
                {"Vce_V": float(vcc), "Ic_mA": 0.0}
            ]
            predictions["dc_load_line"] = load_line_points
            predictions["q_point"] = {"Vce_V": float(vce), "Ic_mA": float(ic * 1000.0)}

        elif "rc_filters" in exp_id:
            r = p.get("R_k", 10.0) * 1000.0
            c = p.get("C_uF", 0.01) * 1e-6
            fc = 1.0 / (2.0 * math.pi * r * c)
            predictions["cutoff_frequency_Hz"] = fc
            
            freqs = np.logspace(1, 5, 20)
            bode_data = []
            for f in freqs:
                g = 1.0 / math.sqrt(1 + (f / fc)**2)
                g_db = 20 * math.log10(g + 1e-6)
                phase = -math.atan(f / fc) * 180.0 / math.pi
                bode_data.append({"frequency_hz": float(f), "gain_db": float(g_db), "phase_deg": float(phase)})
            predictions["bode_plot"] = bode_data

        elif "oscillator" in exp_id or "phase_shift" in exp_id:
            r = p.get("R_k", 10.0) * 1000.0
            c = p.get("C_uF", 0.01) * 1e-6
            fo = 1.0 / (2.0 * math.pi * r * c * math.sqrt(6))
            predictions["fo_Hz"] = fo
            predictions["min_Rf_k"] = 290.0

        elif "wien_bridge" in exp_id:
            r = p.get("R_k", 10.0) * 1000.0
            c = p.get("C_uF", 0.01) * 1e-6
            fo = 1.0 / (2.0 * math.pi * r * c)
            predictions["fo_Hz"] = fo
            predictions["min_Rf_k"] = 20.0

        elif "bandgap" in exp_id or ("sem3" in exp_id and "exp1" in exp_id and "ce_npn" not in exp_id):
            temp_c = p.get("temp_c", 25.0)
            t = temp_c + 273.15
            eg = p.get("Eg_eV", 1.12)
            k = 8.617e-5
            c_val = 1e-8
            is_val = c_val * (t ** 3) * math.exp(-eg / (k * t))
            predictions["temp_K"] = t
            predictions["1_T_Kinv"] = 1.0 / t
            predictions["Is_uA"] = is_val * 1e6
            predictions["ln_Is_T3"] = math.log(is_val / (t ** 3))

        elif "darlington" in exp_id:
            beta1 = p.get("beta1", 100.0)
            beta2 = p.get("beta2", 150.0)
            re = p.get("Re_ohms", 1000.0)
            rs = p.get("Rs_ohms", 600.0)
            total_beta = beta1 * beta2
            r_in = total_beta * re
            a_v = (total_beta * re) / (rs + (total_beta * re))
            predictions["total_current_gain_beta"] = total_beta
            predictions["input_impedance_kOhm"] = r_in / 1000.0
            predictions["voltage_gain_Av"] = a_v

        elif "lissajous" in exp_id:
            ratio_x = p.get("ratio_x", 1.0)
            ratio_y = p.get("ratio_y", 2.0)
            y1 = p.get("Y1_intercept", 1.5)
            y2 = p.get("Y2_max", 3.0)
            try:
                phase_rad = math.asin(min(max(y1 / y2, 0.0), 1.0))
                phase_deg = phase_rad * 180.0 / math.pi
            except Exception:
                phase_deg = 0.0
            predictions["frequency_ratio_Fy_Fx"] = ratio_y / ratio_x
            predictions["phase_difference_degrees"] = phase_deg

        elif "bjt_characteristics" in exp_id or "ce_npn" in exp_id:
            ib = p.get("Ib_uA", 20.0)
            vce = p.get("Vce_V", 5.0)
            beta = p.get("beta", 150.0)
            va = p.get("Early_voltage_V", 100.0)
            if vce < 0.2:
                ic = (vce / 0.2) * (beta * ib * 1e-6)
            else:
                ic = (beta * ib * 1e-6) * (1.0 + vce / va)
            predictions["Ic_mA"] = ic * 1000.0
            predictions["base_current_mA"] = ib / 1000.0
            predictions["power_dissipation_mW"] = vce * (ic * 1000.0)

        elif "nmos_enh" in exp_id:
            vgs = p.get("Vgs_V", 4.0)
            vds = p.get("Vds_V", 5.0)
            vth = p.get("Vth_V", 2.0)
            kn = p.get("Kn_mA_V2", 50.0)
            if vgs < vth:
                ic = 0.0
                region = "Cutoff"
            elif vds < vgs - vth:
                ic = kn * (2 * (vgs - vth) * vds - vds ** 2)
                region = "Triode (Ohmic)"
            else:
                ic = kn * ((vgs - vth) ** 2)
                region = "Saturation"
            predictions["Id_mA"] = ic
            predictions["Vds_sat_V"] = max(vgs - vth, 0.0)
            predictions["operating_region"] = region

        elif "logic_gates" in exp_id or "adder" in exp_id:
            a = int(p.get("A", 1.0))
            b = int(p.get("B", 0.0))
            cin = int(p.get("Cin", 0.0))
            if "adder" in exp_id:
                s = a ^ b ^ cin
                c_out = (a & b) | (cin & (a ^ b))
                predictions["Sum"] = s
                predictions["Carry_Out"] = c_out
            else:
                predictions["AND"] = a & b
                predictions["OR"] = a | b
                predictions["NAND"] = int(not (a & b))
                predictions["NOR"] = int(not (a | b))
                predictions["XOR"] = a ^ b

        elif "rectifiers" in exp_id:
            v_rms = p.get("Vin_rms", 12.0)
            rl = p.get("RL_ohms", 1000.0)
            c = p.get("C_uF", 100.0)
            is_full_wave = p.get("full_wave", 1.0) == 1.0
            vm = math.sqrt(2) * v_rms
            if is_full_wave:
                v_dc_no_filter = (2 * vm) / math.pi
                ripple_factor_no_filter = 0.482
                f_ripple = 100.0
            else:
                v_dc_no_filter = vm / math.pi
                ripple_factor_no_filter = 1.21
                f_ripple = 50.0
            if c > 0:
                r_c_sec = rl * (c * 1e-6)
                v_ripple_pp = vm / (f_ripple * r_c_sec)
                v_dc_filtered = vm - (v_ripple_pp / 2.0)
                if v_dc_filtered < 0:
                    v_dc_filtered = 0
                predictions["Vout_DC_with_filter"] = v_dc_filtered
                predictions["Vripple_peak_to_peak"] = v_ripple_pp
                predictions["ripple_factor_with_filter"] = float(1.0 / (2 * math.sqrt(3) * f_ripple * rl * c * 1e-6))
            predictions["Vm_peak"] = vm
            predictions["Vdc_no_filter"] = v_dc_no_filter
            predictions["ripple_factor_no_filter"] = ripple_factor_no_filter

        elif "am_modulation" in exp_id:
            vc = p.get("Vc_V", 5.0)
            vm = p.get("Vm_V", 2.5)
            pc = p.get("Pc_W", 10.0)
            m = vm / vc
            pt = pc * (1.0 + (m ** 2) / 2.0)
            predictions["modulation_index_m"] = m
            predictions["total_power_Pt_W"] = pt
            predictions["sideband_power_Psb_W"] = pt - pc
            predictions["transmission_efficiency_percent"] = ((m ** 2) / (2.0 + m ** 2)) * 100.0

        elif "fm_modulation" in exp_id:
            delta_f = p.get("deviation_dF_kHz", 75.0)
            fm = p.get("modulating_f_kHz", 15.0)
            beta = delta_f / fm
            bw = 2 * (delta_f + fm)
            predictions["modulation_index_beta"] = beta
            predictions["bandwidth_Carson_kHz"] = bw

        elif "discrete_signal" in exp_id:
            f = p.get("f_Hz", 1000.0)
            fs = p.get("fs_Hz", 1500.0)
            nyquist = 2 * f
            aliased = fs < nyquist
            predictions["Nyquist_rate_Hz"] = nyquist
            predictions["aliasing_status"] = "Aliased (fs < 2f)" if aliased else "Normal (No Aliasing)"

        elif "reflex_klystron" in exp_id:
            vr = abs(p.get("repeller_V", -150.0))
            va = p.get("beam_V", 300.0)
            power = 15.0 * (math.sin(vr / 50.0) ** 2) * (va / 300.0)
            predictions["power_output_mW"] = max(power, 0.0)
            predictions["frequency_GHz"] = 9.4 + (vr - 150.0) * 0.002

        else:
            predictions["info"] = "Calculations complete."
            
    except Exception as e:
        predictions["error"] = f"Calculation failed: {e}"

    return {"experiment_id": req.experiment_id, "predictions": predictions}


# ── 2. Observation Verification ──
@router.post("/verify")
def verify_lab_observations(req: VerificationRequest):
    result = classify_faults(
        exp_id=req.experiment_id,
        measured=req.measured_values,
        expected=req.expected_values,
        symptom=req.symptom
    )
    return result


# ── 3. Breadboard CV Image Analysis & GNN Topology Checks ──
@router.post("/upload-image")
def upload_circuit_image(
    experiment_id: str = Form(...),
    file: UploadFile = File(...)
):
    filename = file.filename
    temp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", filename))
    
    try:
        with open(temp_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
        
    cv_res = analyze_breadboard_photo(exp_id=experiment_id, image_filename=filename)
    
    # ── PyTorch GNN Topology Inference ──
    adj_matrix = np.zeros((5, 5))
    feature_matrix = np.eye(5)
    
    faults = cv_res.get("faults", [])
    active_faults = [f for f in faults if f.get("type") not in [None, "None", ""]]
    
    if not active_faults:
        # Full closed loop topology: V1 -> R1 -> D1 -> GND -> V1
        adj_matrix[0, 1] = adj_matrix[1, 0] = 1
        adj_matrix[1, 2] = adj_matrix[2, 1] = 1
        adj_matrix[2, 3] = adj_matrix[3, 2] = 1
        adj_matrix[3, 0] = adj_matrix[0, 3] = 1
    else:
        # Partial / broken graph representation
        adj_matrix[0, 1] = adj_matrix[1, 0] = 1
        
    gnn_res = predict_circuit_anomaly(adj_matrix, feature_matrix, exp_id=experiment_id, faults=faults)
    cv_res["gnn_topology_check"] = gnn_res
    
    return cv_res


# ── 4. Waveform CRO screenshot analysis ──
@router.post("/upload-waveform")
def upload_waveform_screenshot(
    volts_div: float = Form(1.0),
    time_div_ms: float = Form(1.0),
    file: UploadFile = File(...)
):
    """
    Receives CRO waveform screen capture, processes it using OpenCV HSV mask-filtering,
    and returns signal dimensions and distortion anomalies.
    """
    filename = file.filename
    temp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", filename))
    
    try:
        with open(temp_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
        
    result = analyze_cro_waveform(filename, volts_div, time_div_ms)
    return result


# ── 5. CAD & LaTeX Exporter ──
@router.get("/schematics/{exp_id}")
def get_schematic_codes(exp_id: str):
    result = generate_and_save_cad_files(exp_id)
    return result
