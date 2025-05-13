"""Click options wrapper module"""

from typing import Callable, TypeVar, ParamSpec
import click

P = ParamSpec("P")
R = TypeVar("R")


def tickers_option(f: Callable[P, R]) -> Callable[P, R]:
    return click.option(
        "--tickers",
        "--t",
        default=None,
        help="Comma-separated list of tickers (e.g., AAPL, MSFT)",
    )(f)


def date_range_options(f: Callable[P, R]) -> Callable[P, R]:
    """Date range options."""
    f = click.option(
        "--start-date", "--start", default=None, help="Start date (YYYY-MM-DD)"
    )(f)
    f = click.option("--end-date", "--end", default=None, help="End date (YYYY-MM-DD)")(
        f
    )
    return f


def interval_option(f: Callable[P, R]) -> Callable[P, R]:
    return click.option(
        "--interval",
        default=None,
        help="""Interval in which data is downloaded. 
Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo Intraday data cannot extend last 60 days.""",
    )(f)


def indicator_option(f: Callable[P, R]) -> Callable[P, R]:
    return click.option(
        "--indicators",
        default=None,
        help="Comma-separated list of indicators (e.g., RSI:14,EMA:50,SMA:100,MACD:12-26-9)",
    )(f)


def data_source_option(f: Callable[P, R]) -> Callable[P, R]:
    return click.option(
        "--data-source",
        "--source",
        type=click.Choice(["yfinance", "alphavantage"]),
        default="yfinance",
        help="Data source to use (default: yfinance)",
    )(f)


def api_key_option(f: Callable[P, R]) -> Callable[P, R]:
    return click.option(
        "--api-key", default=None, help="API key for AlphaVantage data source"
    )(f)


def column_option(f: Callable[P, R]) -> Callable[P, R]:
    return click.option(
        "--column", default="Close", help="Column to use for calculations"
    )(f)


def plot_options(f: Callable[P, R]) -> Callable[P, R]:
    """Plot style and color scheme options."""
    f = click.option(
        "--plot-style",
        default="line",
        type=click.Choice(["line", "candlestick"]),
        help="Chart visualization style (default: line)",
    )(f)
    f = click.option(
        "--color-scheme",
        default="default",
        type=click.Choice(["default", "monochrome", "tradingview", "dark"]),
        help="Color scheme for the chart (default: default)",
    )(f)
    f = click.option(
        "--up-color",
        default=None,
        help="Custom color for up candles/bars (overrides color scheme)",
    )(f)
    f = click.option(
        "--down-color",
        default=None,
        help="Custom color for down candles/bars (overrides color scheme)",
    )(f)
    f = click.option(
        "--interactive",
        is_flag=True,
        help="Enable interactive plot.",
    )(f)
    return f


def multi_plot_options(f: Callable[P, R]) -> Callable[P, R]:
    """
    Enable plotting multiple tickers on the same chart,
    plus normalization and log scale optionally for better readiness
    """
    f = click.option(
        "--multi-plot",
        "--multi",
        is_flag=True,
        help="Plot all the tickers on the same plot.",
    )(f)
    f = click.option(
        "--normalize", is_flag=True, help="Normalize the data for multi plot."
    )(f)
    f = click.option(
        "--log-scale", is_flag=True, help="Use logharithmic scale for multi plot."
    )(f)
    return f


def save_options(f: Callable[P, R]) -> Callable[P, R]:
    """
    Save plots in a given directory, format and dpi for raster formats
    instead of showing, good for running plots at scale.
    """
    f = click.option(
        "--save", is_flag=True, help="Save the plot(s) to file automatically. "
    )(f)
    f = click.option("--save-dir", default=None, help="Directory to save plots")(f)
    f = click.option(
        "--save-format",
        "--format",
        default="png",
        type=click.Choice(["png", "pdf", "svg", "jpg"]),
        help="Format to save (png, pdf, svg, jpg)",
    )(f)
    f = click.option(
        "--save-dpi", "--dpi", default=None, type=int, help="DPI for raster formats"
    )(f)
    return f


def common_options(f):
    """Options wrapper"""
    f = tickers_option(f)
    f = date_range_options(f)
    f = interval_option(f)
    f = indicator_option(f)
    f = data_source_option(f)
    f = api_key_option(f)
    f = column_option(f)
    f = plot_options(f)
    f = multi_plot_options(f)
    f = save_options(f)
    return f
