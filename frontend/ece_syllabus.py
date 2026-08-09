"""
frontend/ece_syllabus.py
Static catalog mapping the official BIT Mesra ECE Laboratory Curriculum.
"""

ECE_SYLLABUS = {
    "Semester I": {
        "EC24102": {
            "name": "Basic Electronics Lab",
            "experiments": [
                {
                    "title": "Measurement of voltage, time period and frequency using CRO",
                    "id_match": "cro_measurements",
                    "aim": "Measure peak amplitude, frequency, and time period of AC waveforms using CRO division grids.",
                    "difficulty": "Easy",
                    "time": "30 mins",
                    "components": ["CRO", "Function Generator", "Probes"]
                },
                {
                    "title": "Measurement of frequency and phase difference using Lissajous patterns",
                    "id_match": "lissajous",
                    "aim": "Obtain Lissajous figures for phase alignment checking of two sinusoidal signals.",
                    "difficulty": "Easy",
                    "time": "30 mins",
                    "components": ["CRO", "Dual Function Generators", "Probes"]
                },
                {
                    "title": "PN Junction Diode characteristics",
                    "id_match": "pn_junction",
                    "aim": "Plot forward-biased cut-in voltage and reverse breakdown leakage currents.",
                    "difficulty": "Easy",
                    "time": "45 mins",
                    "components": ["Silicon Diode", "DC Variable Supply", "Multimeters", "Resistor"]
                },
                {
                    "title": "Zener Diode characteristics and Voltage Regulator",
                    "id_match": "zener",
                    "aim": "Model Zener breakdown voltage and evaluate source/load regulation efficiencies.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Zener Diode", "Series Resistor Rs", "Load Resistor RL", "DC Supply"]
                },
                {
                    "title": "BJT characteristics",
                    "id_match": "bjt",
                    "aim": "Plot input and output static characteristics of an NPN transistor in CE configuration.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["NPN Transistor (BC547)", "Dual DC Supplies", "Resistors", "Multimeters"]
                },
                {
                    "title": "Transistor Amplifier",
                    "id_match": "amplifier",
                    "aim": "Evaluate voltage gain, phase inversion, and bandwidth of a Single-Stage Common Emitter amplifier.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["BJT", "Biasing Resistors", "Coupling Capacitors", "Bypass Capacitor", "CRO"]
                },
                {
                    "title": "Inverting and Non-Inverting Op-Amp circuits",
                    "id_match": "opamp",
                    "aim": "Analyze closed-loop feedback gains and output voltage saturation limits of IC 741.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Op-Amp IC 741", "Dual DC Power Supply (+/-12V)", "Resistors", "Function Generator"]
                },
                {
                    "title": "Logic Gates realization and Boolean expression implementation",
                    "id_match": "logic",
                    "aim": "Verify truth tables of AND, OR, NOT, NAND, NOR, and XOR gates using digital ICs.",
                    "difficulty": "Easy",
                    "time": "30 mins",
                    "components": ["IC 7408, 7432, 7404, 7400, 7402, 7486", "Digital Trainer Board"]
                }
            ]
        }
    },
    "Semester III": {
        "EC24202": {
            "name": "Electronic Devices Lab",
            "experiments": [
                {
                    "title": "Energy bandgap determination of semiconductor material",
                    "id_match": "bandgap",
                    "aim": "Determine energy bandgap using reverse saturation current characteristics versus temperature.",
                    "difficulty": "Hard",
                    "time": "45 mins",
                    "components": ["Semiconductor Diode", "Heating Oven", "Thermometer", "Microammeter", "Power Supply"]
                },
                {
                    "title": "CE characteristics of NPN transistor",
                    "id_match": "ce_npn",
                    "aim": "Verify active, cutoff, and saturation regions of CE configuration static curves.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["NPN Transistor", "DC Power Supplies", "Resistors", "Ammeters", "Voltmeters"]
                },
                {
                    "title": "Enhancement-mode nMOSFET characteristics",
                    "id_match": "nmos_enh",
                    "aim": "Plot drain characteristics (ID vs VDS) and transfer curves (ID vs VGS) of Enhancement NMOS.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Enhancement NMOS IC", "Dual Power Supplies", "Voltmeters", "Ammeters"]
                },
                {
                    "title": "Depletion-mode nMOSFET characteristics",
                    "id_match": "nmos_dep",
                    "aim": "Plot drain and transfer characteristics of depletion n-channel MOSFETs.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Depletion NMOS IC", "Dual Power Supplies", "Voltmeters", "Ammeters"]
                },
                {
                    "title": "Schottky diode characteristics",
                    "id_match": "schottky",
                    "aim": "Evaluate forward turn-on potential and low barrier height characteristics of Schottky metal junctions.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Schottky Diode", "Supply", "Resistor", "Ammeters"]
                },
                {
                    "title": "Solar cell characteristics",
                    "id_match": "solar",
                    "aim": "Plot light I-V curves of a silicon solar cell to evaluate open-circuit voltage, short-circuit current, and fill factor.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Solar Panel Module", "Variable Light Source", "Decade Resistance Box", "Voltmeter", "Ammeter"]
                },
                {
                    "title": "PN Junction simulation using TCAD",
                    "id_match": "tcad_pn",
                    "aim": "Model electrostatic potential, electric field, and depletion width variations in Silvaco TCAD.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["TCAD Simulation Workstation"]
                },
                {
                    "title": "Enhancement nMOSFET simulation using TCAD",
                    "id_match": "tcad_nmos",
                    "aim": "Model transfer curves, threshold voltage, and subthreshold characteristics in sub-micron TCAD structures.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["TCAD Simulation Workstation"]
                },
                {
                    "title": "Enhancement pMOSFET simulation using TCAD",
                    "id_match": "tcad_pmos",
                    "aim": "Model transfer characteristics and hole mobility constraints in sub-micron PMOS devices.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["TCAD Simulation Workstation"]
                },
                {
                    "title": "CMOS Inverter simulation",
                    "id_match": "tcad_cmos",
                    "aim": "Model static voltage transfer characteristics (VTC), crossover voltage, and noise margins in TCAD.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["TCAD Simulation Workstation"]
                },
                {
                    "title": "nMOSFET study using Genius Simulator",
                    "id_match": "genius_nmos",
                    "aim": "Extract threshold voltage, drain conductance, and transconductance under Genius simulation engine.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Genius Semiconductor Simulator Tool"]
                },
                {
                    "title": "Double-Gate nMOSFET study using Genius Simulator",
                    "id_match": "genius_double",
                    "aim": "Compare short-channel effects, subthreshold swing, and DIBL benefits of double-gate structures vs bulk MOSFETs.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Genius Semiconductor Simulator Tool"]
                }
            ]
        },
        "EC24204": {
            "name": "Digital System Design Lab",
            "experiments": [
                {
                    "title": "Half Adder and Full Adder",
                    "id_match": "adder",
                    "aim": "Realize adder logic using basic gates and universal NAND/NOR configurations.",
                    "difficulty": "Easy",
                    "time": "30 mins",
                    "components": ["IC 7400, 7408, 7432, 7486", "Digital Trainer Kit"]
                },
                {
                    "title": "Seven Segment Display using IC7447",
                    "aim": "Interface BCD input to 7-segment display via BCD-to-seven-segment decoder driver.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["IC 7447 Decoder", "Common Anode 7-Segment Display", "Resistor Pack"]
                },
                {
                    "title": "Priority Encoder (74148) and Decoder (74138)",
                    "aim": "Verify priority encoding logic and 3-to-8 line demultiplexing operations.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["IC 74148 Priority Encoder", "IC 74138 Decoder", "Digital Trainer Kit"]
                },
                {
                    "title": "CMOS NAND and NOR gates using CD4007",
                    "aim": "Understand CMOS inverter and gate switching characteristics using transistor arrays.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["CD4007 Transistor Array", "Power Supply", "CRO"]
                },
                {
                    "title": "Multiplexer based combinational circuits",
                    "aim": "Implement Boolean functions and parity generators using multiplexer multiplexing logic.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["IC 74150 16-to-1 MUX or IC 74151 8-to-1 MUX", "Digital Board"]
                },
                {
                    "title": "Flip-Flop implementation",
                    "aim": "Build and verify truth tables of SR, JK, D, and T flip-flops.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["IC 7400, 7410, 7474, 7476", "Clock Generator"]
                },
                {
                    "title": "Counter implementation",
                    "aim": "Design synchronous and asynchronous modulo counters using JK flip-flop ICs.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["IC 7476 JK Flip-Flops", "IC 7400 NAND", "Clock Pulse Generator"]
                },
                {
                    "title": "Shift Register implementation",
                    "aim": "Verify SISO, SIPO, PISO, PIPO shift configurations using digital flip-flops.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["IC 7495 Universal Shift Register", "Clock Generator"]
                },
                {
                    "title": "Memory and timing circuits",
                    "aim": "Understand RAM structures and configure 555 timers as astable multivibrators.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["NE555 Timer IC", "Resistors", "Capacitors", "CRO"]
                },
                {
                    "title": "HDL based digital design using Xilinx",
                    "aim": "Write Verilog models for combinational circuits and multiplexers using Xilinx ISE/Vivado.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Xilinx ISE/Vivado FPGA Software Suite"]
                }
            ]
        }
    },
    "Semester IV": {
        "EC24252": {
            "name": "Analog Circuits Lab",
            "experiments": [
                {
                    "title": "Low-pass RC circuit design and frequency response",
                    "id_match": "rc_filters",
                    "aim": "Measure cutoff frequency and plot gain attenuation response using Plotly twin models.",
                    "difficulty": "Easy",
                    "time": "45 mins",
                    "components": ["Resistor", "Capacitor", "Function Generator", "CRO"]
                },
                {
                    "title": "High-pass RC circuit design and frequency response",
                    "id_match": "rc_filters",
                    "aim": "Measure high-pass response parameters and check phase shift responses.",
                    "difficulty": "Easy",
                    "time": "45 mins",
                    "components": ["Resistor", "Capacitor", "Function Generator", "CRO"]
                },
                {
                    "title": "Single-stage amplifier frequency response",
                    "id_match": "transistor_amplifier",
                    "aim": "Plot gain vs frequency for common emitter configurations to calculate bandwidth.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["BJT", "Biasing Resistors", "Capacitors", "CRO", "Signal Generator"]
                },
                {
                    "title": "Darlington Pair amplifier",
                    "aim": "Measure current gain and high input impedance characteristics of a Darlington BJT configuration.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Dual BJTs", "Biasing Resistors", "Capacitors", "Voltmeters", "CRO"]
                },
                {
                    "title": "Feedback amplifier",
                    "aim": "Analyze voltage-series negative feedback effects on voltage gain, bandwidth, and distortions.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Feedback Amplifier Board", "CRO", "Generator"]
                },
                {
                    "title": "Differential amplifier",
                    "aim": "Measure common-mode rejection ratio (CMRR) and differential gain parameters.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Matched Transistor Pair", "Constant Current Source", "CRO", "Supplies"]
                },
                {
                    "title": "RC Phase Shift Oscillator",
                    "id_match": "phase_shift",
                    "aim": "Verify Barkhausen loop gains using feedback RC shift grids to sustain sinusoids.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Op-Amp IC 741 or BJT", "RC Feedback Network", "Dual Power Supply", "CRO"]
                },
                {
                    "title": "Wien Bridge Oscillator",
                    "id_match": "wien_bridge",
                    "aim": "Obtain sine oscillations and evaluate output frequency vs bridge elements.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Op-Amp IC 741", "Wien Bridge Feedbacks", "CRO", "Dual Supply"]
                },
                {
                    "title": "Active Band-Pass Filter",
                    "aim": "Verify gain characteristics of Op-Amp active band-pass filters and plot selectivity.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Op-Amp IC 741", "RC Filter Networks", "CRO"]
                },
                {
                    "title": "Active Band-Stop Filter",
                    "aim": "Plot frequency response and notch parameters of an active band-elimination filter.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Op-Amp IC 741", "Twin-T Notch Network", "CRO"]
                },
                {
                    "title": "DAC design",
                    "aim": "Implement and verify R-2R ladder networks to convert digital inputs to analog steps.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Resistor Array", "Switches", "Op-Amp IC 741 Buffer", "Multimeter"]
                },
                {
                    "title": "ADC design",
                    "aim": "Understand successive approximation or flash converter loops using comparators.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Comparator ICs", "DAC Resistor Ladders", "Priority Encoder IC"]
                }
            ]
        },
        "EC24258": {
            "name": "VLSI Design Lab",
            "experiments": [
                {
                    "title": "Digital circuit design using Verilog/VHDL",
                    "aim": "Model combinational modules (adders, decoders) using dataflow and behavioral descriptions.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Xilinx ISE/Vivado Software"]
                },
                {
                    "title": "FPGA implementation",
                    "aim": "Compile, synthesize, and flash Verilog descriptions onto FPGA hardware boards.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["FPGA Development Board (Xilinx Artix-7/Spartan)"]
                },
                {
                    "title": "FSM implementation using Xilinx",
                    "aim": "Model Mealy/Moore finite state machine controllers in Verilog.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Xilinx ISE/Vivado Software"]
                },
                {
                    "title": "MOSFET-level Full Adder design",
                    "aim": "Model CMOS transistor level full adders and verify transient timing in SPICE.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SPICE Circuit Simulator (LTspice/HSPICE)"]
                },
                {
                    "title": "4-input NAND gate layout",
                    "aim": "Design physical CMOS layout cells including DRC and LVS checks.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["VLSI Layout Design Editor (Microwind/DSCH/Magic)"]
                },
                {
                    "title": "4-input Domino AND gate layout",
                    "aim": "Design dynamic domino logic gates with precharge and evaluate nodes.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["VLSI Layout Design Editor"]
                },
                {
                    "title": "Short-channel effect study",
                    "aim": "Simulate threshold voltage roll-off, DIBL, and hot-carrier degradation trends.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SPICE Circuit Simulator / TCAD"]
                },
                {
                    "title": "Static CMOS and pseudo-NMOS NAND gate",
                    "aim": "Compare propagation delays, noise margins, and static dissipation rates.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SPICE Circuit Simulator"]
                },
                {
                    "title": "XOR gate design",
                    "aim": "Implement XOR gates using transmission gates to minimize transistor counts.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["SPICE Circuit Simulator"]
                },
                {
                    "title": "Bidirectional PAD design",
                    "aim": "Model tri-state buffer PADs for bidirectional input/output configurations.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SPICE Circuit Simulator"]
                },
                {
                    "title": "SR Flip-Flop and D Flip-Flop design",
                    "aim": "Model logic states and setup/hold times of flip-flop CMOS circuits in SPICE.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SPICE Circuit Simulator"]
                },
                {
                    "title": "6T SRAM Cell design",
                    "aim": "Plot write and read static noise margins (SNM) using butterfly curves.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SPICE Circuit Simulator"]
                },
                {
                    "title": "Op-Amp based square-wave generator",
                    "aim": "Design astable multivibrator feedback circuits using operational amplifiers.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Op-Amp IC 741", "Resistors", "Capacitor", "CRO"]
                },
                {
                    "title": "Common Source MOS amplifier",
                    "aim": "Plot frequency gains and output swing limits of NMOS active-load CS stages.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SPICE Circuit Simulator"]
                },
                {
                    "title": "Differential amplifier using Cadence Virtuoso",
                    "aim": "Design layout, run DRC/LVS, and extract parasitics of a CMOS differential pair in Virtuoso.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Cadence Virtuoso Design Platform"]
                }
            ]
        }
    },
    "Semester V": {
        "EC24304": {
            "name": "Communication System Lab",
            "experiments": [
                {
                    "title": "AM Modulation and Demodulation",
                    "id_match": "am_modulation",
                    "aim": "Plot amplitude modulation waveforms and measure modulation index variations.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["AM Modulation Trainer Kit", "CRO", "Signal Generator"]
                },
                {
                    "title": "DSB-SC Modulation and Demodulation",
                    "aim": "Generate double sideband suppressed carrier signals using balanced modulators.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["DSB-SC Modulation Trainer Kit", "CRO"]
                },
                {
                    "title": "SSB Modulation",
                    "aim": "Generate single sideband signals using phase shift or filtering methods.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["SSB Generation Trainer Kit", "CRO"]
                },
                {
                    "title": "FM Modulation and Demodulation",
                    "id_match": "fm_modulation",
                    "aim": "Measure FM frequency deviations and plot demodulated outputs vs VCO sensitivity parameters.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["FM Modulation Trainer Kit", "CRO", "Generator"]
                },
                {
                    "title": "PAM Generation",
                    "aim": "Verify pulse amplitude modulation sampling and reconstruction filters.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["PAM Trainer Kit", "CRO"]
                },
                {
                    "title": "PWM Generation",
                    "aim": "Verify pulse width modulation outputs using mono-stable multivibrators.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["PWM Trainer Kit", "CRO"]
                },
                {
                    "title": "PPM Generation",
                    "aim": "Verify pulse position modulation outputs triggered from PWM falling edges.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["PPM Trainer Kit", "CRO"]
                },
                {
                    "title": "PCM Generation",
                    "aim": "Verify digital quantization, coding, sampling, and reconstruction filters.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["PCM Modulation/Demodulation Trainer Kit", "CRO"]
                },
                {
                    "title": "Delta Modulation",
                    "aim": "Trace slope overload distortion and granular noise limitations.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Delta Modulation Kit", "CRO"]
                },
                {
                    "title": "ASK Generation",
                    "aim": "Perform amplitude shift keying modulation and coherent detection.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["ASK Trainer Kit", "CRO"]
                },
                {
                    "title": "FSK Generation",
                    "aim": "Perform frequency shift keying modulation and phase-locked loop (PLL) decoding.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["FSK Trainer Kit", "CRO"]
                },
                {
                    "title": "PSK Generation",
                    "aim": "Perform phase shift keying modulation and coherent carrier recovery decoding.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["PSK Trainer Kit", "CRO"]
                }
            ]
        },
        "EC24306": {
            "name": "Microprocessors Lab",
            "experiments": [
                {
                    "title": "Rearranging Bytes",
                    "id_match": "rearranging_bytes",
                    "aim": "Write an 8085/8086 assembly program to sort an array of bytes in ascending/descending order.",
                    "difficulty": "Easy",
                    "time": "45 mins",
                    "components": ["8085/8086 Microprocessor Trainer Kit / Emulator"]
                },
                {
                    "title": "Formation of Third Block",
                    "aim": "Transfer two separate memory blocks and merge them into a third target block.",
                    "difficulty": "Easy",
                    "time": "45 mins",
                    "components": ["8085/8086 Trainer Kit"]
                },
                {
                    "title": "Addition of two 20-digit Binary Numbers",
                    "aim": "Perform multi-byte binary additions tracking carry flags.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["8085/8086 Trainer Kit"]
                },
                {
                    "title": "Addition of two 20-digit BCD Numbers",
                    "aim": "Perform BCD additions using decimal adjust instructions (DAA).",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["8085/8086 Trainer Kit"]
                },
                {
                    "title": "Subtraction Programs",
                    "aim": "Perform multi-byte binary and decimal (BCD) subtractions.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["8085/8086 Trainer Kit"]
                },
                {
                    "title": "Sorting Programs",
                    "aim": "Implement Bubble/Selection sort algorithms in assembly.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["8085/8086 Trainer Kit"]
                },
                {
                    "title": "Searching Programs",
                    "aim": "Scan memory blocks to locate specific bytes and store their addresses.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["8085/8086 Trainer Kit"]
                },
                {
                    "title": "Code Conversion Programs",
                    "aim": "Convert binary parameters to BCD equivalents and ASCII inputs to binary registers.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["8085/8086 Trainer Kit"]
                },
                {
                    "title": "8255 Interfacing",
                    "aim": "Configure ports of 8255 PPI to generate traffic light or LED blinking patterns.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["8255 PPI Interface Board", "Microprocessor Kit"]
                },
                {
                    "title": "8253 Timer Interfacing",
                    "aim": "Configure 8253 timer registers to output square waves and act as event counters.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["8253 Timer Interface Board", "CRO"]
                },
                {
                    "title": "8251 USART Interfacing",
                    "aim": "Establish serial communications between trainer kit and PC terminal.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["8251 USART Interface Board", "RS232 Cable"]
                },
                {
                    "title": "Interrupt Applications",
                    "aim": "Trigger subroutines on hardware interrupt pins (TRAP, RST 7.5).",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["8085 Microprocessor Kit", "Push Buttons"]
                }
            ]
        }
    },
    "Semester VI": {
        "EC24352": {
            "name": "Digital Signal Processing Lab",
            "experiments": [
                {
                    "title": "Discrete Signal Generation",
                    "id_match": "discrete_signal",
                    "aim": "Write MATLAB/Python code to generate discrete impulses, steps, ramps, and sinusoidal waveforms.",
                    "difficulty": "Easy",
                    "time": "30 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "Linear Convolution",
                    "aim": "Compute linear convolution of two discrete sequences and verify results.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "Circular Convolution",
                    "aim": "Calculate circular convolution of two discrete sequences using matrix and DFT methods.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "Correlation",
                    "aim": "Compute auto-correlation and cross-correlation arrays of sequences.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "DFT Implementation",
                    "aim": "Implement discrete Fourier transform (DFT) formulas and verify properties.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "FFT Implementation",
                    "aim": "Implement decimation-in-time (DIT) or decimation-in-frequency (DIF) butterfly FFT algorithms.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "FIR Filter Design",
                    "aim": "Design low-pass FIR filter coefficients using Rectangular, Hamming, and Kaiser windowing.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "IIR Filter Design",
                    "aim": "Design IIR filters using bilinear transformation from analog Butterworth prototypes.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "Sampling Theorem Verification",
                    "aim": "Demonstrate the sampling theorem, aliasing effects, and reconstruction interpolation.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["MATLAB / Python Environment"]
                },
                {
                    "title": "Spectrum Analysis",
                    "aim": "Analyze frequency spectrums of noisy signals using FFT.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["MATLAB / Python Environment"]
                }
            ]
        },
        "EC24356": {
            "name": "Embedded Systems Lab",
            "experiments": [
                {
                    "title": "LED Interfacing",
                    "id_match": "led_interface",
                    "aim": "Interface LEDs with a microcontroller (8051/ARM) and write pin toggle loops.",
                    "difficulty": "Easy",
                    "time": "30 mins",
                    "components": ["Microcontroller Board", "LEDs", "Keil IDE / STM32Cube"]
                },
                {
                    "title": "Switch Interfacing",
                    "aim": "Verify switch inputs and debounce patterns using software delay filters.",
                    "difficulty": "Easy",
                    "time": "30 mins",
                    "components": ["Microcontroller Board", "Push Buttons", "Keil IDE"]
                },
                {
                    "title": "LCD Interfacing",
                    "aim": "Interface and write characters to a 16x2 alphanumeric LCD in 4-bit or 8-bit mode.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["16x2 LCD Module", "Microcontroller Board"]
                },
                {
                    "title": "ADC Interfacing",
                    "aim": "Interface and read potentiometer voltages using internal ADC converters.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Microcontroller Board", "Potentiometer", "Keil IDE"]
                },
                {
                    "title": "UART Communication",
                    "aim": "Implement serial receive/transmit routines to exchange strings with PC terminals.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Microcontroller Board", "USB-to-TTL Adapter", "Serial Monitor"]
                },
                {
                    "title": "SPI Communication",
                    "aim": "Establish master-slave data transfer between two microcontrollers or SPI devices.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Dual Microcontroller Boards", "Logic Analyzer"]
                },
                {
                    "title": "I²C Communication",
                    "aim": "Read/write data to external EEPROM (AT24C02) using I²C protocol pins.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Microcontroller Board", "I2C EEPROM Module"]
                },
                {
                    "title": "Sensor Interfacing",
                    "aim": "Interface temperature (LM35/DHT11) sensors and display readings on LCD.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Temperature Sensor", "LCD Module", "Microcontroller"]
                },
                {
                    "title": "Actuator Control",
                    "aim": "Control DC/Servo motor speeds using Pulse Width Modulation (PWM) duty cycles.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["DC/Servo Motor", "Motor Driver H-Bridge IC", "Microcontroller"]
                },
                {
                    "title": "FPGA-based Embedded Design",
                    "aim": "Synthesize a soft-processor block (like NIOS-II / MicroBlaze) on FPGA.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["FPGA Development Board", "Intel Quartus / Xilinx Vivado"]
                }
            ]
        }
    },
    "Semester VII": {
        "EC24402": {
            "name": "Microwave Lab",
            "experiments": [
                {
                    "title": "Reflex Klystron characteristics",
                    "id_match": "reflex_klystron",
                    "aim": "Plot output power and mode characteristics of Klystron tube.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Klystron Tube", "Klystron Power Supply", "Microwave Bench Components"]
                },
                {
                    "title": "Gunn Diode characteristics",
                    "aim": "Plot threshold current and negative resistance curves.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Gunn Diode", "Gunn Power Supply", "Microwave Bench Components"]
                },
                {
                    "title": "Waveguide attenuation measurement",
                    "aim": "Verify attenuation levels in microwave waveguide bends.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Microwave Waveguide Bench", "Variable Attenuator"]
                },
                {
                    "title": "VSWR measurement",
                    "aim": "Verify voltage standing wave ratio under different load mismatches.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Microwave Bench", "Slotted Line Section", "VSWR Meter"]
                },
                {
                    "title": "Microwave frequency & wavelength checks",
                    "aim": "Obtain guide wavelength in TE10 mode using slots.",
                    "difficulty": "Medium",
                    "time": "45 mins",
                    "components": ["Microwave Bench Setup", "Frequency Meter"]
                },
                {
                    "title": "Directional Coupler parameters",
                    "aim": "Measure coupling factor and directivity coefficients of directional couplers.",
                    "difficulty": "Hard",
                    "time": "60 mins",
                    "components": ["Directional Coupler Module", "Power Meter"]
                }
            ]
        }
    }
}
