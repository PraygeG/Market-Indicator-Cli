import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from plots.base_plotter import BasePlotter
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class CandlestickPlotter(BasePlotter):
    """Plotter for candlestick charts with customizable color schemes"""

    COLOR_SCHEMES = {
        "default": {
            "up": "green",
            "down": "red",
            "bg": "white",
            "text": "black",
            "grid": "#cccccc",
        },
        "monochrome": {"up": "black", "down": "gray", "bg": "white", "grid": "#cccccc"},
        "tradingview": {
            "up": "#26a69a",
            "down": "#ef5350",
            "bg": "white",
            "text": "black",
            "grid": "#e0e3eb",
        },
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

        fig, axes = plt.subplots(
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
        grid_color = self.scheme.get("grid", None)
        if grid_color is not None:
            ax_price.grid(color=grid_color)
        else:
            ax_price.grid()
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
            ax_rsi.grid(color=self.scheme.get("grid", None))
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
        data = data.sort_index()
        if len(data) > 1:
            date_nums = [mdates.date2num(d) for d in data.index]
            min_diff = min([b - a for a,b in zip(date_nums[:-1], date_nums[1:])])
            width = min_diff * 0.7
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
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        price_range = data["High"].max().item() - data["Low"].min().item()
        margin = price_range * 0.05
        ax.set_ylim(
            data["Low"].min().item() - margin, data["High"].max().item() + margin
        )
