from __future__ import annotations

from itertools import combinations
import math
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import rankdata
from statsmodels.stats.multitest import multipletests

def median_abs_deviation(values: Iterable[float]) -> float:
    x = np.asarray(list(values), dtype=float)
    if x.size == 0:
        return float("nan")
    return float(stats.median_abs_deviation(x, scale=1.0, nan_policy="omit"))

def iqr(values: Iterable[float]) -> float:
    x = np.asarray(list(values), dtype=float)
    if x.size == 0:
        return float("nan")
    q75, q25 = np.nanpercentile(x, [75, 25])
    return float(q75 - q25)

def zero_yield_ratio(values: Iterable[float]) -> float:
    x = np.asarray(list(values), dtype=float)
    if x.size == 0:
        return float("nan")
    return float(np.mean(x == 0))

def cv(values: Iterable[float]) -> float:
    x = np.asarray(list(values), dtype=float)
    if x.size == 0:
        return float("nan")
    mean = np.nanmean(x)
    if mean == 0 or np.isnan(mean):
        return float("nan")
    return float(np.nanstd(x, ddof=1) / mean)

def bootstrap_ci(
    values: Iterable[float],
    n_boot: int = 4000,
    random_state: int = 20260619,
    stat_func=np.median,
    alpha: float = 0.05,
) -> tuple[float, float]:
    x = np.asarray(list(values), dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return float("nan"), float("nan")
    if np.allclose(x, x[0]):
        return float(x[0]), float(x[0])

    rng = np.random.default_rng(random_state)
    boots = np.empty(n_boot, dtype=float)
    n = x.size
    for i in range(n_boot):
        sample = rng.choice(x, size=n, replace=True)
        boots[i] = float(stat_func(sample))
    lo = float(np.nanpercentile(boots, 100 * (alpha / 2)))
    hi = float(np.nanpercentile(boots, 100 * (1 - alpha / 2)))
    return lo, hi

def threshold_by_detection_rate(df: pd.DataFrame, group_cols: list[str], threshold: float = 0.0) -> pd.DataFrame:
    rows = []
    for keys, group in df.groupby(group_cols, observed=True, sort=False):
        group = group.sort_values("SPL_dB")
        detected = group[group["detection_rate"] > threshold]
        if isinstance(keys, tuple):
            rec = {col: val for col, val in zip(group_cols, keys)}
        else:
            rec = {group_cols[0]: keys}
        if detected.empty:
            rec.update({
                "threshold_SPL_dB": np.nan,
                "detection_rate_at_threshold": np.nan,
                "first_detected": False,
            })
        else:
            first = detected.iloc[0]
            rec.update({
                "threshold_SPL_dB": int(first["SPL_dB"]),
                "detection_rate_at_threshold": float(first["detection_rate"]),
                "first_detected": True,
            })
        rows.append(rec)
    return pd.DataFrame(rows)

def rank_biserial_from_u(u: float, n1: int, n2: int) -> float:
    if n1 == 0 or n2 == 0:
        return float("nan")
    return float(1 - (2 * u) / (n1 * n2))

def common_language_effect_size(u: float, n1: int, n2: int) -> float:
    if n1 == 0 or n2 == 0:
        return float("nan")
    return float(u / (n1 * n2))

def epsilon_squared_kw(h: float, k: int, n: int) -> float:
    if n <= k or np.isnan(h):
        return float("nan")
    return float(max(0.0, (h - k + 1) / (n - k)))

def pairwise_dunn_fallback(df: pd.DataFrame, group_col: str, value_col: str, p_adjust: str = "holm") -> pd.DataFrame:
    data = df[[group_col, value_col]].dropna().copy()
    groups = list(pd.Categorical(data[group_col]).categories if pd.api.types.is_categorical_dtype(data[group_col]) else sorted(data[group_col].unique()))
    if len(groups) < 2:
        return pd.DataFrame(columns=["group1", "group2", "z_statistic", "p_raw", "p_adjusted"])

    data["rank"] = rankdata(data[value_col].to_numpy(dtype=float))
    N = len(data)
    tie_counts = pd.Series(data[value_col]).value_counts()
    tie_term = float(((tie_counts ** 3 - tie_counts).sum()) / (N**3 - N)) if N > 1 else 0.0
    tie_correction = max(1e-12, 1.0 - tie_term)

    mean_ranks = data.groupby(group_col, observed=True)["rank"].mean()
    sizes = data.groupby(group_col, observed=True)[value_col].size()

    rows = []
    pvals = []
    pair_labels = []
    for g1, g2 in combinations(groups, 2):
        n1, n2 = int(sizes[g1]), int(sizes[g2])
        if n1 == 0 or n2 == 0:
            z = np.nan
            p = np.nan
        else:
            diff = float(mean_ranks[g1] - mean_ranks[g2])
            se = math.sqrt((N * (N + 1) / 12.0) * tie_correction * (1 / n1 + 1 / n2))
            z = diff / se if se != 0 else np.nan
            p = 2 * stats.norm.sf(abs(z)) if np.isfinite(z) else np.nan
        rows.append({
            "group1": g1,
            "group2": g2,
            "z_statistic": float(z) if np.isfinite(z) else np.nan,
            "p_raw": float(p) if np.isfinite(p) else np.nan,
        })
        pvals.append(p if np.isfinite(p) else 1.0)
        pair_labels.append((g1, g2))

    _, p_adj, _, _ = multipletests(pvals, method=p_adjust)
    for row, adj in zip(rows, p_adj):
        row["p_adjusted"] = float(adj)
    return pd.DataFrame(rows)
