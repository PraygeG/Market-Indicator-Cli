from matplotlib.figure import Figure
from matplotlib.axes import Axes
import pandas as pd
from typing import Any, Dict, Optional, Sequence

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


def apply_color_scheme(
    fig: Figure, axes: Sequence[Axes], scheme: dict, title: str
) -> None:
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


def plot_macd(ax: Axes, macd_data: pd.DataFrame, params: Any, scheme: dict) -> None:
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


def plot_bbands(ax: Axes, bbands_data: pd.DataFrame, params: Any, scheme: dict) -> None:
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


def plot_rsi(ax: Axes, rsi_data: pd.Series, params: Any, scheme: dict) -> None:
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


def plot_obv(ax: Axes, obv_data: pd.Series, scheme: dict) -> None:
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


def plot_adx(ax: Axes, adx_data: pd.DataFrame, scheme: dict) -> None:
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


def analyze_indicators(indicators: dict) -> dict:
    """Analyze indicator presence and determine the number of subplots"""
    has_macd = any("MACD" in name for name in indicators)
    has_bbands = any("BBANDS" in name for name in indicators)
    has_rsi = any(name.startswith("RSI") for name in indicators)
    has_obv = any(name.startswith("OBV") for name in indicators)
    has_adx = any(name.startswith("ADX") for name in indicators)
    subplot_count = 1 + has_macd + has_rsi + has_obv + has_adx
    return {
        "subplot_count": subplot_count,
        "has_bbands": has_bbands,
        "has_macd": has_macd,
        "has_rsi": has_rsi,
        "has_obv": has_obv,
        "has_adx": has_adx,
    }


def assign_axes(axes: Axes, indicators_info: dict) -> dict:
    """Assign axes to each indicator based on their presence."""
    ax_map = {}
    current_index = 1
    ax_map["price"] = axes[0]
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


def enable_interactive(fig: Figure):
    """Enable interactive features for matplotlib"""
    import matplotlib

    matplotlib.interactive(True)
    fig.canvas.mpl_connect("pick_event", lambda event: print(f"Picked: {event.artist}"))


def plot_multi_ticker(
    ax: Axes,
    data_dict: dict[str, pd.DataFrame],
    column: str,
    scheme: dict,
    normalize: bool = True,
):
    """Plot multiple tickers data on the same axis"""
    for ticker, df in data_dict.items():
        if column in df.columns and not df.empty:
            series = df[column]
            if normalize:
                base = series.iloc[0]
                pct = (series / base - 1) * 100
                ax.plot(series.index, pct, label=f"{ticker} (% change)", linewidth=1.5)
            else:
                ax.plot(series.index, series, label=ticker, linewidth=1.5)
    ax.set_ylabel(f"{column} (% change)" if normalize else column)
    ax.legend()
    ax.grid(color=scheme.get("grid", None))


def plot_multi_candlestick(
    ax: Axes,
    data_dict: dict[str, pd.DataFrame],
    scheme: dict,
    normalize: bool = True,
):
    """Plot multiple tickers as normalized candlesticks (body = % change from open)"""
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import numpy as np

    for ticker, data in data_dict.items():
        if not all(col in data.columns for col in ["Open", "High", "Low", "Close"]):
            continue
        data = data.sort_index()
        date_nums = [mdates.date2num(d) for d in data.index]
        if len(data) > 1:
            diffs = [b - a for a, b in zip(date_nums[:-1], date_nums[1:])]
            width = np.median(diffs) * 0.7
        else:
            width = 0.6

        first_open = data["Open"].iloc[0]
        for date, row in data.iterrows():
            x = mdates.date2num(date)
            o, h, l, c = row["Open"], row["High"], row["Low"], row["Close"]
            if normalize:
                o = (o / first_open - 1) * 100
                h = (h / first_open - 1) * 100
                l = (l / first_open - 1) * 100
                c = (c / first_open - 1) * 100
            color = scheme["up"] if c >= o else scheme["down"]
            body_bottom = min(o, c)
            body_height = abs(c - o)
            rect = Rectangle(
                xy=(x - width / 2, body_bottom),
                width=width,
                height=body_height,
                facecolor=color,
                edgecolor="black",
                linewidth=0.5,
                alpha=0.5,
                label=f"{ticker}" if date == data.index[0] else None,
            )
            ax.add_patch(rect)
            ax.plot([x, x], [max(o, c), h], color="black", linewidth=0.8, alpha=0.5)
            ax.plot([x, x], [min(o, c), l], color="black", linewidth=0.8, alpha=0.5)
    ax.set_ylabel("Price (% change)" if normalize else "Price")
    ax.legend()
    ax.grid(color=scheme.get("grid", None))
