import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.axes import Axes
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


class CandlestickPlotter:
    def __init__(
        self,
        title: str = "Stock Data with Indicators",
        color_scheme: str = "default",
        up_color: str = None,
        down_color: str = None,
    ) -> None:
        self.title = title
        self.scheme = resolve_color_scheme(color_scheme, up_color, down_color)

    def _plot_candlesticks(self, ax: Axes, data: pd.DataFrame) -> None:
        """Draw candlesticks on the given axis"""
        data = data.sort_index()
        date_nums = [mdates.date2num(d) for d in data.index]
        if len(data) > 1:
            diffs = [b - a for a, b in zip(date_nums[:-1], date_nums[1:])]
            import numpy as np

            median_diff = np.median(diffs)
            width = median_diff * 0.7
        else:
            width = 0.6

        for date, row in data.iterrows():
            x = mdates.date2num(date)
            close_value = (
                row["Close"].item() if hasattr(row["Close"], "item") else row["Close"]
            )
            open_value = (
                row["Open"].item() if hasattr(row["Open"], "item") else row["Open"]
            )
            high_value = (
                row["High"].item() if hasattr(row["High"], "item") else row["High"]
            )
            low_value = row["Low"].item() if hasattr(row["Low"], "item") else row["Low"]

            if close_value >= open_value:
                color = self.scheme["up"]
                body_bottom = open_value
                body_height = close_value - open_value
            else:
                color = self.scheme["down"]
                body_bottom = close_value
                body_height = open_value - close_value

            rect = Rectangle(
                xy=(x - width / 2, body_bottom),
                width=width,
                height=body_height,
                facecolor=color,
                edgecolor="black",
                linewidth=0.5,
                alpha=0.8,
            )
            ax.add_patch(rect)

            # Plot the upper wick
            ax.plot(
                [x, x],
                [max(open_value, close_value), high_value],
                color="black",
                linewidth=0.8,
            )

            # Plot the lower wick
            ax.plot(
                [x, x],
                [min(open_value, close_value), low_value],
                color="black",
                linewidth=0.8,
            )
        ax.set_xlim(
            mdates.date2num(data.index.min()) - 1, mdates.date2num(data.index.max()) + 1
        )
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.AutoDateFormatter("%Y-%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        price_range = data["High"].max().item() - data["Low"].min().item()
        margin = price_range * 0.05
        ax.set_ylim(
            data["Low"].min().item() - margin, data["High"].max().item() + margin
        )

    def plot(
        self,
        data: pd.DataFrame,
        indicators: dict[str, tuple[pd.DataFrame | pd.Series, list[int]]],
        _,
        ticker: str = "Unknown",
        save: bool = False,
        save_dir: str = None,
        save_format: str = "png",
        save_dpi: int = 300,
        interval: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> None:
        required_columns = ["Open", "High", "Low", "Close"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError(
                "DataFrame must contain a OHLC columns for candlestick chart."
            )

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

        self._plot_candlesticks(ax_price, data)

        for name, (series, _) in indicators.items():
            if (
                name.startswith("MACD")
                or name.startswith("BBANDS")
                or name.startswith("RSI")
                or name.startswith("OBV")
                or name.startswith("FIBO")
                or name.startswith("ADX")
            ):
                continue
            ax_price.plot(series.index, series, label=f"{name}", linewidth=1.5)
        if indicators_info["has_bbands"]:
            bbands_key = next(name for name in indicators if "BBANDS" in name)
            bbands_data, _ = indicators[bbands_key]
            plot_bbands(ax_price, bbands_data, self.scheme)
        if indicators_info["has_fibo"]:
            fibo_key = next(name for name in indicators if name.startswith("FIBO"))
            fibo_data, _ = indicators[fibo_key]
            plot_fibo(ax_price, fibo_data, self.scheme)
        ax_price.set_ylabel("Price")
        ax_price.legend()
        ax_price.grid(color=self.scheme.get("grid", None))

        if len(data) > 50:
            ax_price.xaxis.set_major_locator(mdates.AutoDateLocator())

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
            adx_data, params = indicators[adx_key]
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
