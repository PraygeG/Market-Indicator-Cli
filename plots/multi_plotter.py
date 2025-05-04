from typing import Dict, Tuple, Optional, Sequence
import pandas as pd
import matplotlib.pyplot as plt


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
        plt.show()

        # Indicator plots
        if indicators:
            for ind_name, (ind_data, params) in indicators.items():
                fig_ind, ax_ind = plt.subplots(1, 1, figsize=figsize)

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
                            ax_ind.plot(series.index, series, label=ticker, linewidth=1)
                else:
                    series = ind_data.sort_index()
                    if self.normalize and not series.empty:
                        first_valid = series.first_valid_index()
                        if first_valid is not None:
                            base_value = series.loc[first_valid]
                            if base_value != 0:
                                series = series / base_value
                    ax_ind.plot(ind_data.index, ind_data, linewidth=1)

                ax_ind.set_title(f"{ind_name} Comparison{"(normalized)" if self.normalize else ""}")
                ax_ind.set_ylabel(ind_name + (" (normalized)" if self.normalize else ""))
                if self.log_scale:
                    ax_ind.set_yscale("log")
                ax_ind.grid(True)
                if len(data) > 1:
                    ax_ind.legend(loc="upper left")
                plt.tight_layout()
                plt.show()
