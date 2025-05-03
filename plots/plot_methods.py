from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib as plt
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, Sequence
from matplotlib.widgets import Cursor, SpanSelector, RectangleSelector, TextBox, Button
import matplotlib as mpl

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


def enable_interactive(fig: Figure, axes: Sequence[Axes], data: pd.DataFrame = None):
    """Enable interactive features for matplotlib"""
    try:
        import mplcursors
    except ImportError:
        print(
            "For full interactive features, please install mplcursors: pip install mplcursors"
        )
        has_mplcursors = False
    else:
        has_mplcursors = True

    fig._interactive_elements = {}

    for ax in axes:
        cursor_obj = Cursor(ax, useblit=True, color="gray", linewidth=0.5)
        fig._interactive_elements["cursor"] = cursor_obj

    if has_mplcursors:
        c = mplcursors.cursor(hover=True)

        @c.connect("add")
        def on_add(sel):
            x, y = sel.target
            try:
                if isinstance(data.index, pd.DatetimeIndex):
                    date_str = pd.to_datetime(x).strftime("%Y-%m-%d")
                    sel.annatation.set_text(f"Date: {date_str}\nValue: {y:.2f}")
                else:
                    sel.annotation.set_text(f"X: {x:.2f}\nY: {y:.2f}")
            except:
                sel.annotation.set_text(f"X: {x:.2f}\nY: {y:.2f}")

        fig._interactive_elements["tooltips"] = c

    ax_price = axes[0]

    def on_select_zoom(eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
            for ax in axes:
                curr_xlim = ax.get_xlim()
                curr_ylim = ax.get_ylim()

                if ax == ax_price:
                    new_ylim = sorted([y1, y2])
                else:
                    new_ylim = curr_ylim

                ax.set_xlim(sorted([x1, x2]))
                ax.set_ylim(new_ylim)
            fig.canvas.draw_idle()

    rect_selector = RectangleSelector(
        ax_price,
        on_select_zoom,
        useblit=True,
        button=[1],
        minspanx=5,
        minspany=5,
        spancoords="pixels",
        interactive=True,
    )
    fig._interactive_elements["rect_selector"] = rect_selector

    def reset_zoom(event):
        for ax in axes:
            ax.relim()
            ax.autoscale()
        fig.canvas.draw_idle()

    reset_button_ax = fig.add_axes([0.85, 0.01, 0.1, 0.03])
    reset_button = Button(reset_button_ax, "Reset Zoom")
    reset_button.on_clicked(reset_zoom)
    fig._interactive_elements["reset_button"] = reset_button

    def on_span_select(xmin, xmax):
        print(f"Selected range: {xmin:.2f} to {xmax:.2f}")

        try:
            if isinstance(data.index, pd.DatetimeIndex):
                xmin_idx = np.argmin(np.abs(np.array(data.index.astype(float)) - xmin))
                xmax_idx = np.argmin(np.abs(np.array(data.index.astype(float)) - xmax))

                date_range = data.iloc[xmin_idx : xmax_idx + 1]

                if not date_range.empty:
                    print(
                        f"Date range: {date_range.index[0].strftime("%Y-%m-%d")} to {date_range.index[-1].strftime("%Y-%m-%d")}"
                    )

                    price_col = date_range.columns[0]

                    stats = {
                        "Start": date_range.index[0].strftime("%Y-%m-%d"),
                        "End": date_range.index[-1].strftime("%Y-%m-%d"),
                        "Min": date_range[price_col].min(),
                        "Max": date_range[price_col].max(),
                        "Mean": date_range[price_col].mean(),
                        "% Change": (
                            (
                                date_range[price_col].iloc[-1]
                                / date_range[price_col].iloc[0]
                            )
                            - 1
                        )
                        * 100,
                    }

                    print("\nSelected Range Statistics:")
                    for k, v in stats.items():
                        if isinstance(v, float):
                            print(f"  {k}: {v:.2f}")
                        else:
                            print(f"  {k}: {v}")
                else:
                    print("No data points in selected range")
        except Exception as e:
            print(f"Error analyzing selection: {e}")

    span_selector = SpanSelector(
        ax_price,
        on_span_select,
        "horizontal",
        useblit=True,
        rectprops=dict(alpha=0.3, facecolor="lightblue"),
        button=[3],
    )
    fig._interactive_elements["span_selector"] = span_selector

    def on_key_press(event):
        if event.key == "r":
            reset_zoom(event)
        elif event.key == "s":
            import os
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"quick_save_{timestamp}.png"
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"Quick saved to: {os.path.abspath(filepath)}")

    fig.canvas.mpl_connect("key_press_event", on_key_press)

    instruction_text = """
    Interactive controls:
    • Click & drag left button: Zoom to rectangle
    • Click & drag right button: Analyze time range
    • Hover: Show data points
    • 'r' key: Reset zoom
    • 's' key: Quick save
    """
    fig.text(
        0.01,
        0.01,
        instruction_text,
        fontsize=8,
        verticalalignment="bottom",
        bbox=dict(boxtyle="round", facecolor="white", alpha=0.08),
    )

    print("Interactive mode enabled with the following features:")
    print("- Hover over data points to see values")
    print("- Left-click and drag to zoom into an area")
    print("- Right-click and drag to analyze a time range")
    print("- Press 'r' to reset zoom")
    print("- Press 's' to quick save the current view")
    print("- Click 'Reset Zoom' button to reset the view")
