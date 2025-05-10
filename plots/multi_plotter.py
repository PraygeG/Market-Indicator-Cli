from typing import Dict, Tuple, Optional, Sequence
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from plots.plot_methods import (
    analyze_indicators,
    assign_axes,
    save_plot,
)


class MultiTickerPlotter:
    """
    Plot multiple tickers on the same axes, with optional normalization and log-scale.
    """

    def __init__(
        self,
        normalize: bool = False,
        log_scale: bool = False,
        title: str = "Multi-Ticker Comparison",
    ) -> None:
        """
        Initialize the MultiTickerPlotter with normalization and log-scale options.
        """
        self.normalize = normalize
        self.log_scale = log_scale
        self.title = title

    def _normalize_series(self, series: pd.Series) -> pd.Series:
        """
        Normalize a pandas Series to its first value.
        """
        if not series.empty:
            first_valid = series.first_valid_index()
            if first_valid is not None:
                base_value = series.loc[first_valid]
                if base_value != 0:
                    return series / base_value
        return series

    def _enable_hover(self, fig: plt.Figure, axes: Sequence[plt.Axes]) -> None:
        """
        Enable hover tooltips on the plot axes if mplcursors is available.
        """
        try:
            mplcursors.cursor(axes, hover=True)
        except Exception as e:
            print("mplcursors not available for failed to initialize:", e)

    def plot(
        self,
        data: Dict[str, pd.DataFrame],
        indicators: Optional[
            Dict[str, Tuple[pd.Series | pd.DataFrame, Optional[list[int]]]]
        ] = None,
        column: str = "Close",
        save: bool = False,
        save_dir: str = None,
        save_format: str = None,
        save_dpi: int = 300,
        figsize: Tuple[int, int] = (12, 6),
    ) -> None:
        """
        Plot multiple tickers and their indicators. Optionally save or show interactively.
        """
        if not data:
            raise ValueError("'data' must contain at least one ticker")

        for ticker, df in data.items():
            if column not in df.columns:
                raise ValueError(f"DataFrame for {ticker!r} has no column {column!r}.")

        # Price comparison plot
        fig_price, ax_price = plt.subplots(1, 1, figsize=figsize)
        for ticker, df in data.items():
            series = df[column].sort_index()
            if self.normalize:
                series = self._normalize_series(series)
            ax_price.plot(series.index, series, label=ticker, linewidth=1.5)
        ax_price.set_title(self.title)
        ax_price.set_ylabel(column + (" (normalized)" if self.normalize else ""))
        if self.log_scale:
            ax_price.set_yscale("log")
        ax_price.grid(True)
        ax_price.legend(loc="upper left")
        plt.tight_layout()
        self._enable_hover(fig_price, [ax_price])
        if save:
            save_plot(fig_price, save_dir, save_format, save_dpi)
        plt.show()

        # Indicator plot
        if indicators:
            indicators_info = analyze_indicators(indicators, True)
            subplot_count = indicators_info["subplot_count"]
            fig_ind, axes = plt.subplots(
                subplot_count,
                1,
                figsize=(figsize[0], figsize[1] * subplot_count),
                sharex=True,
            )
            if subplot_count == 1:
                axes = [axes]
            ax_map = assign_axes(axes, indicators_info, True)

            for ind_name, (ind_data, params) in indicators.items():
                if "MACD" in ind_name and ax_map["macd"]:
                    ax_to_use = ax_map["macd"]
                elif ind_name.startswith("RSI") and ax_map["rsi"]:
                    ax_to_use = ax_map["rsi"]
                elif ind_name.startswith("OBV") and ax_map["obv"]:
                    ax_to_use = ax_map["obv"]
                elif ind_name.startswith("ADX") and ax_map["adx"]:
                    ax_to_use = ax_map["adx"]
                elif (
                    ind_name.startswith("EMA") or ind_name.startswith("SMA")
                ) and ax_map["ma"]:
                    ax_to_use = ax_map["ma"]
                else:
                    continue

                if ax_to_use:
                    if isinstance(ind_data, pd.DataFrame):
                        for ticker in data.keys():
                            if ticker in ind_data.columns:
                                series = ind_data[ticker].sort_index()
                                if self.normalize and not series.empty:
                                    series = self._normalize_series(series)
                                ax_to_use.plot(
                                    series.index,
                                    series,
                                    label=f"{ticker}{ind_name}",
                                    linewidth=1,
                                )
                    else:
                        series = ind_data.sort_index()
                        if self.normalize and not series.empty:
                            series = self._normalize_series(series)
                        ax_to_use.plot(
                            series.index, series, label=ind_name, linewidth=1
                        )

                    if ax_to_use != ax_map["price"]:
                        ax_to_use.set_title(
                            f"{ind_name}{' (normalized)' if self.normalize else ''}"
                        )
                        ax_to_use.set_ylabel(ind_name)

                    if self.log_scale:
                        values = ind_data.dropna().values
                        all_positive = (
                            (values > 0).all() if hasattr(values, "all") else True
                        )
                        if all_positive:
                            ax_to_use.set_yscale("log")
                    ax_to_use.grid(True)
                    ax_to_use.legend(loc="upper left")

            plt.tight_layout()
            self._enable_hover(fig_ind, axes)
            if save:
                save_plot(fig_ind, save_dir, save_format, save_dpi)
            else:
                plt.show()
