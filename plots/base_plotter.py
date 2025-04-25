from abc import ABC, abstractmethod
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from typing import Any, Dict, Optional, Sequence


class BasePlotter(ABC):
    """
    Abstract base class for different plot methods
    """

    COLOR_SCHEMES = {
        "default": {
            "up": "green",
            "down": "red",
            "bg": "white",
            "text": "black",
            "grid": "#cccccc",
        },
        "monochrome": {
            "up": "black",
            "down": "gray",
            "bg": "white",
            "text": "black",
            "grid": "#cccccc",
        },
        "tradingview": {
            "up": "#26a69a",
            "down": "#ef5350",
            "bg": "white",
            "text": "black",
            "grid": "#e0e3eb",
        },
        "dark": {
            "up": "#4CAF50",
            "down": "#FF5252",
            "bg": "#121212",
            "text": "white",
            "grid": "#333333",
        },
    }

    def __init__(
        self,
        title: str,
        color_scheme: str = "default",
        up_color: str = None,
        down_color: str = None,
    ):
        self.title = title
        if color_scheme in self.COLOR_SCHEMES:
            self.scheme = self.COLOR_SCHEMES[color_scheme].copy()
        else:
            self.scheme = self.COLOR_SCHEMES["default"].copy()
        if up_color and up_color.lower() != "none":
            self.scheme["up"] = up_color
        if down_color and down_color.lower() != "none":
            self.scheme["down"] = down_color

    def apply_color_scheme(self, fig: Figure, axes: Sequence[Axes]) -> None:
        fig.patch.set_facecolor(self.scheme["bg"])
        for ax in axes:
            ax.set_facecolor(self.scheme["bg"])
            for spine in ax.spines.values():
                spine.set_color(self.scheme["text"])
            ax.tick_params(colors=self.scheme["text"])
            ax.xaxis.label.set_color(self.scheme["text"])
            ax.yaxis.label.set_color(self.scheme["text"])
            ax.title.set_color(self.scheme["text"])
        fig.suptitle(self.title, color=self.scheme["text"])

    @abstractmethod
    def plot(
        self,
        data: pd.DataFrame,
        indicators: dict,
        column: str,
        company_name: str,
        save: bool = False,
        save_dir: str = None,
        save_format: str = "png",
        save_dpi: int = 300,
        interval: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        pass

    def plot_macd(self, ax: Axes, macd_data: pd.DataFrame, params: Any) -> None:
        macd_line = macd_data["MACD"]
        signal_line = macd_data["Signal"]
        histogram = macd_line - signal_line
        ax.plot(
            macd_data.index, macd_line, label="MACD Line", color="orange", linewidth=1.2
        )
        ax.plot(
            macd_data.index,
            signal_line,
            label="Signal Line",
            color=self.scheme["up"],
            linewidth=1.2,
        )
        colors = [
            self.scheme["up"] if value > 0 else self.scheme["down"]
            for value in histogram
        ]
        ax.bar(
            macd_data.index,
            histogram,
            label="Histogram",
            color=colors,
            alpha=0.7,
            width=1,
        )
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        ax.set_ylabel("MACD")
        ax.legend()
        ax.grid(color=self.scheme.get("grid", None))

    def plot_bbands(self, ax: Axes, bbands_data: pd.DataFrame, params: Any) -> None:
        upper_band = bbands_data["upper_band"]
        lower_band = bbands_data["lower_band"]
        middle_band = bbands_data["middle_band"]
        ax.plot(
            bbands_data.index,
            middle_band,
            label="Middle Band",
            color="blue",
            linewidth=1.2,
        )
        ax.plot(
            bbands_data.index,
            upper_band,
            label="Upper Band",
            color=self.scheme["down"],
            linestyle="--",
            linewidth=1.2,
        )
        ax.plot(
            bbands_data.index,
            lower_band,
            label="Lower Band",
            color=self.scheme["up"],
            linestyle="--",
            linewidth=1.2,
        )
        ax.fill_between(
            bbands_data.index, lower_band, upper_band, color="grey", alpha=0.3
        )
        ax.set_ylabel("BBANDS")
        ax.legend()
        ax.grid(color=self.scheme.get("grid", None))

    def plot_rsi(self, ax: Axes, rsi_data: pd.Series, params: Any) -> None:
        ax.plot(
            rsi_data.index,
            rsi_data,
            label=f"RSI {params}",
            color="purple",
            linewidth=1.2,
        )
        ax.axhline(
            70,
            color=self.scheme["down"],
            linestyle="--",
            linewidth=0.8,
            label="Overbought",
        )
        ax.axhline(
            30, color=self.scheme["up"], linestyle="--", linewidth=0.8, label="Oversold"
        )
        ax.set_ylabel("RSI")
        ax.legend()
        ax.grid(color=self.scheme.get("grid", None))

    def plot_obv(self, ax: Axes, obv_data: pd.Series) -> None:
        ax.plot(
            obv_data.index,
            obv_data,
            label="On balance volume",
            color=self.scheme["up"],
            linewidth=1,
        )
        ax.set_ylabel("OBV")
        ax.legend()
        ax.grid(color=self.scheme.get("grid", None))

    def plot_adx(self, ax: Axes, adx_data: pd.DataFrame) -> None:
        adx_line = adx_data["ADX"]
        positive_di_line = adx_data["plus_DI"]
        negative_di_line = adx_data["minus_DI"]
        ax.plot(
            adx_data.index,
            adx_line,
            label="ADX Line",
            color="blue",
            linewidth=1.2,
        )
        ax.plot(
            adx_data.index,
            positive_di_line,
            label="+DI Line",
            color=self.scheme["up"],
            linewidth=1,
        )
        ax.plot(
            adx_data.index,
            negative_di_line,
            label="-DI Line",
            color=self.scheme["down"],
            linewidth=1,
        )
        ax.set_ylabel("ADX")
        ax.legend()
        ax.grid(color=self.scheme.get("grid", None))

    def save_plot(
        self,
        fig: Figure,
        save_dir: str,
        save_format: str = "png",
        save_dpi: int = 300,
        ticker: str = "",
        interval: str = "",
        start_date: str = "",
        end_date: str = "",
    ) -> str:
        """
        Save the plot to a file.
        """
        import os
        from datetime import datetime

        format = save_format.lower()
        valid_formats = ["png", "pdf", "svg", "jpg", "jpeg"]
        if format not in valid_formats:
            raise ValueError(f"Format must be one of {valid_formats}")

        if format == "jpg":
            format = "jpeg"

        # Generate filename
        components = []
        if ticker:
            components.append(ticker)
        if interval:
            components.append(interval)
        if start_date:
            components.append(start_date.replace("-", ""))
        if end_date:
            components.append(end_date.replace("-", ""))

        if not components:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            components.append(f"plot_{timestamp}")

        filename = "_".join(components) + f".{format}"

        if save_dir:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            filepath = os.path.join(save_dir, filename)
        else:
            filepath = filename

        fig.savefig(filepath, format=format, dpi=save_dpi, bbox_inches="tight")
        print(f"Plot saved to: {os.path.abspath(filepath)}")

        return filepath
