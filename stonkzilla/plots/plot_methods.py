"""Plot methods reused throughout the plotters."""

import os
from datetime import datetime, date
from typing import Any, Dict, Optional, Sequence, Tuple, List
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd

COLOR_SCHEMES = {
    "default": {
        "up": "green",
        "down": "red",
        "bg": "white",
        "text": "black",
        "grid": "#cccccc",
        "fibs": ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3"],
    },
    "monochrome": {
        "up": "black",
        "down": "gray",
        "bg": "white",
        "text": "black",
        "grid": "#cccccc",
        "fibs": ["#666666"] * 5,
    },
    "tradingview": {
        "up": "#26a69a",
        "down": "#ef5350",
        "bg": "white",
        "text": "black",
        "grid": "#e0e3eb",
        "fibs": ["#26a69a", "#a3d9ce", "#c6ece6", "#e8f6f5", "#ffffff"],
    },
    "dark": {
        "up": "#4CAF50",
        "down": "#FF5252",
        "bg": "#121212",
        "text": "white",
        "grid": "#333333",
        "fibs": ["#90ee90", "#98fb98", "#adff2f", "#7cfc00", "#00fa9a"],
    },
}


def apply_color_scheme(
    fig: Figure, axes: Sequence[Axes], scheme: dict, title: str
) -> None:
    """
    Apply the color scheme to the figure and axes.
    """
    fig.patch.set_facecolor(scheme["bg"])
    for ax in axes:
        ax.set_facecolor(scheme["bg"])
        for spine in ax.spines.values():
            spine.set_color(scheme["text"])
        ax.tick_params(colors=scheme["text"])
        ax.xaxis.label.set_color(scheme["text"])
        ax.yaxis.label.set_color(scheme["text"])
        ax.title.set_color(scheme["text"])
    fig.suptitle(title, color=scheme["text"])


def resolve_color_scheme(
    color_scheme: str, up_color: Optional[str] = None, down_color: Optional[str] = None
) -> Dict[str, str]:
    """Determine which color to use."""
    scheme = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["default"]).copy()
    if up_color and up_color.lower() != "none":
        scheme["up"] and up_color
    if down_color and down_color.lower() != "none":
        scheme["down"] = down_color
    return scheme


def create_indicator_subplots(
    subplot_count: int, figsize: tuple = (12, 6), height_ratio: int = 3
) -> Tuple[Figure, List[Axes]]:
    """Create number of subplots for applied indicators."""
    fig, axes = plt.subplots(
        subplot_count,
        1,
        figsize=(figsize[0], figsize[1] + 2 * subplot_count),
        gridspec_kw={"height_ratios": [height_ratio] + [1] * (subplot_count - 1)},
    )
    if subplot_count == 1:
        axes = [axes]
    return fig, axes


def _plot_one_line(
    ax: Axes,
    x_data: pd.Index,
    y_data: pd.Series,
    label: Optional[str],
    color: Optional[str],
    *,
    linewidth: float = 1.0,
    linestyle: str = "--",
    alpha: float = 0.8,
    marker: Optional[str] = None,
    legend: bool = False,
    **plot_kwargs,
) -> None:
    """
    Plot a single line on the given axis.
    """
    ax.plot(
        x_data,
        y_data,
        label=label,
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        alpha=alpha,
        marker=marker,
        **plot_kwargs,
    )
    if legend and label:
        ax.legend(loc="best")


def plot_fibo(
    ax: Axes,
    fibo_data: pd.DataFrame,
    scheme: dict[str, str],
    *,
    ylabel: str = "Price",
    title: str = "Fibonacci Retracement Levels",
    linewidth: float = 1.0,
    linestyle: str = "--",
    alpha: float = 1,
) -> None:
    """
    Plot Fibonacci retracement levels on the axis.
    """
    levels = list(fibo_data.columns)
    fib_colors = scheme.get("fibs", [])

    if not levels:
        ax.set_ylabel(ylabel)
        if title:
            ax.set_title(title)
        ax.grid(color=scheme.get("grid", None), linestyle=":")
        return

    if len(levels) > len(fib_colors):
        raise ValueError(
            f"Not enough fib colors provided. Data has {len(levels)} levels,"
            f"but scheme['fibs'] only provides {len(fib_colors)} colors."
        )

    for i, level_name in enumerate(levels):
        color_for_this_level = fib_colors[i]

        _plot_one_line(
            ax=ax,
            x_data=fibo_data.index,
            y_data=fibo_data[level_name],
            label=level_name,
            color=color_for_this_level,
            linewidth=linewidth,
            linestyle=linestyle,
            alpha=alpha,
        )
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(color=scheme.get("grid", "#D3D3D3"), linestyle=":")


def plot_macd(ax: Axes, macd_data: pd.DataFrame, scheme: dict[str, str]) -> None:
    """
    Plot the MACD indicator on the axis.
    """
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
        color=scheme["up"],
        linewidth=1.2,
    )
    colors = [scheme["up"] if value > 0 else scheme["down"] for value in histogram]
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
    ax.grid(color=scheme.get("grid", None))


def plot_bbands(
    ax: Axes, bbands_data: pd.DataFrame, params: int, scheme: dict[str, str]
) -> None:
    """
    Plot Bollinger Bands on the axis.
    """
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
        color=scheme["down"],
        linestyle="--",
        linewidth=1.2,
    )
    ax.plot(
        bbands_data.index,
        lower_band,
        label="Lower Band",
        color=scheme["up"],
        linestyle="--",
        linewidth=1.2,
    )
    ax.fill_between(bbands_data.index, lower_band, upper_band, color="grey", alpha=0.3)
    ax.set_ylabel("BBANDS")
    ax.legend()
    ax.grid(color=scheme.get("grid", None))


def plot_rsi(
    ax: Axes, rsi_data: pd.Series, params: Any, scheme: dict[str, str]
) -> None:
    """
    Plot the RSI indicator on the axis.
    """
    ax.plot(
        rsi_data.index,
        rsi_data,
        label=f"RSI {params}",
        color="purple",
        linewidth=1.2,
    )
    ax.axhline(
        70,
        color=scheme["down"],
        linestyle="--",
        linewidth=0.8,
        label="Overbought",
    )
    ax.axhline(30, color=scheme["up"], linestyle="--", linewidth=0.8, label="Oversold")
    ax.set_ylabel("RSI")
    ax.legend()
    ax.grid(color=scheme.get("grid", None))


def plot_obv(ax: Axes, obv_data: pd.Series, scheme: dict[str, str]) -> None:
    """
    Plot the OBV indicator on the axis.
    """
    ax.plot(
        obv_data.index,
        obv_data,
        label="On balance volume",
        color=scheme["up"],
        linewidth=1,
    )
    ax.set_ylabel("OBV")
    ax.legend()
    ax.grid(color=scheme.get("grid", None))


def plot_adx(ax: Axes, adx_data: pd.DataFrame, scheme: dict[str, str]) -> None:
    """
    Plot the ADX indicator on the axis.
    """
    adx_line = adx_data["adx"]
    positive_di_line = adx_data["plus_di"]
    negative_di_line = adx_data["minus_di"]
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
        color=scheme["up"],
        linewidth=1,
    )
    ax.plot(
        adx_data.index,
        negative_di_line,
        label="-DI Line",
        color=scheme["down"],
        linewidth=1,
    )
    ax.set_ylabel("ADX")
    ax.legend()
    ax.grid(color=scheme.get("grid", None))


def analyze_indicators(
    indicators: dict[str, tuple[pd.DataFrame | pd.Series, list[int]]],
    is_multi_ticker: bool = False,
) -> dict[str, int | bool]:
    """
    Analyze indicator presence and determine the number of subplots.
    """
    has_macd = any("MACD" in name for name in indicators)
    has_bbands = any("BBANDS" in name for name in indicators)
    has_fibo = any("FIBO" in name for name in indicators)
    has_rsi = any(name.startswith("RSI") for name in indicators)
    has_obv = any(name.startswith("OBV") for name in indicators)
    has_adx = any(name.startswith("ADX") for name in indicators)
    has_ema = any(name.startswith("EMA") for name in indicators)
    has_sma = any(name.startswith("SMA") for name in indicators)
    has_ma = has_ema or has_sma

    subplot_count = 0
    subplot_count += 1

    if has_ma and is_multi_ticker:
        subplot_count += 1

    subplot_count += sum([has_macd, has_rsi, has_obv, has_adx])

    return {
        "subplot_count": subplot_count,
        "has_bbands": has_bbands,
        "has_macd": has_macd,
        "has_rsi": has_rsi,
        "has_obv": has_obv,
        "has_adx": has_adx,
        "has_fibo": has_fibo,
        "has_ema": has_ema,
        "has_sma": has_sma,
        "has_ma": has_ma,
    }


def assign_axes(
    axes: Axes, indicators_info: dict, is_multi_ticker: bool = False
) -> dict[str, Axes]:
    """
    Assign axes to each indicator based on their presence.
    """
    ax_map = {}
    current_index = 1
    ax_map["price"] = axes[0]

    if indicators_info.get("has_ma") and is_multi_ticker:
        ax_map["ma"] = axes[current_index]
        current_index += 1
    else:
        ax_map["ma"] = ax_map["price"]

    if indicators_info.get("has_obv"):
        ax_map["obv"] = axes[current_index]
        current_index += 1
    else:
        ax_map["obv"] = None

    if indicators_info.get("has_macd"):
        ax_map["macd"] = axes[current_index]
        current_index += 1
    else:
        ax_map["macd"] = None

    if indicators_info.get("has_rsi"):
        ax_map["rsi"] = axes[current_index]
        current_index += 1
    else:
        ax_map["rsi"] = None

    if indicators_info.get("has_adx"):
        ax_map["adx"] = axes[current_index]
        current_index += 1
    else:
        ax_map["adx"] = None

    return ax_map


def save_plot(
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

    def _fmt(d):
        if isinstance(d, (date, datetime)):
            return d.strftime("%Y%m%d")
        return d.replace("-", "")

    start_str = _fmt(start_date)
    end_str = _fmt(end_date)

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
    if start_str:
        components.append(start_str)
    if end_str:
        components.append(end_str)
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
