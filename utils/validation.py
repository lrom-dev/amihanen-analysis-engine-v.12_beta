from __future__ import annotations

from typing import Iterable
import pandas as pd

from utils.config import SETUP_ORDER, ENVIRONMENT_ORDER, SPL_ORDER, TRIAL_ORDER, RESPONSE_VARS

REQUIRED_COLUMNS = ["Setup", "Environment", "SPL_dB", "Trial", *RESPONSE_VARS]

def load_dataframe(data: Iterable[dict]) -> pd.DataFrame:
    df = pd.DataFrame(list(data)).copy()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    df["Setup"] = pd.Categorical(df["Setup"], categories=SETUP_ORDER, ordered=True)
    df["Environment"] = pd.Categorical(df["Environment"], categories=ENVIRONMENT_ORDER, ordered=True)
    df["SPL_dB"] = pd.to_numeric(df["SPL_dB"], errors="raise").astype(int)
    df["Trial"] = pd.Categorical(df["Trial"], categories=TRIAL_ORDER, ordered=True)

    for col in RESPONSE_VARS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["Setup", "Environment", "SPL_dB", "Trial"]).reset_index(drop=True)
    return df

def add_detection_flag(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Detected"] = out["DC_Power"] > 0
    return out
