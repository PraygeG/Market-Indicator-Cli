from typing import Optional
import time
import pandas as pd
from stonkzilla.data_sources.yfinance import YfinanceSource
from stonkzilla.data_sources.alphavantage import AlphavantageSource
from stonkzilla.indicators.ema import EMA
from stonkzilla.indicators.sma import SMA
from stonkzilla.indicators.rsi import RSI
from stonkzilla.indicators.bbands import BBANDS
from stonkzilla.indicators.macd import MACD
from stonkzilla.indicators.obv import OBV
from stonkzilla.indicators.adx import ADX
from stonkzilla.indicators.fibonacci_retracement import FibonacciRetracement as FIBO
from stonkzilla.plots.plotter import Plotter
from stonkzilla.plots.candlestick_plotter import CandlestickPlotter
from stonkzilla.plots.multi_plotter import MultiTickerPlotter

INDICATOR_CLASSES = {
    "EMA": EMA,
    "SMA": SMA,
    "RSI": RSI,
    "MACD": MACD,
    "BBANDS": BBANDS,
    "OBV": OBV,
    "ADX": ADX,
    "FIBO": FIBO,
}


def fetch_all_data(
    tickers: list[str],
    start_date: str,
    end_date: str,
    interval: str,
    source: str,
    delay=1,
    api_key: str = None,
) -> dict[str, pd.DataFrame]:
    if source == "yfinance":
        src = YfinanceSource()
    elif source == "alphavantage":
        src = AlphavantageSource(api_key=api_key)
    else:
        raise NotImplementedError("Only yfinance and alphavantage are supported")
    data_dict = {}
    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        data = src.fetch_data(ticker, start_date, end_date, interval)
        time.sleep(delay)
        data_dict[ticker] = data
    return data_dict


def run_multi_ticker_indicators(
    ticker_data: dict[str, pd.DataFrame],
    indicators: list[tuple[str, list[int | float]]],
    column: str = "Close",
    normalize: bool = False,
) -> dict[str, tuple[pd.DataFrame | pd.Series, Optional[list[int]]]]:
    """
    Calculate indicators for multi-ticker plotting.
    FIBO is only calculated and included if normalize=True.
    """
    calculated = {}
    filtered_indicators = []
    for name, params in indicators:
        if name == "FIBO" and not normalize:
            continue
        filtered_indicators.append((name, params))
    for name, params in indicators:
        indicator_class = INDICATOR_CLASSES.get(name)
        if not indicator_class:
            continue
        if name in ("SMA", "EMA"):
            result_df = pd.DataFrame()
            for ticker, data in ticker_data.items():
                indicator = indicator_class(*params, column=column)
                series = indicator.calculate(data)
                if isinstance(series, pd.Series):
                    result_df[ticker] = series
                elif isinstance(series, pd.DataFrame):
                    series = series.add_prefix(f"{ticker}_")
                    result_df = pd.concat([result_df, series], axis=1)
                else:
                    raise TypeError(
                        f"Unexpected output type from {name}: {type(series)}"
                    )
            calculated[f"{name}_{"_".join(map(str, params))}"] = (result_df, params)
        elif name == "FIBO":
            fibo_dfs = []
            for ticker, data in ticker_data.items():
                indicator = indicator_class(*params)
                fibo_df = indicator.calculate(data)
                # fibo_df: index = dates, columns = fib levels
                # Take the first row (or last, or mean) for each ticker
                # Here, take the first row (earliest date)
                fibo_levels = fibo_df.iloc[0]
                fibo_levels.name = ticker
                fibo_dfs.append(fibo_levels)
            if fibo_dfs:
                all_levels = pd.concat(fibo_dfs, axis=1)
                calculated[f"{name}_{'_'.join(map(str, params))}"] = (
                    all_levels,
                    params,
                )
    return calculated


def run_indicators(
    data: pd.DataFrame, indicators: list[tuple[str, list[int | float]]], column: str
) -> dict[str, tuple[pd.DataFrame | pd.Series, Optional[list[int]]]]:
    calculated = {}
    for name, params in indicators:
        indicator_class = INDICATOR_CLASSES.get(name)
        if not indicator_class:
            continue
        if name == "OBV":
            indicator = indicator_class(name)
            calculated_series = indicator.calculate(data)
            calculated[name] = (calculated_series, params)
        elif name in ("ADX", "FIBO"):
            indicator = indicator_class(*params)
            calculated_series = indicator.calculate(data)
            calculated[f"{name}_{'_'.join(map(str, params))}"] = (
                calculated_series,
                params,
            )
        else:
            indicator = indicator_class(*params, column=column)
            calculated_series = indicator.calculate(data)
            calculated[f"{name}_{'_'.join(map(str, params))}"] = (
                calculated_series,
                params,
            )
    return calculated


def plot_data(
    data: dict[str, pd.DataFrame],
    indicators: dict[str, tuple[pd.DataFrame | pd.Series, list[int]]],
    column: str,
    ticker: str,
    plot_style="line",
    color_scheme="default",
    up_color: str = None,
    down_color: str = None,
    save: bool = False,
    save_dir: str = None,
    save_format: str = "png",
    save_dpi: int = 300,
    interval: str = None,
    start_date: str = None,
    end_date: str = None,
):
    title = f"Stock analysis for {ticker}"
    if plot_style == "candlestick":
        plotter = CandlestickPlotter(
            title=title,
            color_scheme=color_scheme,
            up_color=up_color,
            down_color=down_color,
        )
    else:
        plotter = Plotter(
            title=title,
            color_scheme=color_scheme,
            up_color=up_color,
            down_color=down_color,
        )
    plotter.plot(
        data,
        indicators,
        column,
        ticker,
        save=save,
        save_dir=save_dir,
        save_format=save_format,
        save_dpi=save_dpi,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
    )


def plot_multi(
    data: dict[str, pd.DataFrame],
    indicators: dict[str, tuple[pd.DataFrame | pd.Series, list[int]]],
    column: str,
    save: bool,
    save_dir: str,
    save_format: str,
    save_dpi: int,
    normalize: bool,
    log_scale: bool,
) -> None:
    plotter = MultiTickerPlotter(
        normalize=normalize,
        log_scale=log_scale,
    )
    plotter.plot(
        data,
        indicators,
        column,
        save,
        save_dir,
        save_format,
        save_dpi,
    )
