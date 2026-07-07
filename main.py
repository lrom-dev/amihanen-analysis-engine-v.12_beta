from __future__ import annotations

import json

from data.master_dataset import DATA
from utils.validation import load_dataframe, add_detection_flag
from utils.config import OUTPUT_DIR, FIGURES_DIR, RESULTS_DIR, TABLES_DIR
from utils.export_helpers import save_json

from analysis.objective1 import analyze as analyze_objective1
from analysis.objective2 import analyze as analyze_objective2
from analysis.objective3 import analyze as analyze_objective3

def _stringify(obj):
    if isinstance(obj, dict):
        return {str(k): _stringify(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stringify(v) for v in obj]
    return str(obj) if hasattr(obj, "as_posix") else obj

def main():
    df = load_dataframe(DATA)
    df = add_detection_flag(df)

    for p in [OUTPUT_DIR, FIGURES_DIR, RESULTS_DIR, TABLES_DIR]:
        p.mkdir(parents=True, exist_ok=True)

    all_results = {
        "objective1": analyze_objective1(df, TABLES_DIR, FIGURES_DIR),
        "objective2": analyze_objective2(df, TABLES_DIR, FIGURES_DIR),
        "objective3": analyze_objective3(df, TABLES_DIR, FIGURES_DIR),
    }

    manifest_path = save_json(all_results, RESULTS_DIR, "manifest")
    print(json.dumps(_stringify(all_results), indent=2))
    print(f"Manifest saved to: {manifest_path}")

if __name__ == "__main__":
    main()