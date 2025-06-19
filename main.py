import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf

# Constants for file paths
CONFIG_PATH = "config.json"
SECTORS_PATH = "sectors.json"
RESULTS_DIR = "results"
RESULTS_PATH = os.path.join(RESULTS_DIR, "backtest_results.csv")
TOP_RESULTS_PATH = os.path.join(RESULTS_DIR, "top_strategies.csv")

def load_config(path):
    with open(path, "r") as f:
        config = json.load(f)
    # Set today's date dynamically as end_date
    config["end_date"] = datetime.today().strftime("%Y-%m-%d")
    return config

def load_sectors(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def fetch_data(symbol, start, end, interval="1d", alpaca_config=None):
    # Try Alpaca first
    if alpaca_config and alpaca_config.get("API_KEY") and alpaca_config.get("API_SECRET"):
        try:
            base_url = alpaca_config.get("BASE_URL", "https://data.alpaca.markets/v2")
            headers = {
                "APCA-API-KEY-ID": alpaca_config["API_KEY"],
                "APCA-API-SECRET-KEY": alpaca_config["API_SECRET"]
            }
            params = {
                "start": f"{start}T00:00:00Z",
                "end": f"{end}T23:59:59Z",
                "timeframe": "1Day",
                "adjustment": "all",
                "limit": 10000
            }
            url = f"{base_url}/stocks/{symbol}/bars"
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            bars = resp.json().get("bars", [])
            if not bars:
                raise ValueError(f"No data returned from Alpaca for {symbol}")
            df = pd.DataFrame(bars)
            df.rename(columns={
                "t": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"
            }, inplace=True)
            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            return df
        except Exception as e:
            print(f"[WARN] Alpaca fetch failed for {symbol}: {e}. Falling back to yfinance.")
    # Fallback: yfinance
    try:
        df = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
        if df.empty:
            raise ValueError(f"No data returned for {symbol} from yfinance")
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"[ERROR] yfinance failed for {symbol}: {e}")
        return pd.DataFrame()

def add_indicators(df, sma_periods, rsi_period, need_sma_100=False):
    for period in set(sma_periods + ([100] if need_sma_100 else [])):
        df[f"SMA_{period}"] = df["Close"].rolling(window=period).mean()
    # RSI
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=rsi_period).mean()
    avg_loss = pd.Series(loss).rolling(window=rsi_period).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df[f"RSI_{rsi_period}"] = 100 - (100 / (1 + rs))
    # 20-day average volume
    df["VOL_MA20"] = df["Volume"].rolling(window=20).mean()
    return df

def backtest_strategy(
    df, sma_fast, sma_slow, rsi_period, rsi_oversold, rsi_overbought, sl_pct, tp_pct, initial_equity,
    volume_filter=False, trend_filter=False
):
    sma_periods = [sma_fast, sma_slow]
    need_sma_100 = trend_filter
    df = add_indicators(df.copy(), sma_periods, rsi_period, need_sma_100=need_sma_100)
    trades = []
    entry_price, sl_price, tp_price, entry_idx = None, None, None, None
    stats = {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0, "returns": [], "max_drawdown": 0.0}
    equity = initial_equity
    peak_equity = equity

    min_idx = max(sma_fast, sma_slow, rsi_period, 100 if trend_filter else 0, 20 if volume_filter else 0)
    for i in range(min_idx, len(df)):
        row, prev_row = df.iloc[i], df.iloc[i-1]
        skip_entry = False
        if entry_price is None:
            if volume_filter and row["Volume"] < row["VOL_MA20"]:
                skip_entry = True
            if trend_filter and row["Close"] < row.get("SMA_100", np.nan):
                skip_entry = True
        sma_fast_now = row[f"SMA_{sma_fast}"]
        sma_slow_now = row[f"SMA_{sma_slow}"]
        rsi_now = row[f"RSI_{rsi_period}"]
        if entry_price is None and not skip_entry:
            if (
                prev_row[f"SMA_{sma_fast}"] < prev_row[f"SMA_{sma_slow}"]
                and sma_fast_now > sma_slow_now
                and rsi_now > rsi_oversold
            ):
                entry_price = row["Close"]
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                entry_idx = i
        else:
            low, high = row["Low"], row["High"]
            exit_price, exit_reason = None, None
            if low <= sl_price:
                exit_price, exit_reason = sl_price, "SL"
            elif high >= tp_price:
                exit_price, exit_reason = tp_price, "TP"
            elif prev_row[f"SMA_{sma_fast}"] > prev_row[f"SMA_{sma_slow}"] and sma_fast_now < sma_slow_now:
                exit_price, exit_reason = row["Close"], "CrossExit"
            if exit_price is not None:
                ret = (exit_price - entry_price) / entry_price
                equity *= (1 + ret)
                stats["returns"].append(ret)
                stats["trades"] += 1
                if ret > 0:
                    stats["wins"] += 1
                else:
                    stats["losses"] += 1
                stats["profit"] += ret
                trades.append({"entry": entry_price, "exit": exit_price, "ret": ret, "reason": exit_reason, "entry_idx": entry_idx, "exit_idx": i})
                entry_price, sl_price, tp_price, entry_idx = None, None, None, None
                if equity > peak_equity:
                    peak_equity = equity
                drawdown = (peak_equity - equity) / peak_equity
                stats["max_drawdown"] = max(stats["max_drawdown"], drawdown)

    if stats["returns"]:
        mean_return = np.mean(stats["returns"])
        std_return = np.std(stats["returns"])
        sharpe = (mean_return / (std_return + 1e-10)) * np.sqrt(252)
        profit_factor = -np.sum([r for r in stats["returns"] if r < 0]) / (np.sum([r for r in stats["returns"] if r > 0]) + 1e-10)
        win_rate = stats["wins"] / stats["trades"] if stats["trades"] > 0 else 0
    else:
        sharpe = 0
        profit_factor = 0
        win_rate = 0

    stats.update({
        "sharpe": sharpe,
        "profit_factor": profit_factor,
        "win_rate": win_rate,
        "final_equity": equity
    })
    return stats

def run_batch(config, symbols):
    results = []
    sma_fast_list = config["sma_fast"]
    sma_slow_list = config["sma_slow"]
    rsi_period = config["rsi_period"]
    rsi_oversold_list = config["rsi_oversold"]
    rsi_overbought_list = config["rsi_overbought"]
    stop_loss_list = config["stop_loss_pct"]
    take_profit_list = config["take_profit_pct"]
    initial_equity = config.get("initial_equity", 1000)
    start_date = config["start_date"]
    end_date = config["end_date"]
    interval = config.get("interval", "1d")
    volume_filter = config.get("volume_filter", False)
    trend_filter = config.get("trend_filter", False)
    alpaca_config = config.get("alpaca", None)

    for symbol in symbols:
        try:
            df = fetch_data(symbol, start_date, end_date, interval, alpaca_config)
            if df.empty:
                print(f"[WARN] No data for {symbol}, skipping.")
                continue
            for sma_fast in sma_fast_list:
                for sma_slow in sma_slow_list:
                    if sma_fast >= sma_slow:
                        continue
                    for sl_pct in stop_loss_list:
                        for tp_pct in take_profit_list:
                            for rsi_oversold in rsi_oversold_list:
                                for rsi_overbought in rsi_overbought_list:
                                    params = {
                                        "sma_fast": sma_fast,
                                        "sma_slow": sma_slow,
                                        "rsi_period": rsi_period,
                                        "rsi_oversold": rsi_oversold,
                                        "rsi_overbought": rsi_overbought,
                                        "sl_pct": sl_pct,
                                        "tp_pct": tp_pct,
                                        "initial_equity": initial_equity,
                                        "volume_filter": volume_filter,
                                        "trend_filter": trend_filter
                                    }
                                    stats = backtest_strategy(df, **params)
                                    result_row = {
                                        "symbol": symbol,
                                        **params,
                                        **stats
                                    }
                                    results.append(result_row)
        except Exception as e:
            print(f"[ERROR] Exception for {symbol}: {e}")
    return pd.DataFrame(results)

def score_and_filter_results(df, outpath, sector=None):
    df = df.copy()
    df["strategy_score"] = (df["sharpe"] * 2) + (df["win_rate"] * 100) + df["profit_factor"]
    filtered = df[
        (df["trades"] >= 10) &
        (df["sharpe"] >= 1.0) &
        (df["win_rate"] >= 0.55) &
        (df["profit_factor"] >= 1.5)
    ].copy()
    filtered.sort_values(by="strategy_score", ascending=False, inplace=True)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    filtered.to_csv(outpath, index=False)
    if sector:
        print(f"\n[RESULT] Top strategies for sector '{sector}' exported to {outpath}")
    else:
        print(f"\n[RESULT] Top strategies exported to {outpath}")
    print(f"\n[SUMMARY] Top 5 Strategies{' for ' + sector if sector else ''}:")
    if not filtered.empty:
        print(filtered.head(5).to_string(index=False))
    else:
        print("No strategies passed the filter criteria.")

def export_results(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[RESULT] Results exported to {path}")

def main():
    config = load_config(CONFIG_PATH)

    # Set today's date as dynamic end_date
    config["end_date"] = datetime.today().strftime('%Y-%m-%d')

    # Check if sectors.json exists
    if os.path.isfile(SECTORS_PATH):
        sectors = load_sectors(SECTORS_PATH)
        all_results = []
        for sector, symbols in sectors.items():
            print(f"\n=== Running backtest for sector: {sector} ===")
            sector_results_df = run_batch(config, symbols)
            sector_results_path = f"results/{sector}_backtest_results.csv"
            export_results(sector_results_df, sector_results_path)
            top_sector_path = f"results/top_strategies_{sector}.csv"
            score_and_filter_results(sector_results_df, top_sector_path, sector=sector)
            all_results.append(sector_results_df.assign(sector=sector))
        combined_results = pd.concat(all_results, ignore_index=True)
        export_results(combined_results, RESULTS_PATH)
        score_and_filter_results(combined_results, TOP_RESULTS_PATH)
    else:
        print("No sectors.json found, running on config['symbols']")
        results_df = run_batch(config, config["symbols"])
        export_results(results_df, RESULTS_PATH)
        score_and_filter_results(results_df, TOP_RESULTS_PATH)

if __name__ == "__main__":
    main()
