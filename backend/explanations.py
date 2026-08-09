"""
backend/explanations.py
Static database of known ECE circuit faults, causes, and recommendations.
Used as a fast, zero-cost fallback for diagnosis and explanation.
"""

FAULTS_DB = {
    "cro_measurements": {
        "unstable_scrolling": {
            "title": "Waveform is unstable or scrolling on screen",
            "causes": ["Trigger level set outside the waveform voltage bounds", "Trigger source set to an unused channel (e.g. CH2 when signal is on CH1)"],
            "fix": "Rotate the TRIGGER LEVEL knob until the waveform stabilizes. Check that the TRIGGER SOURCE matches the input channel (CH1 or CH2) you are using."
        },
        "waveform_too_small": {
            "title": "Waveform is too small to measure",
            "causes": ["VOLTS/DIV knob set to an excessively high scale"],
            "fix": "Rotate the VOLTS/DIV knob counter-clockwise (reduce scale) until the waveform fills 4 to 6 vertical divisions."
        },
        "flat_line": {
            "title": "Only a flat line is displayed on screen",
            "causes": ["Function generator is not powered ON", "CRO channel selector is set to a channel with no probe", "Probe ground clip is floating"],
            "fix": "Power on the signal generator, verify the probe connections, and make sure the active channel on the CRO matches the probe input pin."
        }
    },
    "pn_junction": {
        "reversed_diode": {
            "title": "No current flows in forward bias",
            "causes": ["Diode is reversed ( silver band cathode connected to positive supply )", "Voltmeter is connected in series instead of parallel"],
            "fix": "Flip the diode on the breadboard so the silver band (cathode) connects to ground or negative node. Ensure voltmeter is in parallel."
        },
        "diode_overheating": {
            "title": "Diode gets hot and current spikes suddenly",
            "causes": ["Current limiting resistor is missing or short-circuited"],
            "fix": "Immediately turn off the power supply. Connect a 1kΩ resistor in series with the diode to protect it from thermal runaway."
        }
    },
    "zener": {
        "no_breakdown": {
            "title": "Output voltage keeps rising, no clamping/regulation",
            "causes": ["Zener diode is forward biased instead of reverse biased", "Input supply voltage Vin is less than the Zener voltage Vz"],
            "fix": "Verify Zener polarity: the cathode (black/silver stripe) must connect to the positive voltage rail. Ensure Vin is set higher than Vz."
        },
        "voltage_droop": {
            "title": "Output voltage drops significantly under load",
            "causes": ["Load resistor RL is too small, drawing too much current", "Series resistor Rs is too large, starving the Zener of current"],
            "fix": "Increase load resistor RL (e.g. above 1kΩ) or reduce Rs (e.g. to 470Ω) to ensure the Zener current remains above Iz_min."
        }
    },
    "bjt_characteristics": {
        "stuck_cutoff": {
            "title": "Collector current IC stays near zero regardless of IB",
            "causes": ["Wrong BJT pin connections", "Base-emitter voltage VBE is below 0.6V", "Collector supply VCC is off"],
            "fix": "Confirm BJT pinout: for BC547, flat side facing you pins down, left-to-right order is Collector-Base-Emitter. Ensure VBE > 0.6V."
        }
    },
    "transistor_amplifier": {
        "clipping_distortion": {
            "title": "Output waveform is severely clipped on one side",
            "causes": ["Q-point is not centered (improper bias resistor values)", "AC input voltage is too large, causing saturation or cutoff"],
            "fix": "Reduce the input generator voltage (try 10-20 mV). Check R1 and R2 values to ensure VCE is around half of VCC (6V for a 12V supply)."
        },
        "no_gain": {
            "title": "Output voltage equals input (gain is approximately 1)",
            "causes": ["Emitter bypass capacitor CE is missing or disconnected", "Coupling capacitors connected in reverse polarity"],
            "fix": "Verify that a 100μF bypass capacitor is connected in parallel with the emitter resistor RE. Check electrolytic capacitor polarities (+ to higher DC)."
        }
    },
    "opamp": {
        "output_clipping": {
            "title": "Output is a square wave or clipping at rails",
            "causes": ["Input signal amplitude is too large for the configured closed-loop gain", "Dual power supplies ±12V are not connected to pins 7 and 4"],
            "fix": "Reduce the input signal amplitude (e.g., to 0.5V). Verify that pin 7 has +12V and pin 4 has -12V relative to system ground."
        },
        "zero_output": {
            "title": "Output remains stuck at zero volts",
            "causes": ["Feedback resistor Rf is missing or open-circuited", "Op-amp supply rails are not turned on"],
            "fix": "Verify that the feedback resistor connects pin 6 (output) to pin 2 (inverting input). Check supply connections."
        }
    },
    "logic_gates": {
        "always_high": {
            "title": "All gate outputs are stuck HIGH",
            "causes": ["Floating TTL inputs (unconnected inputs float to HIGH)", "VCC or GND pins not connected to the breadboard rails"],
            "fix": "Connect unused gate inputs to a defined logic level (VCC for logic 1, GND for logic 0). Check pin 14 (VCC) and pin 7 (GND) connections."
        },
        "ic_hot": {
            "title": "Logic IC is extremely hot to the touch",
            "causes": ["Power supply reversed (VCC to pin 7, GND to pin 14)", "Output pins shorted together or to ground"],
            "fix": "Turn off power immediately. Orient IC notch/dot to the left (pin 1 bottom-left). Verify VCC connects to pin 14 and GND to pin 7."
        }
    },
    "rectifiers": {
        "half_wave_fwr": {
            "title": "Full-wave rectifier output looks like a half-wave",
            "causes": ["One of the two diodes is open-circuited or connected in reverse", "Center-tap ground wire is disconnected"],
            "fix": "Ensure both diodes' cathode bands are connected to the same side of the load resistor. Verify center-tap is grounded."
        },
        "capacitor_burst": {
            "title": "Filter capacitor got extremely hot or burst",
            "causes": ["Filter electrolytic capacitor connected in reverse polarity"],
            "fix": "Always connect the positive lead of the electrolytic capacitor to the rectifier output, and the negative lead (marked with minus stripe) to ground."
        }
    },
    "rc_filters": {
        "incorrect_cutoff": {
            "title": "Cutoff frequency is far from theoretical 1.6kHz",
            "causes": ["Read wrong resistor or capacitor code (e.g. 0.1uF instead of 0.01uF)"],
            "fix": "Check capacitor marking: '103' represents 0.01μF. Confirm resistor is 10kΩ (brown-black-orange)."
        }
    },
    "rc_phase_shift": {
        "no_oscillation": {
            "title": "Oscillator does not start (flat line)",
            "causes": ["Feedback resistor Rf potentiometer is set below 290kΩ (loop gain < 29)", "The three RC stages are wired incorrectly"],
            "fix": "Slowly adjust the Rf potentiometer to increase its resistance until oscillation starts. Double-check the 3-stage RC cascade."
        }
    },
    "wien_bridge": {
        "stuck_saturation": {
            "title": "Output is a heavily clipped/saturated wave",
            "causes": ["Rf potentiometer set too high (gain much greater than 3)"],
            "fix": "Adjust the Rf potentiometer downwards to decrease the gain until the waveform becomes a clean, unclipped sinusoid."
        }
    },
    "am_modulation": {
        "overmodulation": {
            "title": "AM envelope is pinched or distorted",
            "causes": ["Modulating message amplitude is too high (m > 1)"],
            "fix": "Reduce the amplitude of the message signal from the function generator until the envelope valleys (Vmin) are above 0V."
        },
        "diagonal_clipping": {
            "title": "Recovered message is jagged/sawtooth instead of sine",
            "causes": ["RC time constant of envelope detector is too large (does not follow carrier fall)"],
            "fix": "Decrease the resistor or capacitor value of the envelope filter so it discharges faster."
        }
    },
    "fm_modulation": {
        "pll_no_lock": {
            "title": "PLL demodulator output is stuck at a DC offset or noise",
            "causes": ["VCO free-running frequency of the PLL does not match carrier frequency", "FM input amplitude is too small"],
            "fix": "Adjust the PLL free-running frequency pot (Rt/Ct) to center around 50kHz. Increase amplitude of FM input."
        }
    }
}


def has_explanation(circuit: str, fault: str) -> bool:
    """Check if the static database contains the given circuit-fault pair."""
    # Handle variations in circuit name matching
    c_clean = circuit.lower()
    for key in FAULTS_DB:
        if key in c_clean or c_clean in key:
            if fault in FAULTS_DB[key]:
                return True
    return False


def get_explanation(circuit: str, fault: str) -> str:
    """Retrieve explanation formatting as text."""
    c_clean = circuit.lower()
    for key in FAULTS_DB:
        if key in c_clean or c_clean in key:
            if fault in FAULTS_DB[key]:
                f_data = FAULTS_DB[key][fault]
                ans = f"### ⚠️ **{f_data['title']}**\n\n"
                ans += "**Likely Causes:**\n"
                for cause in f_data["causes"]:
                    ans += f"- {cause}\n"
                ans += "\n**Recommended Fix:**\n"
                ans += f"{f_data['fix']}\n"
                return ans
    return "No static explanation found."
