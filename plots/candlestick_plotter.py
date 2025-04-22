import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from plots.base_plotter import BasePlotter
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from datetime import datetime


class CandlestickPlotter(BasePlotter):
    """Plotter for candlestick charts with customizable color schemes"""

    COLOR_SCHEMES = {
        "default": {"up": "green", "down": "red"},
        "monochrome": {"up": "black", "down": "gray"},
        "tradingview": {"up": "#26a69a", "down": "#ef5350"},
        "dark": {
            "up": "#CAF50",
            "down": "#FF5252",
            "bg": "#121212",
            "text": "white",
            "grid": "#333333",
        },
    }

    def __init__(
        self,
        title: str = "Stock Dat with Indicators",
        color_scheme: str = "default",
        up_color: str = None,
        down_color: str = None,
    ):
        super().__init__(title)
        self.color_scheme = color_scheme

        if color_scheme in self.COLOR_SCHEMES:
            self.scheme = self.COLOR_SCHEMES[color_scheme].copy()
        else:
            self.scheme = self.COLOR_SCHEMES["default"].copy()

        if up_color:
            self.scheme["up"] = up_color
        if down_color:
            self.scheme["down"] = down_color

    def plot(
        self,
        data: pd.DataFrame,
        indicators: dict,
        column: str = "Close",
        company_name: str = "Unknown",
    ):
        required_columns = ["Open", "High", "Low", "Close"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError(
                f"DataFrame must contain OHLC columns for candlestick chart."
            )

        has_macd = any("MACD" in name for name in indicators)
        has_bbands = any("BBANDS" in name for name in indicators)
        has_rsi = any(name.startswith("RSI") for name in indicators)
        has_obv = any(name.startswith("OBV") for name in indicators)
        subplot_count = 1 + has_macd + has_bbands + has_rsi + has_obv

        fig: Figure
        axes: Axes | list[Axes]

        fig, axes = plt.subplot(
            subplot_count,
            1,
            figsize=(12, 6 + 2 * subplot_count),
            gridspec_kw={"height_ratios": [3] + [1] * (subplot_count - 1)},
        )
        if subplot_count == 1:
            axes = [axes]

        # Apply dark theme if selected
        if "bg" in self.scheme:
            fig.patch.set_facecolor(self.scheme["bg"])
            for ax in axes:
                ax: Axes
                ax.set_facecolor(self.scheme["bg"])
                ax.spines["bottom"].set_color(self.scheme["text"])
                ax.spines["top"].set_color(self.scheme["text"])
                ax.spines["right"].set_color(self.scheme["text"])
                ax.spines["left"].set_color(self.scheme["text"])
                ax.tick_params(colors=self.scheme["text"])
                ax.xaxis.label.set_color(self.scheme["text"])
                ax.yaxis.label.set_color(self.scheme["text"])
                ax.title.set_color(self.scheme["text"])
            fig.suptitle(f"{self.title} - {company_name}", color=self.scheme["text"])
        else:
            fig.suptitle(f"{self.title} - {company_name}")

        ax_price = axes[0]
        current_index = 1
        ax_macd = axes[current_index] if has_macd else None
        if has_macd:
            current_index += 1
        ax_bbands = axes[current_index] if has_bbands else None
        if has_bbands:
            current_index += 1
        ax_rsi = axes[current_index] if has_rsi else None
        if has_rsi:
            current_index += 1
        ax_obv = axes[current_index] if has_obv else None

        self._plot_candlesticks(ax_price, data)

        for name, (series, params) in indicators.items():
            if (
                name.startswith("MACD")
                or name.startswith("BBANDS")
                or name.startswith("RSI")
                or name.startswith("OBV")
            ):
                continue
            ax_price.plot(series.index, series, label=f"{name} {params}", linewidth=1.5)

        ax_price.set_ylabel("Price")
        ax_price.legend()
        ax_price.grid(color=self.scheme.get("grid", None))
        if len(data) > 50:
            ax_price.xaxis.set_major_locator(mdates.AutoDateLocator())

        if has_macd:
            macd_key = next(name for name in indicators if "MACD" in name)
            macd_data, params = indicators[macd_key]
            macd_line = macd_data["MACD"]
            signal_line = macd_data["Signal"]
            histogram = macd_line - signal_line
            ax_macd.plot(
                macd_data.index,
                macd_line,
                label="MACD Line",
                color="orange",
                linewidth=1.2,
            )
            ax_macd.plot(
                macd_data.index,
                signal_line,
                label="Signal Line",
                color="green",
                linewidth=1.2,
            )
            colors = [
                self.scheme["up"] if value > 0 else self.scheme["down"]
                for value in histogram
            ]
            ax_macd.bar(
                macd_data.index,
                histogram,
                label="Histogram",
                color=colors,
                alpha=0.7,
                width=1,
            )
            ax_macd.axhline(0, color="gray", linestyle="--", linewidth=0.8)
            ax_macd.set_ylabel("MACD")
            ax_macd.legend()
            ax_macd.grid(color=self.scheme.get("grid", None))
        if has_bbands:
            bbands_key = next(name for name in indicators if "BBANDS" in name)
            bbands_data, params = indicators[bbands_key]
            upper_band = bbands_data["upper_band"]
            lower_band = bbands_data["lower_band"]
            middle_band = bbands_data["middle_band"]
            ax_bbands.plot(
                bbands_data.index,
                middle_band,
                label="Middle Band",
                color="blue",
                linewidth=1.2,
            )
            ax_bbands.plot(
                bbands_data.index,
                upper_band,
                label="Upper Band",
                color="red",
                linestyle="--",
                linewidth=1.2,
            )
            ax_bbands.plot(
                bbands_data.index,
                lower_band,
                label="Lower Band",
                color="green",
                linestyle="--",
                linewidth=1.2,
            )
            ax_bbands.fill_between(
                bbands_data.index, lower_band, upper_band, color="grey", alpha=0.3
            )
            ax_bbands.set_ylabel("BBANDS")
            ax_bbands.legend()
            ax_bbands.grid(color=self.scheme.get("grid", None))
        if has_rsi:
            rsi_key = next(name for name in indicators if name.startswith("RSI"))
            rsi_data, params = indicators[rsi_key]
            ax_rsi.plot(
                rsi_data.index,
                rsi_data,
                label=f"RSI {params}",
                color="purple",
                linewidth=1.2,
            )
            ax_rsi.axhline(
                70, color="red", linestyle="--", linewidth=0.8, label="Overbought"
            )
            ax_rsi.axhline(
                30, color="green", linestyle="--", linewidth=0.8, label="Oversold"
            )
            ax_rsi.set_ylabel("RSI")
            ax_rsi.legend()
            ax_rsi.grid("grid", None)
        if has_obv:
            obv_key = next(name for name in indicators if name.startswith("OBV"))
            obv_data, _ = indicators[obv_key]
            ax_obv.plot(
                obv_data.index,
                obv_data,
                label="On balance volume",
                color="green",
                linewidth=1,
            )
            ax_obv.set_ylabel("OBV")
            ax_obv.legend()
            ax_obv.grid(color=self.scheme.get("grid", None))

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    def _plot_candlesticks(self, ax: Axes, data: pd.DataFrame):
        """Draw candlesticks on the given axis"""
        width = 0.6

        for i, (date, row) in enumerate(data.iterrows()):
            if row["Close"] >= row["Open"]:
                color = self.scheme["up"]
                body_bottom = row["Open"]
                body_height = row["Close"] - row["Open"]
            else:
                color = self.scheme["down"]
                body_bottom = row["Close"]
                body_height = row["Open"] - row["Close"]

            rect = Rectangle(
                xy=(i - width / 2, body_bottom),
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
                [i, i],
                [max(row["Open"], row["Close"]), row["High"]],
                color="black",
                linewidth=0.8,
            )

            # Plot the lower wick
            ax.plot(
                [i, i],
                [max(row["Open"], row["Close"]), row["Low"]],
                color="black",
                linewidth=0.8,
            )

        if len(data) <= 50:
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(
                [date.date() for date in data.index], rotation=45, ha="right"
            )
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_locator(mdates.DateFormatter("%Y-%m-%d"))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        price_range = data["High"].max() - data["Low"].min()
        margin = price_range * 0.05
        ax.set_ylim(data["Low"].min() - margin, data["High"].max() + margin)
