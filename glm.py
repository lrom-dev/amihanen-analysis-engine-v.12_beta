
"""
glm_selector_v5.py

Advanced GLM + Hurdle Model Selector
Ranking based on CV metrics only.

Includes:
- Gaussian (Identity, Log)
- Gamma (Log, Identity)
- Inverse Gaussian (Log, Identity)
- Tweedie (1.1-1.9)
- Hurdle Gamma
- Hurdle Inverse Gaussian
- Hurdle Tweedie (1.3,1.5,1.7)

Outputs:
- ranking.csv
- ranking.txt
- best_model_summary.txt

# ==========================================================
# tweedie_visualizations.py
#
# Visualization-only Tweedie-Log GLM analysis
#
# Produces:
#
# 1. Tweedie fitted curves
# 2. 3D response surfaces
# 3. Setup-effect plots
# 4. Observed vs Predicted plots
#
# Responses:
#   dcVoltage
#   dcCurrent
#   dcPower
#
# ==========================================================
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")

RESPONSES = ["DC_Voltage", "DC_Current", "DC_Power"]


def preprocess_data(df):
    df = df.copy()

    rename = {
        "setup": "Setup",
        "env": "Environment",
        "spl": "SPL_dB",
        "dcVoltage": "DC_Voltage",
        "dcCurrent": "DC_Current",
        "dcPower": "DC_Power",
    }
    df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)

    for c in ["Setup", "Environment"]:
        if c in df.columns:
            df[c] = df[c].astype("category")

    return df


def formula(response):
    return f"{response} ~ C(Setup) + C(Environment) + SPL_dB"


def glm_registry():
    models = [
        ("Gaussian_Identity",
            sm.families.Gaussian(sm.families.links.Identity())),
        ("Gaussian_Log",
            sm.families.Gaussian(sm.families.links.Log())),
        ("Gamma_Log",
            sm.families.Gamma(sm.families.links.Log())),
        ("Gamma_Identity",
            sm.families.Gamma(sm.families.links.Identity())),
        ("InverseGaussian_Log",
            sm.families.InverseGaussian(sm.families.links.Log())),
        ("InverseGaussian_Identity",
            sm.families.InverseGaussian(sm.families.links.Identity())),
    ]

    for p in np.arange(1.1, 2.0, 0.1):
        models.append(
            (
                f"Tweedie_{p:.1f}",
                sm.families.Tweedie(
                    var_power=round(float(p), 1),
                    link=sm.families.links.Log(),
                ),
            )
        )

    return models


def metrics(y, pred):
    return {
        "RMSE": float(np.sqrt(mean_squared_error(y, pred))),
        "MAE": float(mean_absolute_error(y, pred)),
        "R2": float(r2_score(y, pred)),
    }


def fit_standard_glm(df, response, family):
    fit_df = df

    if isinstance(family, (sm.families.Gamma, sm.families.InverseGaussian)):
        fit_df = df[df[response] > 0].copy()

    fit = smf.glm(
        formula=formula(response),
        data=fit_df,
        family=family,
    ).fit()

    pred = np.asarray(fit.predict(df))

    m = metrics(df[response], pred)

    pseudo_r2 = np.nan
    if getattr(fit, "null_deviance", 0) > 0:
        pseudo_r2 = 1 - fit.deviance / fit.null_deviance

    disp = np.nan
    if getattr(fit, "df_resid", 0) > 0:
        try:
            disp = fit.pearson_chi2 / fit.df_resid
        except Exception:
            pass

    return {
        "fit": fit,
        "pred": pred,
        "AIC": getattr(fit, "aic", np.nan),
        "BIC": getattr(fit, "bic", np.nan),
        "LLF": getattr(fit, "llf", np.nan),
        "PseudoR2": pseudo_r2,
        "Dispersion": disp,
        **m,
    }


def fit_hurdle(df, response, family, label):
    active = (df[response] > 0).astype(int)

    work = df.copy()
    work["_active"] = active

    logistic = smf.glm(
        "_active ~ C(Setup) + C(Environment) + SPL_dB",
        data=work,
        family=sm.families.Binomial(),
    ).fit()

    positive_df = df[df[response] > 0].copy()

    positive_model = smf.glm(
        formula=formula(response),
        data=positive_df,
        family=family,
    ).fit()

    p_active = np.asarray(logistic.predict(df))
    positive_pred = np.asarray(positive_model.predict(df))

    final_pred = p_active * positive_pred

    m = metrics(df[response], final_pred)

    return {
        "fit": (logistic, positive_model),
        "pred": final_pred,
        "AIC": logistic.aic + positive_model.aic,
        "BIC": np.nan,
        "LLF": logistic.llf + positive_model.llf,
        "PseudoR2": np.nan,
        "Dispersion": np.nan,
        **m,
        "Model": label,
    }


def cross_validate_standard(df, response, family):
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    rmses, maes, r2s = [], [], []

    for tr, te in kf.split(df):
        train = df.iloc[tr]
        test = df.iloc[te]

        try:
            fit_train = train

            if isinstance(family, (sm.families.Gamma, sm.families.InverseGaussian)):
                fit_train = train[train[response] > 0]

            fit = smf.glm(
                formula=formula(response),
                data=fit_train,
                family=family,
            ).fit()

            pred = fit.predict(test)

            rmses.append(np.sqrt(mean_squared_error(test[response], pred)))
            maes.append(mean_absolute_error(test[response], pred))
            r2s.append(r2_score(test[response], pred))

        except Exception:
            pass

    return np.mean(rmses), np.mean(maes), np.mean(r2s)


def cross_validate_hurdle(df, response, family):
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    rmses, maes, r2s = [], [], []

    for tr, te in kf.split(df):
        train = df.iloc[tr].copy()
        test = df.iloc[te].copy()

        try:
            train["_active"] = (train[response] > 0).astype(int)

            logit = smf.glm(
                "_active ~ C(Setup) + C(Environment) + SPL_dB",
                data=train,
                family=sm.families.Binomial(),
            ).fit()

            pos = train[train[response] > 0]

            glm = smf.glm(
                formula=formula(response),
                data=pos,
                family=family,
            ).fit()

            pred = logit.predict(test) * glm.predict(test)

            rmses.append(np.sqrt(mean_squared_error(test[response], pred)))
            maes.append(mean_absolute_error(test[response], pred))
            r2s.append(r2_score(test[response], pred))

        except Exception:
            pass

    return np.mean(rmses), np.mean(maes), np.mean(r2s)


def analyze_dataframe(df, output_dir="outputs/glm_selection_v4"):
    df = preprocess_data(df)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for response in RESPONSES:

        if response not in df.columns:
            continue

        print(f"\n{'='*70}")
        print(response)
        print(f"{'='*70}")

        rows = []
        fitted = {}

        for name, family in glm_registry():
            try:
                res = fit_standard_glm(df, response, family)
                cv_rmse, cv_mae, cv_r2 = cross_validate_standard(df, response, family)

                print(f"{name:30s} CV_RMSE={cv_rmse:.6f} CV_R2={cv_r2:.6f}")

                rows.append({
                    "Model": name,
                    **{k: v for k, v in res.items() if k != "fit" and k != "pred"},
                    "CV_RMSE": cv_rmse,
                    "CV_MAE": cv_mae,
                    "CV_R2": cv_r2,
                })

                fitted[name] = res["fit"]

            except Exception as e:
                print(f"{name}: FAILED ({e})")

        hurdle_models = [
            ("Hurdle_Gamma", sm.families.Gamma(sm.families.links.Log())),
            ("Hurdle_InvGauss", sm.families.InverseGaussian(sm.families.links.Log())),
            ("Hurdle_Tweedie_1.3", sm.families.Tweedie(var_power=1.3, link=sm.families.links.Log())),
            ("Hurdle_Tweedie_1.5", sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log())),
            ("Hurdle_Tweedie_1.7", sm.families.Tweedie(var_power=1.7, link=sm.families.links.Log())),
        ]

        for name, fam in hurdle_models:
            try:
                res = fit_hurdle(df, response, fam, name)
                cv_rmse, cv_mae, cv_r2 = cross_validate_hurdle(df, response, fam)

                print(f"{name:30s} CV_RMSE={cv_rmse:.6f} CV_R2={cv_r2:.6f}")

                rows.append({
                    "Model": name,
                    **{k: v for k, v in res.items() if k not in ("fit", "pred", "Model")},
                    "CV_RMSE": cv_rmse,
                    "CV_MAE": cv_mae,
                    "CV_R2": cv_r2,
                })

                fitted[name] = res["fit"]

            except Exception as e:
                print(f"{name}: FAILED ({e})")

        ranking = pd.DataFrame(rows)

        ranking["Rank"] = (
            ranking["CV_RMSE"].rank(na_option="bottom")
            + ranking["CV_MAE"].rank(na_option="bottom")
            + (-ranking["CV_R2"]).rank(na_option="bottom")
        )

        ranking = ranking.sort_values("Rank")

        response_dir = out / response
        response_dir.mkdir(exist_ok=True)

        ranking.to_csv(response_dir / "ranking.csv", index=False)

        with open(response_dir / "ranking.txt", "w", encoding="utf-8") as f:
            f.write(ranking.to_string(index=False))

        if len(ranking):
            winner = ranking.iloc[0]["Model"]
            print(f"\nBEST MODEL: {winner}")

            with open(response_dir / "best_model_summary.txt", "w", encoding="utf-8") as f:

                fit_obj = fitted[winner]

                if isinstance(fit_obj, tuple):
                    f.write("ACTIVATION MODEL\n\n")
                    f.write(str(fit_obj[0].summary()))
                    f.write("\n\nPOSITIVE MODEL\n\n")
                    f.write(str(fit_obj[1].summary()))
                else:
                    f.write(str(fit_obj.summary()))

    print("\nFinished.")


def analyze_csv(csv_path, output_dir="glm.selector-output/glm_selection_v4"):
    return analyze_dataframe(pd.read_csv(csv_path), output_dir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python glm_selector_v4.py data.csv")
        sys.exit(1)

    analyze_csv(sys.argv[1])


# ==========================================================
# CONFIGURATION
# ==========================================================

CSV_FILE = "amihanen_dataset.csv"

OUTPUT_DIR = Path("glm-results")
OUTPUT_DIR.mkdir(exist_ok=True)

TWEEDIE_POWER = 1.5

RESPONSES = {
    "dcVoltage": "Voltage (V)",
    "dcCurrent": "Current (A)",
    "dcPower": "Power (W)",
}

ENV_MAP = {
    "Ind.": 0,
    "Traf.": 1,
    "Comm.": 2,
}

ENV_LABELS = [
    "Industrial",
    "Traffic",
    "Commercial",
]

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(CSV_FILE)

df["SPL_dB"] = (
    df["spl"]
    .str.replace(" dB", "", regex=False)
    .astype(float)
)

df["Setup"] = df["setup"]
df["Environment"] = df["env"]

# ==========================================================
# TWEEDIE MODEL
# ==========================================================

def fit_tweedie(response):

    formula = (
        f"{response} ~ "
        "C(Setup) + "
        "SPL_dB * C(Environment)"
    )

    model = smf.glm(
        formula=formula,
        data=df,
        family=sm.families.Tweedie(
            var_power=TWEEDIE_POWER,
            link=sm.families.links.Log()
        )
    )

    return model.fit()

# ==========================================================
# FIGURE 1
# FITTED CURVES
# ==========================================================

def plot_fitted_curves(response, fit):

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(14, 5),
        sharey=True
    )

    spl_grid = np.linspace(60, 100, 300)

    colors = {
        "Ind.": "red",
        "Traf.": "blue",
        "Comm.": "green"
    }

    for ax, setup in zip(
        axes,
        ["A", "B"]
    ):

        subset = df[
            df["Setup"] == setup
        ]

        for env in ENV_MAP:

            env_data = subset[
                subset["Environment"] == env
            ]

            ax.scatter(
                env_data["SPL_dB"],
                env_data[response],
                color=colors[env],
                alpha=0.75
            )

            pred_df = pd.DataFrame({
                "SPL_dB": spl_grid,
                "Environment": env,
                "Setup": setup
            })

            pred = fit.predict(pred_df)

            ax.plot(
                spl_grid,
                pred,
                color=colors[env],
                linewidth=3,
                label=env
            )

        ax.set_title(
            f"Setup {setup}"
        )

        ax.set_xlabel(
            "SPL (dB)"
        )

        ax.grid(alpha=0.3)

    axes[0].set_ylabel(response)

    handles, labels = (
        axes[0]
        .get_legend_handles_labels()
    )

    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR /
        f"{response}_fitted_curves.png",
        dpi=600
    )

    plt.close()

# ==========================================================
# FIGURE 2
# 3D RESPONSE SURFACES
# ==========================================================

def plot_response_surface(
    response,
    fit
):

    for setup in ["A", "B"]:

        fig = plt.figure(
            figsize=(10, 8)
        )

        ax = fig.add_subplot(
            111,
            projection="3d"
        )

        spl_grid = np.linspace(
            60,
            100,
            100
        )

        env_grid = np.array([
            0,
            1,
            2
        ])

        X, Y = np.meshgrid(
            spl_grid,
            env_grid
        )

        Z = np.zeros_like(X)

        env_names = list(
            ENV_MAP.keys()
        )

        for i, env in enumerate(
            env_names
        ):

            pred_df = pd.DataFrame({
                "SPL_dB": spl_grid,
                "Environment": env,
                "Setup": setup
            })

            Z[i, :] = fit.predict(
                pred_df
            )

        surf = ax.plot_surface(
            X,
            Y,
            Z,
            cmap="viridis",
            alpha=0.85
        )

        observed = df[
            df["Setup"] == setup
        ]

        obs_env = (
            observed["Environment"]
            .map(ENV_MAP)
        )

        ax.scatter(
            observed["SPL_dB"],
            obs_env,
            observed[response],
            color="black",
            s=40
        )

        ax.set_xlabel(
            "SPL (dB)"
        )

        ax.set_ylabel(
            "Environment"
        )

        ax.set_zlabel(
            response
        )

        ax.set_yticks([
            0, 1, 2
        ])

        ax.set_yticklabels(
            ENV_LABELS
        )

        ax.set_title(
            f"{response} Surface "
            f"(Setup {setup})"
        )

        fig.colorbar(
            surf,
            shrink=0.7
        )

        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR /
            f"{response}_surface_setup_{setup}.png",
            dpi=600
        )

        plt.close()

# ==========================================================
# FIGURE 3
# SETUP EFFECT PLOT
# ==========================================================

def plot_setup_effect(
    response,
    fit
):

    spl_grid = np.linspace(
        60,
        100,
        300
    )

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    for setup in ["A", "B"]:

        pred_df = pd.DataFrame({
            "SPL_dB": spl_grid,
            "Environment": "Ind.",
            "Setup": setup
        })

        pred = fit.predict(
            pred_df
        )

        ax.plot(
            spl_grid,
            pred,
            linewidth=3,
            label=f"Setup {setup}"
        )

    ax.set_xlabel(
        "SPL (dB)"
    )

    ax.set_ylabel(
        response
    )

    ax.set_title(
        f"Setup Effect ({response})"
    )

    ax.legend()

    ax.grid(alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR /
        f"{response}_setup_effect.png",
        dpi=600
    )

    plt.close()

# ==========================================================
# FIGURE 4
# OBSERVED VS PREDICTED
# ==========================================================

def plot_observed_vs_predicted(
    response,
    fit
):

    obs = df[response]

    pred = fit.predict(df)

    fig, ax = plt.subplots(
        figsize=(7, 7)
    )

    ax.scatter(
        obs,
        pred,
        alpha=0.8
    )

    mn = min(
        obs.min(),
        pred.min()
    )

    mx = max(
        obs.max(),
        pred.max()
    )

    ax.plot(
        [mn, mx],
        [mn, mx],
        "k--",
        linewidth=2
    )

    ax.set_xlabel(
        "Observed"
    )

    ax.set_ylabel(
        "Predicted"
    )

    ax.set_title(
        f"Observed vs Predicted "
        f"({response})"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR /
        f"{response}_observed_vs_predicted.png",
        dpi=600
    )

    plt.close()

# ==========================================================
# MAIN
# ==========================================================

for response in RESPONSES:

    print(
        f"Processing {response}..."
    )

    fit = fit_tweedie(
        response
    )

    plot_fitted_curves(
        response,
        fit
    )

    plot_response_surface(
        response,
        fit
    )

    plot_setup_effect(
        response,
        fit
    )

    plot_observed_vs_predicted(
        response,
        fit
    )

print(
    "\nDone."
)

print(
    f"Figures saved to:\n"
    f"{OUTPUT_DIR.resolve()}"
)