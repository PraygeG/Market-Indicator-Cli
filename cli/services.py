from data_sources.yfinance_source import YfinanceSource
from data_sources.alphavantage_source import AlphavantageSource
from indicators.EMA import EMA
from indicators.SMA import SMA
from indicators.RSI import RSI
from indicators.BBANDS import BBANDS
from indicators.MACD import MACD
from indicators.OBV import OBV
from indicators.ADX import ADX
from plots.plotter import Plotter
from plots.candlestick_plotter import CandlestickPlotter
import pandas as pd
import time

INDICATOR_CLASSES = {
    "EMA": EMA,
    "SMA": SMA,
    "RSI": RSI,
    "MACD": MACD,
    "BBANDS": BBANDS,
    "OBV": OBV,
    "ADX": ADX,
}


def fetch_all_data(
    tickers: list[str],
    start_date: str,
    end_date: str,
    interval: str,
    source: str,
    delay=1,
):
    if source == "yfinance":
        src = YfinanceSource()
    elif source == "alphavantage":
        src = AlphavantageSource()
    else:
        raise NotImplementedError("Only yfinance and alphavantage are supported")
    data_dict = {}
    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        data = src.fetch_data(ticker, start_date, end_date, interval)
        time.sleep(delay)
        data_dict[ticker] = data
    return data_dict


def run_indicators(
    data: dict[str, pd.DataFrame], indicators: list[tuple[str, list[int]]], column: str
) -> dict[str, tuple[pd.DataFrame | pd.Series, list[int]]]:
    calculated = {}
    for name, params in indicators:
        indicator_class = INDICATOR_CLASSES.get(name)
        if not indicator_class:
            continue
        if name == "OBV":
            indicator = indicator_class()
            calculated_series = indicator.calculate(data)
            calculated[name] = (calculated_series, params)
        elif name == "ADX":
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
    data,
    indicators,
    column: str,
    ticker,
    plot_style="line",
    color_scheme="default",
    up_color=None,
    down_color=None,
    save=False,
    save_dir=None,
    save_format="png",
    save_dpi=300,
    interval=None,
    start_date=None,
    end_date=None,
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
