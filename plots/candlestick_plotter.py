import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from plots.base_plotter import BasePlotter
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class CandlestickPlotter(BasePlotter):
    """Plotter for candlestick charts with customizable color schemes"""

    def __init__(
        self,
        title: str = "Stock Data with Indicators",
        color_scheme: str = "default",
        up_color: str = None,
        down_color: str = None,
    ):
        super().__init__(title, color_scheme, up_color, down_color)

    def plot(
        self,
        data: pd.DataFrame,
        indicators: dict,
        column: str = "Close",
        company_name: str = "Unknown",
        save: bool = False,
        save_dir: str = None,
        save_format: str = "png",
        save_dpi: int = 300,
        interval: str = None,
        start_date: str = None,
        end_date: str = None,
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
            self.plot_macd(ax_macd, macd_data, params)
        if has_bbands:
            bbands_key = next(name for name in indicators if "BBANDS" in name)
            bbands_data, params = indicators[bbands_key]
            self.plot_bbands(ax_bbands, bbands_data, params)
        if has_rsi:
            rsi_key = next(name for name in indicators if name.startswith("RSI"))
            rsi_data, params = indicators[rsi_key]
            self.plot_rsi(ax_rsi, rsi_data, params)
        if has_obv:
            obv_key = next(name for name in indicators if name.startswith("OBV"))
            obv_data, _ = indicators[obv_key]
            self.plot_obv(ax_obv, obv_data)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save to file logic
        if save:
            self.save_plot(
                fig,
                save_dir=save_dir,
                save_format=save_format,
                save_dpi=save_dpi,
                ticker=company_name,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
            )

        plt.show()

    def _plot_candlesticks(self, ax: Axes, data: pd.DataFrame):
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
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        price_range = data["High"].max().item() - data["Low"].min().item()
        margin = price_range * 0.05
        ax.set_ylim(
            data["Low"].min().item() - margin, data["High"].max().item() + margin
        )
