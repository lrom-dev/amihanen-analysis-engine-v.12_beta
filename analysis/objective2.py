from __future__ import annotations

from pathlib import Path
import pandas as pd

from utils.config import RESPONSE_VARS, BOOTSTRAP_N, RANDOM_SEED
from utils.export_helpers import save_table, print_apa_table
from utils.stats_helpers import median_abs_deviation, iqr, zero_yield_ratio, cv, bootstrap_ci
from utils.figures import plot_response_curves, plot_heatmap

def _summarize_group(s: pd.Series) -> dict:
    vals = s.to_numpy(dtype=float)
    lo, hi = bootstrap_ci(vals, n_boot=BOOTSTRAP_N, random_state=RANDOM_SEED)
    ser = pd.Series(vals)
    return {
        "n": int(ser.shape[0]),
        "zero_yield_ratio": zero_yield_ratio(vals),
        "median": float(ser.median()),
        "mad": median_abs_deviation(vals),
        "iqr": iqr(vals),
        "min": float(ser.min()),
        "max": float(ser.max()),
        "ci_low": lo,
        "ci_high": hi,
        "cv": cv(vals),
    }

def analyze(df: pd.DataFrame, out_tables: Path, out_figures: Path) -> dict:
    results = {}
    summary_frames = []

    for var in RESPONSE_VARS:
        records = []
        grouped = df.groupby(["Setup", "Environment", "SPL_dB"], observed=True)[var]
        for (setup, env, spl), series in grouped:
            rec = {"Setup": setup, "Environment": env, "SPL_dB": spl, "variable": var}
            rec.update(_summarize_group(series))
            records.append(rec)
        summary_frames.append(pd.DataFrame.from_records(records))

    summary = pd.concat(summary_frames, ignore_index=True)
    summary = summary.sort_values(["variable", "Setup", "Environment", "SPL_dB"]).reset_index(drop=True)

    apa_summary = summary.rename(
        columns={
            "zero_yield_ratio": "Zero Yield Ratio",
            "median": "Mdn",
            "mad": "MAD",
            "iqr": "IQR",
            "ci_low": "95% CI LL",
            "ci_high": "95% CI UL",
            "cv": "CV",
        }
    )
    print_apa_table(apa_summary, 5, "Descriptive Statistics by Condition")
    results["descriptive_summary"] = save_table(
        summary,
        out_tables,
        "objective2_descriptive_summary",
        title="Descriptive Statistics by Condition",
        table_number=5,
    )

    overall_records = []

    for var in RESPONSE_VARS:

        stats_by_setup = {}

        for setup in df["Setup"].cat.categories:

            vals = df.loc[df["Setup"] == setup, var].to_numpy(dtype=float)

            ci_low, ci_high = bootstrap_ci(
                vals,
                n_boot=BOOTSTRAP_N,
                random_state=RANDOM_SEED
            )

            stats_by_setup[setup] = {
                "Median": float(pd.Series(vals).median()),
                "MAD": median_abs_deviation(vals),
                "Min": float(pd.Series(vals).min()),
                "Max": float(pd.Series(vals).max()),
                "95% CI LL": ci_low,
                "95% CI UL": ci_high,
            }

        for stat_name in [
            "Median",
            "MAD",
            "Min",
            "Max",
            "95% CI LL",
            "95% CI UL",
        ]:

            row = {
                "Variable": var,
                "Statistic": stat_name,
            }

            for setup in df["Setup"].cat.categories:
                row[str(setup)] = stats_by_setup[setup][stat_name]

            overall_records.append(row)

    overall_table = pd.DataFrame(overall_records)

    print_apa_table(
        overall_table,
        6,
        "Overall Descriptive Statistics by Harvester Type"
    )

    results["overall_descriptives"] = save_table(
        overall_table,
        out_tables,
        "objective2_overall_descriptives",
        title="Overall Descriptive Statistics by Harvester Type",
        table_number=6,
    )

    for var in RESPONSE_VARS:
        var_df = summary[summary["variable"] == var].copy()
        results[f"figure_response_curves_{var}"] = plot_response_curves(
            var_df,
            var,
            out_figures / f"objective2_response_curves_{var}.png",
        )
        for setup in df["Setup"].cat.categories:
            setup_df = var_df[var_df["Setup"] == setup]
            results[f"figure_heatmap_{var}_{setup}"] = plot_heatmap(
                setup_df,
                var,
                str(setup),
                out_figures / f"objective2_heatmap_{var}_{setup}.png",
            )

    return results
