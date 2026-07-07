from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "output"
TABLES_DIR = OUTPUT_DIR / "tables"
FIGURES_DIR = OUTPUT_DIR / "figures"
RESULTS_DIR = OUTPUT_DIR / "results"

ALPHA = 0.01
RANDOM_SEED = 20260619
BOOTSTRAP_N = 4000

RESPONSE_VARS = ["DC_Voltage", "DC_Current", "DC_Power"]

SETUP_ORDER = ["Standalone", "Integrated"]
ENVIRONMENT_ORDER = ["Ind.", "Traf.", "Comm."]
SPL_ORDER = [60, 70, 80, 90, 100]
TRIAL_ORDER = ["Round 1", "Round 2", "Round 3"]
