from __future__ import annotations

from pathlib import Path
import pandas as pd
from scipy import stats

from utils.config import RESPONSE_VARS, ALPHA
from utils.export_helpers import save_table, print_apa_table
from utils.figures import plot_detection_rate
from utils.stats_helpers import threshold_by_detection_rate

def analyze(df: pd.DataFrame, out_tables: Path, out_figures: Path) -> dict:
    results = {}

    detection_summary = (
        df.groupby(["Setup", "Environment", "SPL_dB"], observed=True)
        .agg(
            n=("DC_Power", "size"),
            detection_rate=("DC_Power", lambda s: float((s > 0).mean())),
            voltage_detection_rate=("DC_Voltage", lambda s: float((s > 0).mean())),
            current_detection_rate=("DC_Current", lambda s: float((s > 0).mean())),
            power_detection_rate=("DC_Power", lambda s: float((s > 0).mean())),
        )
        .reset_index()
        .sort_values(["Setup", "Environment", "SPL_dB"])
    )

    print_apa_table(detection_summary, 1, "Detection Rates Across Sound Pressure Levels")
    results["detection_summary"] = save_table(
        detection_summary,
        out_tables,
        "objective1_detection_summary",
        title="Detection Rates Across Sound Pressure Levels",
        table_number=1,
    )

    threshold_summary = threshold_by_detection_rate(
        detection_summary[["Setup", "Environment", "SPL_dB", "power_detection_rate"]].rename(
            columns={"power_detection_rate": "detection_rate"}
        ),
        ["Setup", "Environment"],
        threshold=0.0,
    ).sort_values(["Setup", "Environment"])

    print_apa_table(threshold_summary, 2, "Minimum Sound Intensity Threshold by Setup and Environment")
    results["threshold_summary"] = save_table(
        threshold_summary,
        out_tables,
        "objective1_threshold_summary",
        title="Minimum Sound Intensity Threshold by Setup and Environment",
        table_number=2,
    )

    overall_detection = (
        df.groupby(["Setup", "SPL_dB"], observed=True)
        .agg(detection_rate=("DC_Power", lambda s: float((s > 0).mean())))
        .reset_index()
        .sort_values(["Setup", "SPL_dB"])
    )
    overall_detection["Environment"] = "All"
    overall_threshold = threshold_by_detection_rate(
        overall_detection[["Setup", "Environment", "SPL_dB", "detection_rate"]],
        ["Setup"],
        threshold=0.0,
    ).sort_values(["Setup"])

    print_apa_table(overall_threshold, 3, "Overall Threshold by Setup")
    results["overall_threshold"] = save_table(
        overall_threshold,
        out_tables,
        "objective1_overall_threshold",
        title="Overall Threshold by Setup",
        table_number=3,
    )

    standalone = df[df["Setup"] == "Standalone"].copy()
    spearman_rows = []
    for var in RESPONSE_VARS:
        rho, p = stats.spearmanr(standalone["SPL_dB"].astype(int), standalone[var], nan_policy="omit")
        spearman_rows.append(
            {
                "variable": var,
                "spearman_rho": float(rho) if pd.notna(rho) else float("nan"),
                "p_value": float(p) if pd.notna(p) else float("nan"),
                "n": int(standalone[var].notna().sum()),
                "alpha": ALPHA,
            }
        )
    spearman_df = pd.DataFrame(spearman_rows)
    spearman_apa = spearman_df.rename(columns={"spearman_rho": "rₛ", "p_value": "p"})
    print_apa_table(spearman_apa, 4, "Spearman Correlations in Standalone Group")
    results["spearman"] = save_table(
        spearman_df,
        out_tables,
        "objective1_spearman_standalone",
        title="Spearman Correlations in Standalone Group",
        table_number=4,
    )

    results["figure_detection_rate"] = plot_detection_rate(
        overall_detection,
        out_figures / "objective1_detection_rate.png",
    )
    return results
