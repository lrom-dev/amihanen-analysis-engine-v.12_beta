from __future__ import annotations

DATA = []

def _add_rows(setup, environment, spl, voltages, currents, powers):
    for i, (v, c, p) in enumerate(zip(voltages, currents, powers), start=1):
        DATA.append(
            {
                "Setup": setup,
                "Environment": environment,
                "SPL_dB": spl,
                "Trial": f"Round {i}",
                "DC_Voltage": v,
                "DC_Current": c,
                "DC_Power": p,
            }
        )

# Standalone
_add_rows("Standalone", "Ind.", 60, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
_add_rows("Standalone", "Ind.", 70, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
_add_rows("Standalone", "Ind.", 80, [0.003, 0.001, 0.001], [0.00003, 0.00001, 0.00001], [9.00e-08, 1.00e-08, 1.00e-08])
_add_rows("Standalone", "Ind.", 90, [0.029, 0.047, 0.05], [0.00029, 0.00047, 0.0005], [8.41e-06, 2.209e-05, 2.50e-05])
_add_rows("Standalone", "Ind.", 100, [1.132, 1.099, 1.049], [0.01132, 0.01099, 0.01049], [0.01281424, 0.01207801, 0.01100401])

_add_rows("Standalone", "Traf.", 60, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
_add_rows("Standalone", "Traf.", 70, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
_add_rows("Standalone", "Traf.", 80, [0.001, 0.001, 0.001], [0.00001, 0.00001, 0.00001], [1.00e-08, 1.00e-08, 1.00e-08])
_add_rows("Standalone", "Traf.", 90, [0.002, 0.002, 0.002], [0.00002, 0.00002, 0.00002], [4.00e-08, 4.00e-08, 4.00e-08])
_add_rows("Standalone", "Traf.", 100, [0.082, 0.064, 0.064], [0.00082, 0.00064, 0.00064], [6.274e-05, 4.096e-05, 4.096e-05])

_add_rows("Standalone", "Comm.", 60, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
_add_rows("Standalone", "Comm.", 70, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
_add_rows("Standalone", "Comm.", 80, [0.001, 0.001, 0.002], [0.00001, 0.00001, 0.00002], [1.00e-08, 1.00e-08, 4.00e-08])
_add_rows("Standalone", "Comm.", 90, [0.002, 0.002, 0.003], [0.00002, 0.00002, 0.00003], [4.00e-08, 4.00e-08, 9.00e-08])
_add_rows("Standalone", "Comm.", 100, [0.203, 0.192, 0.192], [0.00203, 0.00192, 0.00192], [0.00041209, 0.00036864, 0.00036864])

# Integrated
for env in ["Ind.", "Traf.", "Comm."]:
    for spl in [60, 70, 80, 90, 100]:
        _add_rows("Integrated", env, spl, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

assert len(DATA) == 90, f"Expected 90 records, got {len(DATA)}"
