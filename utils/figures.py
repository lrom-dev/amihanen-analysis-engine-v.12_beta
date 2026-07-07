from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

def plot_detection_rate(df: pd.DataFrame, out_path: Path) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    for (setup, env), sub in df.groupby(["Setup", "Environment"], observed=True):
        sub = sub.sort_values("SPL_dB")
        ax.plot(sub["SPL_dB"], sub["detection_rate"], marker="o", label=f"{setup} | {env}")
    ax.set_xlabel("Sound Pressure Level (dB)")
    ax.set_ylabel("Detection Rate")
    ax.set_title("Detection Rate Across SPL")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)

def plot_response_curves(summary_df: pd.DataFrame, variable: str, out_path: Path) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    for (setup, env), sub in summary_df.groupby(["Setup", "Environment"], observed=True):
        sub = sub.sort_values("SPL_dB")
        ax.plot(sub["SPL_dB"], sub["median"], marker="o", label=f"{setup} | {env}")
    ax.set_xlabel("Sound Pressure Level (dB)")
    ax.set_ylabel(variable)
    ax.set_title(f"Response Curve: {variable}")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)

def plot_heatmap(summary_df: pd.DataFrame, variable: str, setup_label: str, out_path: Path) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    pivot = summary_df.pivot_table(index="Environment", columns="SPL_dB", values="median", aggfunc="mean")
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([str(c) for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([str(i) for i in pivot.index])
    ax.set_xlabel("Sound Pressure Level (dB)")
    ax.set_ylabel("Environment")
    ax.set_title(f"Heatmap: {variable} | {setup_label}")
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)
