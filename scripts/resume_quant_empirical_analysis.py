from __future__ import annotations

import argparse
import json
import math
import sqlite3
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf
from arch import arch_model
from scipy.stats import chi2, norm
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

START = "2010-01-01"
END = "2026-10-01"
RISK_TICKERS = ["SPY", "TLT", "GLD", "IWM"]
SECTOR_TICKERS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
EXTRA_TICKERS = ["QQQ"]
ALL_TICKERS = sorted(set(RISK_TICKERS + SECTOR_TICKERS + EXTRA_TICKERS))
FRED_SERIES = ["DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"]


def _download_one_ticker(ticker: str) -> pd.DataFrame:
    last_error: Exception | None = None
    for _ in range(3):
        try:
            df = yf.download(
                ticker,
                start=START,
                end=END,
                auto_adjust=False,
                progress=False,
                threads=False,
                actions=False,
            )
            if isinstance(df.columns, pd.MultiIndex):
                if ticker in df.columns.get_level_values(-1):
                    df = df.xs(ticker, axis=1, level=-1)
                else:
                    df.columns = df.columns.get_level_values(0)
            df = df.rename(columns={c: str(c) for c in df.columns})
            if not df.empty and ("Adj Close" in df.columns or "Close" in df.columns):
                df.index = pd.to_datetime(df.index).tz_localize(None)
                df.index.name = "date"
                return df
        except Exception as exc:  # pragma: no cover - network retry
            last_error = exc
    raise RuntimeError(f"Failed to download {ticker}: {last_error}")


def download_market_data() -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for ticker in ALL_TICKERS:
        out[ticker] = _download_one_ticker(ticker)
    return out


def download_fred_rates() -> pd.DataFrame:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=" + ",".join(FRED_SERIES)
    df = pd.read_csv(url)
    date_col = "DATE" if "DATE" in df.columns else "observation_date"
    df = df.rename(columns={date_col: "date"})
    df["date"] = pd.to_datetime(df["date"])
    for col in FRED_SERIES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[(df["date"] >= START) & (df["date"] < END)].set_index("date").sort_index()
    return df


def create_sqlite_pipeline(
    market: dict[str, pd.DataFrame], rates: pd.DataFrame, db_path: Path
) -> tuple[sqlite3.Connection, dict[str, Any]]:
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.executescript(
        """
        CREATE TABLE asset_prices (
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL NOT NULL,
            volume REAL,
            PRIMARY KEY (date, ticker)
        );
        CREATE INDEX idx_asset_prices_ticker_date ON asset_prices(ticker, date);
        CREATE TABLE treasury_yields (
            date TEXT NOT NULL,
            tenor TEXT NOT NULL,
            yield_pct REAL NOT NULL,
            PRIMARY KEY (date, tenor)
        );
        CREATE INDEX idx_treasury_yields_tenor_date ON treasury_yields(tenor, date);
        """
    )

    price_rows: list[tuple[Any, ...]] = []
    raw_price_rows = 0
    dropped_price_missing_adj = 0
    for ticker, df in market.items():
        adj_col = "Adj Close" if "Adj Close" in df.columns else "Close"
        for dt, row in df.iterrows():
            raw_price_rows += 1
            adj = pd.to_numeric(row.get(adj_col), errors="coerce")
            if pd.isna(adj):
                dropped_price_missing_adj += 1
                continue
            def val(name: str) -> float | None:
                x = pd.to_numeric(row.get(name), errors="coerce")
                return None if pd.isna(x) else float(x)
            price_rows.append(
                (
                    dt.strftime("%Y-%m-%d"),
                    ticker,
                    val("Open"),
                    val("High"),
                    val("Low"),
                    val("Close"),
                    float(adj),
                    val("Volume"),
                )
            )
    con.executemany(
        "INSERT INTO asset_prices VALUES (?, ?, ?, ?, ?, ?, ?, ?)", price_rows
    )

    raw_rate_cells = int(rates.shape[0] * rates.shape[1])
    rate_rows: list[tuple[str, str, float]] = []
    for dt, row in rates.iterrows():
        for tenor in FRED_SERIES:
            value = row[tenor]
            if pd.notna(value):
                rate_rows.append((dt.strftime("%Y-%m-%d"), tenor, float(value)))
    con.executemany("INSERT INTO treasury_yields VALUES (?, ?, ?)", rate_rows)
    con.commit()

    price_count = con.execute("SELECT COUNT(*) FROM asset_prices").fetchone()[0]
    rate_count = con.execute("SELECT COUNT(*) FROM treasury_yields").fetchone()[0]
    price_dups = con.execute(
        """
        SELECT COUNT(*) FROM (
          SELECT date, ticker, COUNT(*) c FROM asset_prices
          GROUP BY date, ticker HAVING c > 1
        )
        """
    ).fetchone()[0]
    rate_dups = con.execute(
        """
        SELECT COUNT(*) FROM (
          SELECT date, tenor, COUNT(*) c FROM treasury_yields
          GROUP BY date, tenor HAVING c > 1
        )
        """
    ).fetchone()[0]
    return con, {
        "market_source": "Yahoo Finance via yfinance",
        "rates_source": "Federal Reserve Bank of St. Louis FRED / Federal Reserve H.15",
        "period_start": START,
        "period_end_exclusive": END,
        "tickers": ALL_TICKERS,
        "asset_price_rows_raw": raw_price_rows,
        "asset_price_rows_loaded": int(price_count),
        "asset_price_rows_dropped_missing_adjusted_close": int(dropped_price_missing_adj),
        "treasury_rate_cells_raw": raw_rate_cells,
        "treasury_yield_rows_loaded": int(rate_count),
        "treasury_missing_cells_excluded": int(raw_rate_cells - rate_count),
        "duplicate_asset_primary_keys": int(price_dups),
        "duplicate_rate_primary_keys": int(rate_dups),
    }


def prices_from_sql(con: sqlite3.Connection, tickers: list[str]) -> pd.DataFrame:
    placeholders = ",".join("?" for _ in tickers)
    query = f"""
        SELECT date, ticker, adj_close
        FROM asset_prices
        WHERE ticker IN ({placeholders})
        ORDER BY date, ticker
    """
    df = pd.read_sql_query(query, con, params=tickers, parse_dates=["date"])
    return df.pivot(index="date", columns="ticker", values="adj_close").dropna()


def kupiec_test(breaches: np.ndarray, alpha: float) -> tuple[float, float]:
    n = len(breaches)
    x = int(np.sum(breaches))
    if x == 0 or x == n:
        return float("inf"), 0.0
    phat = x / n
    ll0 = (n - x) * math.log(1 - alpha) + x * math.log(alpha)
    ll1 = (n - x) * math.log(1 - phat) + x * math.log(phat)
    lr = -2 * (ll0 - ll1)
    return float(lr), float(chi2.sf(lr, 1))


def fit_garch_train(train: pd.Series) -> dict[str, float]:
    scaled = train.dropna() * 100.0
    model = arch_model(
        scaled, mean="Constant", vol="GARCH", p=1, q=1, dist="normal", rescale=False
    )
    res = model.fit(disp="off")
    p = res.params
    return {
        "mu": float(p["mu"]),
        "omega": float(p["omega"]),
        "alpha": float(p["alpha[1]"]),
        "beta": float(p["beta[1]"]),
        "last_variance": float(res.conditional_volatility.iloc[-1] ** 2),
        "last_epsilon": float(scaled.iloc[-1] - p["mu"]),
    }


def garch_variance_forecast_series(
    full_returns: pd.Series, test_index: pd.DatetimeIndex, params: dict[str, float]
) -> pd.Series:
    mu = params["mu"]
    omega = params["omega"]
    alpha = params["alpha"]
    beta = params["beta"]
    var_next = omega + alpha * params["last_epsilon"] ** 2 + beta * params["last_variance"]
    forecasts: dict[pd.Timestamp, float] = {}
    for dt in test_index:
        forecasts[dt] = var_next / 10000.0
        r_pct = float(full_returns.loc[dt] * 100.0)
        eps = r_pct - mu
        var_next = omega + alpha * eps**2 + beta * var_next
    return pd.Series(forecasts, dtype=float)


def risk_analysis(con: sqlite3.Connection) -> tuple[dict[str, Any], dict[str, float]]:
    prices = prices_from_sql(con, RISK_TICKERS)
    rets = prices.pct_change().dropna()
    portfolio = rets.mean(axis=1)
    train = portfolio[portfolio.index < "2020-01-01"]
    test = portfolio[(portfolio.index >= "2020-01-01") & (portfolio.index < END)]
    alpha_tail = 0.01
    z = norm.ppf(alpha_tail)
    garch_params = fit_garch_train(train)
    garch_var = garch_variance_forecast_series(portfolio, test.index, garch_params)

    rows: list[dict[str, Any]] = []
    for dt, r in test.items():
        hist = portfolio.loc[:dt].iloc[:-1].tail(500)
        if len(hist) < 250:
            continue
        mu = float(hist.mean())
        sigma = float(hist.std(ddof=1))
        q_gauss = mu + z * sigma
        es_gauss = -(mu - sigma * norm.pdf(z) / alpha_tail)
        q_hist = float(hist.quantile(alpha_tail))
        tail = hist[hist <= q_hist]
        es_hist = -float(tail.mean())
        gv = float(garch_var.loc[dt])
        gs = math.sqrt(max(gv, 1e-16))
        gmu = garch_params["mu"] / 100.0
        q_garch = gmu + z * gs
        es_garch = -(gmu - gs * norm.pdf(z) / alpha_tail)
        rows.append(
            {
                "date": dt,
                "return": float(r),
                "gaussian_q": q_gauss,
                "gaussian_es": es_gauss,
                "historical_q": q_hist,
                "historical_es": es_hist,
                "garch_q": q_garch,
                "garch_es": es_garch,
            }
        )
    df = pd.DataFrame(rows).set_index("date")

    models: dict[str, Any] = {}
    for name in ["gaussian", "historical", "garch"]:
        breach = (df["return"] < df[f"{name}_q"]).to_numpy()
        lr, pval = kupiec_test(breach, alpha_tail)
        realized_breach_loss = -df.loc[breach, "return"].mean() if breach.any() else np.nan
        models[name] = {
            "observations": int(len(df)),
            "breaches": int(breach.sum()),
            "breach_rate_pct": float(100 * breach.mean()),
            "target_breach_rate_pct": 1.0,
            "absolute_coverage_error_pp": float(abs(100 * breach.mean() - 1.0)),
            "kupiec_lr": lr,
            "kupiec_p_value": pval,
            "average_forecast_es_pct": float(100 * df[f"{name}_es"].mean()),
            "average_realized_loss_on_breaches_pct": float(100 * realized_breach_loss)
            if pd.notna(realized_breach_loss)
            else None,
        }

    stress = df.loc["2020-02-19":"2020-05-29"]
    stress_summary: dict[str, Any] = {}
    for name in ["gaussian", "historical", "garch"]:
        breach = stress["return"] < stress[f"{name}_q"]
        stress_summary[name] = {
            "observations": int(len(stress)),
            "breaches": int(breach.sum()),
            "breach_rate_pct": float(100 * breach.mean()) if len(stress) else None,
        }

    best = min(models, key=lambda k: models[k]["absolute_coverage_error_pp"])
    baseline_error = models["gaussian"]["absolute_coverage_error_pp"]
    best_error = models[best]["absolute_coverage_error_pp"]
    coverage_error_reduction = None
    if baseline_error > 0:
        coverage_error_reduction = 100 * (baseline_error - best_error) / baseline_error
    result = {
        "portfolio": "equal-weight SPY/TLT/GLD/IWM",
        "training_period": [str(train.index.min().date()), str(train.index.max().date())],
        "test_period": [str(df.index.min().date()), str(df.index.max().date())],
        "models": models,
        "covid_stress_window": stress_summary,
        "best_by_absolute_coverage_error": best,
        "coverage_error_reduction_vs_gaussian_pct": float(coverage_error_reduction)
        if coverage_error_reduction is not None
        else None,
        "garch_parameters": {k: float(v) for k, v in garch_params.items() if k not in {"last_variance", "last_epsilon"}},
    }
    return result, garch_params


def time_series_volatility_analysis(
    con: sqlite3.Connection, garch_params_portfolio_unused: dict[str, float] | None = None
) -> dict[str, Any]:
    spy = prices_from_sql(con, ["SPY"])["SPY"]
    r = spy.pct_change().dropna()
    train = r[r.index < "2020-01-01"]
    test = r[(r.index >= "2020-01-01") & (r.index < END)]
    gparams = fit_garch_train(train)
    gvar = garch_variance_forecast_series(r, test.index, gparams)

    rolling_var = r.rolling(20).var(ddof=0).shift(1).reindex(test.index)
    ewma = pd.Series(index=r.index, dtype=float)
    initial = float(train.iloc[:60].var(ddof=0))
    ewma.iloc[0] = initial
    lam = 0.94
    for i in range(1, len(r)):
        ewma.iloc[i] = lam * ewma.iloc[i - 1] + (1 - lam) * float(r.iloc[i - 1] ** 2)
    ewma_test = ewma.reindex(test.index)
    target = test**2

    def qlike(y: pd.Series, f: pd.Series) -> float:
        yv = np.maximum(y.to_numpy(), 1e-12)
        fv = np.maximum(f.to_numpy(), 1e-12)
        ratio = yv / fv
        return float(np.mean(ratio - np.log(ratio) - 1.0))

    metrics: dict[str, Any] = {}
    forecasts = {"rolling20": rolling_var, "ewma94": ewma_test, "garch11": gvar}
    for name, f in forecasts.items():
        valid = pd.concat([target.rename("y"), f.rename("f")], axis=1).dropna()
        mse = float(mean_squared_error(valid["y"], valid["f"]))
        metrics[name] = {
            "observations": int(len(valid)),
            "qlike": qlike(valid["y"], valid["f"]),
            "variance_mse": mse,
        }
    baseline = metrics["rolling20"]["qlike"]
    best = min(metrics, key=lambda k: metrics[k]["qlike"])
    improvement = 100 * (baseline - metrics[best]["qlike"]) / baseline
    return {
        "asset": "SPY",
        "training_period": [str(train.index.min().date()), str(train.index.max().date())],
        "test_period": [str(test.index.min().date()), str(test.index.max().date())],
        "metrics": metrics,
        "best_by_qlike": best,
        "qlike_reduction_vs_rolling20_pct": float(improvement),
        "garch_parameters": {k: float(v) for k, v in gparams.items() if k not in {"last_variance", "last_epsilon"}},
    }


def fixed_income_analysis(con: sqlite3.Connection) -> dict[str, Any]:
    query = "SELECT date, tenor, yield_pct FROM treasury_yields ORDER BY date, tenor"
    long = pd.read_sql_query(query, con, parse_dates=["date"])
    panel = long.pivot(index="date", columns="tenor", values="yield_pct")
    complete = panel.dropna(subset=FRED_SERIES)
    latest_date = complete.index.max()
    latest = complete.loc[latest_date]

    known_maturities = np.array([1, 2, 3, 5, 7, 10, 20, 30], dtype=float)
    known_yields = np.array([latest[s] for s in FRED_SERIES], dtype=float) / 100.0
    annual_maturities = np.arange(1, 31, dtype=float)
    par_rates = np.interp(annual_maturities, known_maturities, known_yields)

    dfs: list[float] = []
    for n, c in enumerate(par_rates, start=1):
        coupon = 100.0 * c
        prior_pv = coupon * sum(dfs)
        df_n = (100.0 - prior_pv) / (100.0 + coupon)
        dfs.append(df_n)
    dfs_arr = np.array(dfs)
    zeros = -np.log(dfs_arr) / annual_maturities

    face = 100.0
    coupon_rate = 0.04
    maturity = 10
    cashflows = np.full(maturity, face * coupon_rate)
    cashflows[-1] += face
    t = np.arange(1, maturity + 1, dtype=float)
    base_zero = zeros[:maturity]

    def price_with_shift(shift: float) -> float:
        disc = np.exp(-(base_zero + shift) * t)
        return float(np.dot(cashflows, disc))

    p0 = price_with_shift(0.0)
    h = 0.0001
    p_plus = price_with_shift(h)
    p_minus = price_with_shift(-h)
    duration = -(p_plus - p_minus) / (2 * h * p0)
    convexity = (p_plus + p_minus - 2 * p0) / (h * h * p0)

    shock_rows: list[dict[str, Any]] = []
    for bp in [-200, -100, -50, -25, 25, 50, 100, 200]:
        dy = bp / 10000.0
        exact = price_with_shift(dy) - p0
        dur_approx = p0 * (-duration * dy)
        dc_approx = p0 * (-duration * dy + 0.5 * convexity * dy * dy)
        shock_rows.append(
            {
                "shock_bp": bp,
                "exact_delta_price": exact,
                "duration_delta_price": dur_approx,
                "duration_convexity_delta_price": dc_approx,
                "duration_abs_error": abs(dur_approx - exact),
                "duration_convexity_abs_error": abs(dc_approx - exact),
            }
        )
    shock_df = pd.DataFrame(shock_rows)
    mae_d = float(shock_df["duration_abs_error"].mean())
    mae_dc = float(shock_df["duration_convexity_abs_error"].mean())
    reduction = 100 * (mae_d - mae_dc) / mae_d

    swap_maturity = 5
    annuity = float(dfs_arr[:swap_maturity].sum())
    par_swap_rate = (1.0 - dfs_arr[swap_maturity - 1]) / annuity
    def swap_pv(shift: float) -> float:
        shifted_df = np.exp(-(zeros[:swap_maturity] + shift) * np.arange(1, swap_maturity + 1))
        fixed_leg = par_swap_rate * float(shifted_df.sum())
        float_leg = 1.0 - float(shifted_df[-1])
        return 100.0 * (float_leg - fixed_leg)
    swap_dv01 = swap_pv(0.0001) - swap_pv(0.0)

    return {
        "curve_date": str(latest_date.date()),
        "fred_cmt_yields_pct": {s: float(latest[s]) for s in FRED_SERIES},
        "method": "Linear interpolation of Treasury CMT yields to annual maturities followed by annual par-style discount-factor bootstrap",
        "ten_year_four_pct_bond": {
            "price": p0,
            "effective_duration": float(duration),
            "effective_convexity": float(convexity),
            "duration_only_mae_across_shocks": mae_d,
            "duration_convexity_mae_across_shocks": mae_dc,
            "approximation_error_reduction_pct": float(reduction),
            "shock_results": shock_rows,
        },
        "five_year_swap": {
            "par_rate_pct": float(100 * par_swap_rate),
            "payer_swap_pv_change_for_plus_1bp_per_100_notional": float(swap_dv01),
        },
    }


def ml_volatility_analysis(con: sqlite3.Connection) -> dict[str, Any]:
    query = "SELECT date, adj_close, volume FROM asset_prices WHERE ticker='SPY' ORDER BY date"
    df = pd.read_sql_query(query, con, parse_dates=["date"]).set_index("date")
    px = df["adj_close"]
    r = px.pct_change()
    annual = math.sqrt(252.0)
    feat = pd.DataFrame(index=df.index)
    for w in [5, 10, 20, 60]:
        feat[f"rv{w}"] = r.rolling(w).std(ddof=0) * annual
    for w in [5, 20, 60]:
        feat[f"ret{w}"] = px.pct_change(w)
    feat["abs_ret1"] = r.abs()
    feat["neg_ret1"] = r.clip(upper=0.0)
    feat["vol_ratio_20_60"] = feat["rv20"] / feat["rv60"] - 1.0
    logv = np.log1p(df["volume"])
    feat["volume_z20"] = (logv - logv.rolling(20).mean()) / logv.rolling(20).std(ddof=0)
    feat["drawdown60"] = px / px.rolling(60).max() - 1.0
    target = r.rolling(20).std(ddof=0).shift(-20) * annual
    baseline = feat["rv20"]
    target_end = pd.Series(df.index, index=df.index).shift(-20)

    data = feat.copy()
    data["target"] = target
    data["baseline"] = baseline
    data["target_end"] = target_end
    data = data.dropna()
    features = [c for c in feat.columns]

    train_mask = data["target_end"] <= pd.Timestamp("2018-12-31")
    val_mask = (data.index >= pd.Timestamp("2019-01-01")) & (data["target_end"] <= pd.Timestamp("2021-12-31"))
    test_mask = data.index >= pd.Timestamp("2022-01-01")
    train, val, test = data.loc[train_mask], data.loc[val_mask], data.loc[test_mask]
    Xtr, ytr = train[features], train["target"]
    Xv, yv = val[features], val["target"]
    Xte, yte = test[features], test["target"]

    candidates: dict[str, Any] = {
        "linear": Pipeline([("scale", StandardScaler()), ("model", LinearRegression())]),
    }
    for a in [0.01, 0.1, 1.0, 10.0, 100.0]:
        candidates[f"ridge_{a:g}"] = Pipeline(
            [("scale", StandardScaler()), ("model", Ridge(alpha=a))]
        )
    for depth in [3, 6, None]:
        candidates[f"rf_depth_{depth}"] = RandomForestRegressor(
            n_estimators=250,
            max_depth=depth,
            min_samples_leaf=10,
            random_state=17,
            n_jobs=-1,
        )
    for depth in [2, 3]:
        for lr in [0.03, 0.05]:
            candidates[f"gbr_d{depth}_lr{lr}"] = GradientBoostingRegressor(
                n_estimators=250,
                learning_rate=lr,
                max_depth=depth,
                min_samples_leaf=10,
                random_state=17,
                loss="squared_error",
            )

    val_scores: dict[str, float] = {}
    fitted: dict[str, Any] = {}
    for name, model in candidates.items():
        model.fit(Xtr, ytr)
        pred = model.predict(Xv)
        val_scores[name] = float(mean_squared_error(yv, pred) ** 0.5)
        fitted[name] = model

    # Choose the best model within each major family on validation, then refit on train+validation.
    family_candidates = {
        "linear": ["linear"],
        "ridge": [n for n in candidates if n.startswith("ridge_")],
        "random_forest": [n for n in candidates if n.startswith("rf_")],
        "gradient_boosting": [n for n in candidates if n.startswith("gbr_")],
    }
    selected: dict[str, str] = {
        fam: min(names, key=lambda n: val_scores[n]) for fam, names in family_candidates.items()
    }
    trainval = pd.concat([train, val]).sort_index()
    Xtv, ytv = trainval[features], trainval["target"]
    test_metrics: dict[str, Any] = {
        "persistence": {
            "rmse": float(mean_squared_error(yte, test["baseline"]) ** 0.5),
            "mae": float(mean_absolute_error(yte, test["baseline"])),
            "r2": float(r2_score(yte, test["baseline"])),
        }
    }
    for family, selected_name in selected.items():
        model = candidates[selected_name]
        model.fit(Xtv, ytv)
        pred = model.predict(Xte)
        test_metrics[family] = {
            "selected_validation_spec": selected_name,
            "validation_rmse": val_scores[selected_name],
            "rmse": float(mean_squared_error(yte, pred) ** 0.5),
            "mae": float(mean_absolute_error(yte, pred)),
            "r2": float(r2_score(yte, pred)),
        }
    base_rmse = test_metrics["persistence"]["rmse"]
    best = min(test_metrics, key=lambda k: test_metrics[k]["rmse"])
    improvement = 100 * (base_rmse - test_metrics[best]["rmse"]) / base_rmse
    return {
        "target": "next-20-trading-day annualized SPY realized volatility",
        "features": features,
        "train_rows": int(len(train)),
        "validation_rows": int(len(val)),
        "test_rows": int(len(test)),
        "train_target_end_through": "2018-12-31",
        "validation_target_end_through": "2021-12-31",
        "test_start": str(test.index.min().date()),
        "test_end": str(test.index.max().date()),
        "test_metrics": test_metrics,
        "best_by_test_rmse": best,
        "rmse_reduction_vs_persistence_pct": float(improvement),
    }


def pca_analysis(con: sqlite3.Connection) -> dict[str, Any]:
    prices = prices_from_sql(con, SECTOR_TICKERS)
    r = prices.pct_change().dropna()

    def regime(start: str, end: str) -> dict[str, Any]:
        x = r.loc[start:end].dropna()
        corr = x.corr().to_numpy()
        eigvals, eigvecs = np.linalg.eigh(corr)
        order = np.argsort(eigvals)[::-1]
        eigvals = eigvals[order]
        eigvecs = eigvecs[:, order]
        explained = eigvals / eigvals.sum()
        pc1_loadings = {
            ticker: float(eigvecs[i, 0]) for i, ticker in enumerate(SECTOR_TICKERS)
        }
        return {
            "observations": int(len(x)),
            "pc1_variance_explained_pct": float(100 * explained[0]),
            "first_3_variance_explained_pct": float(100 * explained[:3].sum()),
            "pc1_loadings": pc1_loadings,
        }

    calm = regime("2018-01-01", "2019-12-31")
    covid = regime("2020-02-19", "2020-04-30")
    return {
        "universe": SECTOR_TICKERS,
        "method": "PCA of the 9x9 daily-return correlation matrix",
        "calm_2018_2019": calm,
        "covid_stress_2020_02_19_to_2020_04_30": covid,
        "pc1_increase_percentage_points": float(
            covid["pc1_variance_explained_pct"] - calm["pc1_variance_explained_pct"]
        ),
    }


def main(output: Path) -> None:
    market = download_market_data()
    rates = download_fred_rates()
    db_path = output.with_suffix(".sqlite")
    con, sql_summary = create_sqlite_pipeline(market, rates, db_path)
    try:
        risk, risk_garch = risk_analysis(con)
        results = {
            "metadata": {
                "generated_utc": pd.Timestamp.utcnow().isoformat(),
                "analysis_version": 1,
                "no_random_train_test_split": True,
            },
            "sql_data_pipeline": sql_summary,
            "market_risk": risk,
            "fixed_income": fixed_income_analysis(con),
            "time_series_volatility": time_series_volatility_analysis(con, risk_garch),
            "ml_volatility": ml_volatility_analysis(con),
            "pca_sector_risk": pca_analysis(con),
        }
    finally:
        con.close()
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("RESULT_JSON_BEGIN")
    print(json.dumps(results, indent=2))
    print("RESULT_JSON_END")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("resume_quant_results.json"))
    args = parser.parse_args()
    main(args.output)
