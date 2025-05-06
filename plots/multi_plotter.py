from typing import Dict, Tuple, Optional, Sequence
import pandas as pd
import matplotlib.pyplot as plt
from plots.plot_methods import (
    analyze_indicators,
    assign_axes,
    save_plot,
)


class MultiTickerPlotter:
    """
    Plot multiple tickers on the same axes, with optional normalization and log-scale,
    """

    def __init__(
        self,
        normalize: bool = False,
        log_scale: bool = False,
        title: str = "Multi-Ticker Comparison",
    ) -> None:
        self.normalize = normalize
        self.log_scale = log_scale
        self.title = title

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
                series = series / series.iloc[0]
            ax_price.plot(series.index, series, label=ticker, linewidth=1.5)
        ax_price.set_title(self.title)
        ax_price.set_ylabel(column + (" (normalized)" if self.normalize else ""))
        if self.log_scale:
            ax_price.set_yscale("log")
        ax_price.grid(True)
        ax_price.legend(loc="upper left")
        plt.tight_layout()
        if save:
            save_plot(fig_price, save_dir, save_format, save_dpi)
        plt.show()

        # Indicator plot
        if indicators:
            indicators_info = analyze_indicators(indicators, True)

            subplot_count = indicators_info["subplot_count"] 

            fig_ind, axes = plt.subplots(subplot_count, 1, figsize=(figsize[0], figsize[1] * subplot_count), sharex=True)

            if subplot_count == 1:
                axes = [axes]

            current_index = 0

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
                elif (ind_name.startswith("EMA") or ind_name.startswith("SMA")) and ax_map["ma"]:
                    ax_to_use = ax_map["ma"]
                else:
                    continue

                if ax_to_use:
                    if isinstance(ind_data, pd.DataFrame):
                        for ticker in data.keys():
                            if ticker in ind_data.columns:
                                series = ind_data[ticker].sort_index()
                                if self.normalize and not series.empty:
                                    first_valid = series.first_valid_index()
                                    if first_valid is not None:
                                        base_value = series.loc[first_valid]
                                        if base_value != 0:
                                            series = series / base_value
                                ax_to_use.plot(series.index, series, label=f"{ticker}{ind_name}", linewidth=1)
                    else:
                        series = ind_data.sort_index()
                        if self.normalize and not series.empty:
                            first_valid = series.first_valid_index()
                            if first_valid is not None:
                                base_value = series.loc[first_valid]
                                if base_value != 0:
                                    series = series / base_value
                        ax_to_use.plot(ind_data.index, ind_data, label=ind_name, linewidth=1)

                    if ax_to_use != ax_map["price"]:
                        ax_to_use.set_title(f"{ind_name}{"normalized" if self.normalize else ""}")
                        ax_to_use.set_ylabel(ind_name)

                    if self.log_scale:
                        values = ind_data.dropna().values
                        all_positive = True
                        if hasattr(values, "__iter__"):
                            for v in values:
                                if hasattr(v, "__iter__"):
                                    all_positive = all(x > 0 for x in v if pd.notnull(x))
                                else:
                                    all_positive = v > 0 if pd.notnull(v) else True
                                if not all_positive:
                                    break
                        else:
                            all_positive = values > 0
                        
                        if all_positive:
                            ax_to_use.set_yscale("log")
                    ax_to_use.grid(True)
                    ax_to_use.legend(loc="upper left")

            plt.tight_layout()
            if save:
                save_plot(fig_ind, save_dir, save_format, save_dpi)
            plt.show()
                














            #for ind_name, (ind_data, params) in indicators.items():
            #    fig_ind, ax_ind = plt.subplots(1, 1, figsize=figsize)
            #    if isinstance(ind_data, pd.DataFrame):
            #        for ticker in data.keys():
            #            if ticker in ind_data.columns:
            #                series = ind_data[ticker].sort_index()
            #                if self.normalize and not series.empty:
            #                    first_valid = series.first_valid_index()
            #                    if first_valid is not None:
            #                        base_value = series.loc[first_valid]
            #                        if base_value != 0:
            #                            series = series / base_value
            #                ax_ind.plot(series.index, series, label=ticker, linewidth=1)
            #    else:
            #        series = ind_data.sort_index()
            #        if self.normalize and not series.empty:
            #            first_valid = series.first_valid_index()
            #            if first_valid is not None:
            #                base_value = series.loc[first_valid]
            #                if base_value != 0:
            #                    series = series / base_value
            #        ax_ind.plot(ind_data.index, ind_data, linewidth=1)
            #    ax_ind.set_title(
            #        f"{ind_name} Comparison{"(normalized)" if self.normalize else ""}"
            #    )
            #    ax_ind.set_ylabel(
            #        ind_name + (" (normalized)" if self.normalize else "")
            #    )
            #    if self.log_scale:
            #        ax_ind.set_yscale("log")
            #    ax_ind.grid(True)
            #    if len(data) > 1:
            #        ax_ind.legend(loc="upper left")
            #    if save:
            #        save_plot(
            #            fig_ind,
            #            save_dir,
            #            save_format,
            #            save_dpi,
            #        )
            #    plt.tight_layout()
            #    plt.show()
#