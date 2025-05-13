import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import pandas as pd
from stonkzilla.plots.plot_methods import (
    apply_color_scheme,
    resolve_color_scheme,
    create_indicator_subplots,
    plot_macd,
    plot_bbands,
    plot_rsi,
    plot_obv,
    plot_adx,
    plot_fibo,
    analyze_indicators,
    assign_axes,
    save_plot,
)


class Plotter:
    """
    Handles plotting of stock data and technical indicators using matplotlib.
    """

    def __init__(
        self,
        title: str = "Stock Data with Indicators",
        color_scheme: str = "default",
        up_color: str = None,
        down_color: str = None,
    ) -> None:
        """
        Initialize the Plotter with title and color scheme.
        """
        self.title = title
        self.scheme = resolve_color_scheme(color_scheme, up_color, down_color)

    def plot(
        self,
        data: pd.DataFrame,
        indicators: dict[str, tuple[pd.DataFrame | pd.Series, list[int]]],
        column: str = "Close",
        ticker: str = "Unknown",
        save: bool = False,
        save_dir: str = None,
        save_format: str = "png",
        save_dpi: int = 300,
        interval: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> None:
        """
        Plot the stock data and indicators. Optionally save or show interactively.
        """
        if column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{column}' column.")

        indicators_info = analyze_indicators(indicators)
        subplot_count = indicators_info["subplot_count"]

        fig, axes = create_indicator_subplots(subplot_count)

        apply_color_scheme(fig, axes, self.scheme, self.title)
        fig.suptitle(f"{self.title} - {ticker}", color=self.scheme["text"])

        ax_map = assign_axes(axes, indicators_info)
        ax_price: Axes = ax_map["price"]
        ax_obv: Axes = ax_map["obv"]
        ax_macd: Axes = ax_map["macd"]
        ax_rsi: Axes = ax_map["rsi"]
        ax_adx: Axes = ax_map["adx"]

        ax_price.plot(
            data.index,
            data[column],
            label=column,
            color=self.scheme["up"],
            linewidth=1.5,
        )
        for name, (series, _) in indicators.items():
            if (
                name.startswith("MACD")
                or name.startswith("RSI")
                or name.startswith("OBV")
                or name.startswith("BBANDS")
                or name.startswith("ADX")
                or name.startswith("FIBO")
            ):
                continue
            ax_price.plot(series.index, series, label=f"{name}", linewidth=1)
        if indicators_info["has_bbands"]:
            bbands_key = next(name for name in indicators if "BBANDS" in name)
            bbands_data, params = indicators[bbands_key]
            plot_bbands(ax_price, bbands_data, params, self.scheme)
        if indicators_info["has_fibo"]:
            fibo_key = next(name for name in indicators if name.startswith("FIBO"))
            fibo_data, _ = indicators[fibo_key]
            plot_fibo(ax_price, fibo_data, self.scheme)
        ax_price.set_label("Price")
        ax_price.legend()
        ax_price.grid(color=self.scheme.get("grid", None))

        if indicators_info["has_obv"]:
            obv_key = next(name for name in indicators if name.startswith("OBV"))
            obv_data, _ = indicators[obv_key]
            plot_obv(ax_obv, obv_data, self.scheme)

        if indicators_info["has_macd"]:
            macd_key = next(name for name in indicators if "MACD" in name)
            macd_data, _ = indicators[macd_key]
            plot_macd(ax_macd, macd_data, self.scheme)

        if indicators_info["has_rsi"]:
            rsi_key = next(name for name in indicators if name.startswith("RSI"))
            rsi_data, params = indicators[rsi_key]
            plot_rsi(ax_rsi, rsi_data, params, self.scheme)

        if indicators_info["has_adx"]:
            adx_key = next(name for name in indicators if name.startswith("ADX"))
            adx_data, _ = indicators[adx_key]
            plot_adx(ax_adx, adx_data, self.scheme)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save plots to file
        if save:
            save_plot(
                fig,
                save_dir,
                save_format,
                save_dpi,
                ticker,
                interval,
                start_date,
                end_date,
            )
        else:
            plt.show()
