import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from plots.plot_methods import (
    COLOR_SCHEMES,
    apply_color_scheme,
    plot_macd,
    plot_bbands,
    plot_rsi,
    plot_obv,
    plot_adx,
    analyze_indicators,
    assign_axes,
    save_plot,
)

class CandlestickPlotter:
    def __init__(
        self,
        title: str = "Stock Data with Indicators",
        color_scheme: str = "default",
        up_color: str = None,
        down_color: str = None,
    ):
        self.title = title
        self.scheme = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["default"]).copy()
        if up_color and up_color.lower() != "none":
            self.scheme["up"] = up_color
        if down_color and down_color.lower() != "none":
            self.scheme["down"] = down_color

    def plot(
        self,
        data: pd.DataFrame,
        indicators: dict,
        column: str = "Close",
        ticker: str = "Unknown",
        save: bool = False,
        save_dir: str = None,
        save_format: str = "png",
        save_dpi: int = 300,
        interval: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        required_columns = ["Open", "High", "Low", "Close"]
        if  not all(col in data.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain a OHLC columns for candlestick chart.")
        
        indicators_info = analyze_indicators(indicators)
        subplot_count = indicators_info["subplot_count"]

        fig, axes = plt.subplots(
            subplot_count,
            1,
            figsize=(12, 6, 2 * subplot_count),
            gridspec_kw={"height_ratios": [3] + [1] * (subplot_count - 1)},
        )
        if subplot_count == 1:
            axes = [axes]

        apply_color_scheme(fig, axes, self.scheme, self.title)
        fig.suptitle(f"{self.title} - {ticker}", color=self.scheme["text"])

        ax_map = assign_axes(axes, indicators_info)
        ax_price: Axes = ax_map["price"]
        ax_obv: Axes = ax_map["obv"]
        ax_macd: Axes = ax_map["macd"]
        ax_rsi: Axes = ax_map["rsi"]
        ax_adx: Axes = ax_map["adx"]