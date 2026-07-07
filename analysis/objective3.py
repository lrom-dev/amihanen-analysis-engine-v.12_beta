from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

from utils.config import RESPONSE_VARS, ALPHA
from utils.export_helpers import save_table, print_apa_table
from utils.stats_helpers import (
    rank_biserial_from_u,
    common_language_effect_size,
    epsilon_squared_kw,
    pairwise_dunn_fallback,
)

def _tweedie_family():
    return sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log())

def omnibus_factorial_table(df: pd.DataFrame, variable: str) -> pd.DataFrame:
    full_formula = f"{variable} ~ C(Environment) * C(SPL_dB) * C(Setup)"
    full = smf.glm(formula=full_formula, data=df, family=_tweedie_family()).fit()
    wald = full.wald_test_terms(skip_single=False, scalar=True).summary_frame()

    term_map = [
        ("Env.", "C(Environment)"),
        ("SPL", "C(SPL_dB)"),
        ("Setup", "C(Setup)"),
        ("Env. × SPL", "C(Environment):C(SPL_dB)"),
        ("Env. × Setup", "C(Environment):C(Setup)"),
        ("SPL × Setup", "C(SPL_dB):C(Setup)"),
        ("Env. × SPL × Setup", "C(Environment):C(SPL_dB):C(Setup)"),
    ]

    rows = []
    for label, term in term_map:
        if term not in wald.index:
            chi2 = np.nan
            p = np.nan
            dfc = np.nan
        else:
            chi2 = float(wald.loc[term, "chi2"])
            p = float(wald.loc[term, "P>chi2"])
            dfc = int(wald.loc[term, "df constraint"])
        eta2 = float(chi2 / (chi2 + full.df_resid)) if np.isfinite(chi2) and (chi2 + full.df_resid) != 0 else float("nan")
        rows.append({
            "Macro-effect": label,
            "η²": eta2,
            "χ²": chi2,
            "p": p,
            "df": dfc,
            "variable": variable,
        })
    return pd.DataFrame(rows)

def tweedie_family():
    return sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log())

def fit_tweedie_models(df: pd.DataFrame, variable: str):
    full_formula = f"{variable} ~ C(Environment) * C(SPL_dB)"
    main_formula = f"{variable} ~ C(Environment) + C(SPL_dB)"
    null_formula = f"{variable} ~ 1"

    full = smf.glm(formula=full_formula, data=df, family=tweedie_family()).fit()
    main = smf.glm(formula=main_formula, data=df, family=tweedie_family()).fit()
    null = smf.glm(formula=null_formula, data=df, family=tweedie_family()).fit()

    model_fit = pd.DataFrame([{
        "variable": variable,
        "log_likelihood": float(full.llf),
        "deviance": float(full.deviance),
        "pseudo_r2": float(1 - (full.deviance / null.deviance if null.deviance != 0 else np.nan)),
        "AIC": float(full.aic),
        "BIC": float(full.bic_llf if hasattr(full, "bic_llf") and np.isfinite(full.bic_llf) else (full.bic if np.isfinite(full.bic) else np.nan)),
        "pearson_chi2": float(full.pearson_chi2),
        "dispersion_phi": float(full.pearson_chi2 / full.df_resid) if full.df_resid != 0 else np.nan,
        "link_function": "log",
        "nobs": int(full.nobs),
        "df_model": float(full.df_model),
        "df_resid": float(full.df_resid),
    }])

    lr = pd.DataFrame([
        {
            "variable": variable,
            "comparison": "full_vs_null",
            "lr_statistic": float(2 * (full.llf - null.llf)),
            "df_diff": int(full.df_model - null.df_model),
            "p_value": float(stats.chi2.sf(2 * (full.llf - null.llf), int(full.df_model - null.df_model))),
        },
        {
            "variable": variable,
            "comparison": "full_vs_main_effects",
            "lr_statistic": float(2 * (full.llf - main.llf)),
            "df_diff": int(full.df_model - main.df_model),
            "p_value": float(stats.chi2.sf(2 * (full.llf - main.llf), int(full.df_model - main.df_model))),
        },
    ])

    params = full.summary2().tables[1].reset_index().rename(columns={"index": "term"})
    params = params.rename(columns={
        "Coef.": "coef",
        "Std.Err.": "std_err",
        "z": "wald_z",
        "P>|z|": "wald_p",
        "[0.025": "ci_low",
        "0.975]": "ci_high",
    })
    params["variable"] = variable
    params["exp_coef"] = np.exp(params["coef"])

    diag = pd.DataFrame([{
        "variable": variable,
        "full_formula": full_formula,
        "main_formula": main_formula,
        "null_formula": null_formula,
        "nobs": int(full.nobs),
    }])

    return model_fit, lr, params, diag

def mann_whitney_table(df: pd.DataFrame, variable: str, group_col: str = "Setup") -> pd.DataFrame:
    levels = list(df[group_col].cat.categories)
    x = df.loc[df[group_col] == levels[0], variable].to_numpy(dtype=float)
    y = df.loc[df[group_col] == levels[1], variable].to_numpy(dtype=float)
    res = stats.mannwhitneyu(x, y, alternative="two-sided", method="asymptotic", use_continuity=True)
    u1 = float(res.statistic)
    n1, n2 = len(x), len(y)
    ranks = pd.Series(np.r_[x, y]).rank(method="average")
    r1 = float(ranks.iloc[:n1].sum())
    r2 = float(ranks.iloc[n1:].sum())
    return pd.DataFrame([{
        "variable": variable,
        "group1": levels[0],
        "group2": levels[1],
        "u_statistic": u1,
        "p_value": float(res.pvalue),
        "rank_biserial_r": rank_biserial_from_u(u1, n1, n2),
        "common_language_effect_size": common_language_effect_size(u1, n1, n2),
        "group1_median": float(np.median(x)),
        "group2_median": float(np.median(y)),
        "R1": r1,
        "R2": r2,
        "n1": n1,
        "n2": n2,
        "alpha": ALPHA,
    }])

def kruskal_table(df: pd.DataFrame, variable: str, factor: str):
    groups = [sub[variable].dropna().to_numpy(dtype=float) for _, sub in df.groupby(factor, observed=True)]
    h, p = stats.kruskal(*groups)
    n = sum(len(g) for g in groups)
    k = len(groups)
    eps2 = epsilon_squared_kw(float(h), k, n)
    ranks = df[[factor, variable]].copy()
    ranks["rank"] = ranks[variable].rank(method="average")
    mean_ranks = ranks.groupby(factor, observed=True)["rank"].mean().reset_index(name="mean_rank")
    sizes = df.groupby(factor, observed=True)[variable].size().reset_index(name="n")
    summary = mean_ranks.merge(sizes, on=factor)
    omnibus = pd.DataFrame([{
        "variable": variable,
        "factor": factor,
        "H_statistic": float(h),
        "omnibus_p_value": float(p),
        "epsilon_squared": float(eps2),
        "df": k - 1,
        "k": k,
        "n": n,
        "alpha": ALPHA,
    }])
    try:
        import scikit_posthocs as sp  # type: ignore
        posthoc = sp.posthoc_dunn(df, val_col=variable, group_col=factor, p_adjust="holm").reset_index()
        posthoc = posthoc.rename(columns={"index": factor})
        # convert matrix-like output to long form
        long_rows = []
        cols = [c for c in posthoc.columns if c != factor]
        for _, row in posthoc.iterrows():
            g1 = row[factor]
            for g2 in cols:
                if str(g1) == str(g2):
                    continue
                long_rows.append({"group1": g1, "group2": g2, "p_adjusted": row[g2]})
        posthoc = pd.DataFrame(long_rows).drop_duplicates(subset=["group1", "group2"])
    except Exception:
        posthoc = pairwise_dunn_fallback(df[[factor, variable]].copy(), factor, variable)
    return omnibus, summary, posthoc

def analyze(df: pd.DataFrame, out_tables: Path, out_figures: Path) -> dict:
    results = {}

    mw_rows = []
    kw_rows = []
    kw_posthoc_tables = []
    glm_fits = []
    glm_lrs = []
    glm_params = []
    glm_diag = []
    omnibus_rows = []

    standalone = df[df["Setup"] == "Standalone"].copy()
    standalone["SPL_dB"] = standalone["SPL_dB"].astype(int)

    for var in RESPONSE_VARS:
        mw_rows.append(mann_whitney_table(df, var))

        omni_spl, summary_spl, posthoc_spl = kruskal_table(standalone, var, "SPL_dB")
        omni_spl["scope"] = "Standalone"
        kw_rows.append(omni_spl)

        summary_spl["variable"] = var
        summary_spl["scope"] = "Standalone"
        summary_spl["factor"] = "SPL_dB"
        kw_posthoc_tables.append(summary_spl.assign(variable=var, factor="SPL_dB"))

        omni_env, summary_env, posthoc_env = kruskal_table(standalone, var, "Environment")
        omni_env["scope"] = "Standalone"
        kw_rows.append(omni_env)

        summary_env["variable"] = var
        summary_env["scope"] = "Standalone"
        summary_env["factor"] = "Environment"
        kw_posthoc_tables.append(summary_env.assign(variable=var, factor="Environment"))

        if isinstance(posthoc_spl, pd.DataFrame):
            kw_posthoc_tables.append(posthoc_spl.assign(variable=var, factor="SPL_dB"))
        if isinstance(posthoc_env, pd.DataFrame):
            kw_posthoc_tables.append(posthoc_env.assign(variable=var, factor="Environment"))

        fit, lr, params, diag = fit_tweedie_models(standalone, var)
        glm_fits.append(fit)
        glm_lrs.append(lr)
        glm_params.append(params)
        glm_diag.append(diag)

        omnibus_rows.append(omnibus_factorial_table(df, var))

    mw = pd.concat(mw_rows, ignore_index=True)
    kw = pd.concat(kw_rows, ignore_index=True)
    kw_posthoc = pd.concat(kw_posthoc_tables, ignore_index=True) if kw_posthoc_tables else pd.DataFrame()
    fits = pd.concat(glm_fits, ignore_index=True)
    lrs = pd.concat(glm_lrs, ignore_index=True)
    params = pd.concat(glm_params, ignore_index=True)
    diag = pd.concat(glm_diag, ignore_index=True)
    omnibus = pd.concat(omnibus_rows, ignore_index=True)

    mw_apa = mw.rename(columns={"u_statistic": "U", "p_value": "p", "rank_biserial_r": "r_rb", "common_language_effect_size": "CL"})
    print_apa_table(mw_apa, 6, "Mann–Whitney U Test Comparing Standalone and Integrated Harvesters")
    results["mann_whitney"] = save_table(mw, out_tables, "objective3_mann_whitney", title="Mann–Whitney U Test Comparing Standalone and Integrated Harvesters", table_number=6)

    kw_apa = kw.rename(columns={"H_statistic": "H", "omnibus_p_value": "p", "epsilon_squared": "ε²"})
    print_apa_table(kw_apa, 7, "Kruskal–Wallis Test Results Across SPL and Environment")
    results["kruskal_wallis"] = save_table(kw, out_tables, "objective3_kruskal_wallis", title="Kruskal–Wallis Test Results Across SPL and Environment", table_number=7)

    print_apa_table(kw_posthoc, 8, "Dunn Post Hoc Comparisons")
    results["dunn_posthoc"] = save_table(kw_posthoc, out_tables, "objective3_dunn_posthoc", title="Dunn Post Hoc Comparisons", table_number=8)

    print_apa_table(fits, 9, "Tweedie GLM Fit")
    results["glm_fit"] = save_table(fits, out_tables, "objective3_tweedie_glm_fit", title="Tweedie GLM Fit", table_number=9)

    print_apa_table(lrs, 10, "Tweedie GLM Likelihood-Ratio Tests")
    results["glm_lr"] = save_table(lrs, out_tables, "objective3_tweedie_glm_lrt", title="Tweedie GLM Likelihood-Ratio Tests", table_number=10)

    params_apa = params.rename(columns={
        "coef": "B",
        "std_err": "SE",
        "wald_z": "z",
        "wald_p": "p",
        "exp_coef": "Exp(B)"
    })
    print_apa_table(params_apa, 11, "Tweedie Log-GLM Parameter Estimates")
    results["glm_params"] = save_table(params, out_tables, "objective3_tweedie_glm_params", title="Tweedie Log-GLM Parameter Estimates", table_number=11)

    print_apa_table(diag, 12, "Tweedie GLM Diagnostics")
    results["glm_diag"] = save_table(diag, out_tables, "objective3_tweedie_glm_diag", title="Tweedie GLM Diagnostics", table_number=12)

    omnibus_apa = omnibus.copy()
    print_apa_table(omnibus_apa, 13, "Omnibus Test Results")
    results["omnibus"] = save_table(omnibus_apa, out_tables, "objective3_omnibus_factorial", title="Omnibus Test Results", table_number=13)

    return results
