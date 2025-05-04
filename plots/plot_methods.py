from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib as plt
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, Sequence
from matplotlib.widgets import Cursor, SpanSelector, RectangleSelector, TextBox, Button
import matplotlib.dates as mdates
import matplotlib as mpl
import os
from datetime import datetime

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


def enable_interactive(fig: Figure, data: pd.DataFrame):
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

    if not fig.get_axes():
        print(
            "Warning: No axes found in the figure. Cannot enable interactive features."
        )
        return

    if not hasattr(fig, "_interactive_state"):
        fig._interactive_state = {"widgets": {}, "initial_limits": {}}
    # Get all axes from the figure
    axes = fig.get_axes()
    for ax in axes:
        if ax not in fig._interactive_state["initial_limits"]:
            fig._interactive_state["initial_limits"][ax] = {
                "xlim": ax.get_xlim(),
                "ylim": ax.get_ylim(),
            }
    cursor_obj = Cursor(axes[0], useblit=True, color="gray", linewidth=0.5)
    fig._interactive_state["widgets"]["cursor"] = cursor_obj

    if has_mplcursors:
        c = mplcursors.cursor(axes, hover=True, multiple=True)

        @c.connect("add")
        def on_add(sel):
            ax: Axes = sel.artist.axes
            x, y = sel.target
            try:
                is_date_axis = isinstance(
                    ax.xaxis.get_major_formatter(), mdates.DateFormatter
                ) or isinstance(ax.xaxis.get_major_locator(), mdates.DateLocator)

                if is_date_axis:
                    try:
                        dt_obj: datetime = mdates.num2date(x)
                        date_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                        sel.annotation.set_text(f"X (num): {x:.2f}\nY: {y:.4f}")
                    except (ValueError, TypeError) as e:
                        print(f"Debug: Date conversion failed for x={x}. Error: {e}")
                        sel.annotation.set_text(f"X (num): {x:.2f}\nY: {y:.4f}")
                else:
                    sel.annotation.set_text(f"X: {x:.4f}\nY: {y:.4f}")

            except Exception as e:
                print(f"Error in hover annotation callback: {e}")
                try:
                    sel.annotation.set_text(f"X: {x:.2f}\nY: {y:.2f}")
                except Exception:
                    pass

            sel.annotation.get_bbox_patch().set(alpha=0.8, facecolor="white")

        fig._interactive_state["widgets"]["tooltips"] = c
    else:
        print(
            "For full interactive hover features, please install mplcursors: python -m pip install mplcursors"
        )

    # Custom zoom

    ax_main = axes[0]

    def on_select_zoom(eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        if x1 is None or x2 is None or y1 is None or y2 is None:
            return

        # Check for minimal drag distance to avoid accidental zooms
        min_pixel_dist = 5
        if (
            abs(eclick.x - erelease.x) < min_pixel_dist
            or abs(eclick.y - erelease.y) < min_pixel_dist
        ):
            return

        new_xlim = sorted([x1, x2])
        new_ylim = sorted([y1, y2])

        for ax in axes:
            ax.set_xlim(new_xlim)

            if ax == ax_main:
                ax.set_ylim(new_ylim)
            else:
                pass

        fig.canvas.draw_idle()

    rect_selector = RectangleSelector(
        ax_main,
        on_select_zoom,
        useblit=True,
        button=[1],
        minspanx=5,
        minspany=5,
        spancoords="pixels",
        interactive=True,
        props=dict(facecolor="lightblue", edgecolor="blue", alpha=0.3, fill=True),
    )
    fig._interactive_state["widgets"]["rect_selector"] = rect_selector

    # Reset Zoom Function
    # Restores to the *initial* limits stored earlier
    def reset_zoom(event=None):
        initial_limits = fig._interactive_state.get("initial_limits", {})
        if not initial_limits:
            print("Warning: Initial limits not stored. Cannot reset precisely.")
            for ax in axes:
                ax.relim()
                ax.autoscale()
        else:
            for ax in axes:
                if ax in initial_limits:
                    limits = initial_limits[ax]
                    ax.set_xlim(limits["xlim"])
                    ax.set_ylim(limits["ylim"])
                else:
                    ax.relim()
                    ax.autoscale()
        fig.canvas.draw_idle()

    # Reset button
    try:
        reset_button_ax = fig.add_axes([0.88, 0.92, 0.1, 0.04])
        reset_button = Button(reset_button_ax, "Reset View")
        reset_button.on_clicked(reset_zoom)
        fig._interactive_state["widgets"]["reset_button"] = reset_button
    except ValueError as e:
        print(f"Could not add reset button (overlapping axes?): {e}")

    def on_span_select(xmin, xmax):
        if data is None:
            print(
                f"Selected X range: {xmin:.2f} to {xmax:.2f} (No data provided for analysis.)"
            )
            return

        print(f"\nAnalyzing selected range: {xmin:.4f} to {xmax:.4f}")
        try:
            if isinstance(data.index, pd.DatetimeIndex):
                if not data.index.is_monotonic_increasing:
                    print(
                        "Warning: DataFrame index is not sorted. Span analysis might be incorrect."
                    )

                try:
                    pd_xmin = mdates.num2date(xmin)
                    pd_xmax = mdates.num2date(xmax)
                    start_idx = data.index.searchsorted(pd_xmin, side="left")
                    end_idx = data.index.searchsorted(pd_xmax, side="right")
                    selected_data = data.iloc[start_idx:end_idx]

                except Exception as e_conv:
                    print(
                        f"Debug: Error converting span limits ({xmin}, {xmax}) or finding indices: {e_conv}"
                    )
                    numeric_index = data.index.astype(np.int64)
                    print("Analysis failed due to date conversion issues.")
                    return

                if not selected_data.empty:
                    price_col = None
                    potential_cols = ["Close", "Adj Close", "Value", "Price"]
                    for col in potential_cols:
                        if col in selected_data.columns:
                            price_col = col
                            break
                    if price_col is None:
                        numeric_cols = selected_data.select_dtypes(
                            include=np.number
                        ).columns
                        if not numeric_cols.empty:
                            price_col = numeric_cols[0]
                        else:
                            print("No suitable numeric column found for analysis.")
                            return

                    first_date = selected_data.index[0]
                    last_date = selected_data.index[-1]
                    start_price = selected_data[price_col].iloc[0]
                    end_price = selected_data[price_col].iloc[-1]

                    stats = {
                        "Start Date": first_date.strftime("%Y-%m-%d"),
                        "End Date": last_date.strftime("%Y-%m-%d"),
                        "Duration": (last_date - first_date),
                        f"Min {price_col}": selected_data[price_col].min(),
                        f"Max {price_col}": selected_data[price_col].max(),
                        f"Mean {price_col}": selected_data[price_col].mean(),
                        f"Start {price_col}": start_price,
                        f"End {price_col}": end_price,
                        "% Change": (
                            ((end_price / start_price) - 1) * 100
                            if start_price != 0
                            else float("inf")
                        ),
                        "Points": len(selected_data),
                    }

                    print("--- Selected Range Statistics ---")
                    for k, v in stats.items():
                        if isinstance(v, float):
                            print(f"   {k}: {v:.2f}")
                        else:
                            print(f"   {k}: {v}")
                    print("---------------------------------")
                else:
                    print("No data points found in the selected range.")
            else:
                print("Span analysis currently requires a DatetimeIndex.")

        except Exception as e:
            print(f"Error during span analysis: {e}")
            import traceback

            traceback.print_exc()

    span_selector = SpanSelector(
        ax_main,
        on_span_select,
        "horizontal",
        useblit=True,
        props=dict(alpha=0.3, facecolor="lightcoral"),
        button=[3],
        interactive=True,
        minspan=None,
    )
    fig._interactive_state["widgets"]["span_selector"] = span_selector

    def on_key_press(event):
        if event.key == "r":
            print("Reseting zoom (R key)")
            reset_zoom(event)
        elif event.key == "s":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"plot_save_{timestamp}.png"
            try:
                filepath = default_filename
                fig.savefig(filepath, dpi=150, bbox_inches="tight")
                abs_path = os.path.abspath(filepath)
                print(f"Plot saved to: {abs_path}")
            except Exception as e_save:
                print(f"Error saving plot: {e_save}")

    if not hasattr(fig.canvas, "_key_press_cid") or fig.canvas._key_press_cid is None:
        fig.canvas._key_press_cid = fig.canvas.mpl_connect(
            "key_press_event", on_key_press
        )

    for txt in fig.texts:
        if hasattr(txt, "_is_instruction_text"):
            txt.remove()

    instruction_text = """Interactive Controls:
L-Drag: Zoom Box | R-Drag: Analyze Range | Hover: Data Value
Keys: [R] Reset View | [S] Save PNG"""
    instr_obj = fig.text(
        0.02,
        0.01,
        instruction_text,
        fontsize=8,
        verticalalignment="bottom",
        wrap=True,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgrey", alpha=0.6),
        transform=fig.transFigure,
    )
    instr_obj._is_instruction_text = True

    fig.canvas.draw_idle()
