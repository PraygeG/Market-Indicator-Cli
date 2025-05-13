from typing import Dict, Tuple, Optional
from functools import reduce
import pandas as pd
import matplotlib.pyplot as plt
from stonkzilla.plots.plot_methods import save_plot


class MultiTickerPlotter:
    """
    Plot multiple tickers on the same axes, with optional normalization and log-scale.
    Only price, FIBO (if normalized), and moving averages (SMA, EMA) are supported.
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

    @staticmethod
    def align_dataframes(
        data: Dict[str, pd.DataFrame], column: str
    ) -> Dict[str, pd.Series]:
        """
        Align all ticker series to the intersection of their indexes.
        Returns a dict of ticker -> pd.Series.
        """
        indexes = [df[column].dropna().index for df in data.values()]
        if not indexes:
            common_index = pd.Index([])
        else:
            common_index = reduce(lambda a, b: a.intersection(b), indexes)
        return {
            ticker: df.loc[common_index, column].sort_index()
            for ticker, df in data.items()
        }

    @staticmethod
    def get_base_values(series_dict: Dict[str, pd.Series]) -> Dict[str, float]:
        """
        Get the first valid value for each ticker's series.
        """
        return {
            ticker: series.iloc[0] if not series.empty else 1.0
            for ticker, series in series_dict.items()
        }

    @staticmethod
    def normalize_series(series: pd.Series, base: float) -> pd.Series:
        """
        Normalize a pandas Series to its base value.
        """
        return series / base if base != 0 else series

    @staticmethod
    def normalize_and_average_fibo(
        fibo_df: pd.DataFrame, base_values: Dict[str, float]
    ) -> pd.Series:
        """
        Normalize FIBO levels for each ticker and average across tickers for each level.
        Handles both (levels as rows, tickers as columns) and vice versa.
        Returns: pd.Series with index as FIBO level and value as normalized average.
        """
        tickers = set(base_values.keys())
        # Try columns first
        fibo_cols = set(fibo_df.columns)
        fibo_idx = set(fibo_df.index)
        if tickers & fibo_cols:
            common = list(tickers & fibo_cols)
            norm = fibo_df[common].copy()
            for ticker in common:
                norm[ticker] = norm[ticker] / base_values[ticker]
            return norm.mean(axis=1)
        elif tickers & fibo_idx:
            common = list(tickers & fibo_idx)
            norm = fibo_df.loc[common].copy()
            for ticker in common:
                norm.loc[ticker] = norm.loc[ticker] / base_values[ticker]
            return norm.mean(axis=0)
        elif tickers & set(fibo_df.T.columns):
            # Try transposed columns
            fibo_df = fibo_df.T
            common = list(tickers & set(fibo_df.columns))
            norm = fibo_df[common].copy()
            for ticker in common:
                norm[ticker] = norm[ticker] / base_values[ticker]
            return norm.mean(axis=1)
        elif tickers & set(fibo_df.T.index):
            # Try transposed index
            fibo_df = fibo_df.T
            common = list(tickers & set(fibo_df.index))
            norm = fibo_df.loc[common].copy()
            for ticker in common:
                norm.loc[ticker] = norm.loc[ticker] / base_values[ticker]
            return norm.mean(axis=0)
        else:
            raise ValueError(
                f"FIBO DataFrame columns or index do not match tickers. "
                f"Tickers in price: {tickers}, "
                f"FIBO columns: {fibo_df.columns}, "
                f"FIBO index: {fibo_df.index}"
            )

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
        Plot normalized prices, FIBO overlays, and moving averages for multiple tickers.
        """
        if not data:
            raise ValueError("'data' must contain at least one ticker")
        for ticker, df in data.items():
            if column not in df.columns:
                raise ValueError(f"DataFrame for {ticker!r} has no column {column!r}.")

        # --- Data alignment and normalization ---
        price_series = self.align_dataframes(data, column)
        base_values = self.get_base_values(price_series)
        norm_prices = {
            ticker: (
                self.normalize_series(series, base_values[ticker])
                if self.normalize
                else series
            )
            for ticker, series in price_series.items()
        }

        # --- Figure setup ---
        fig, (ax_price, ax_ma) = plt.subplots(
            2, 1, figsize=figsize, sharex=True, gridspec_kw={"height_ratios": [2, 1]}
        )

        # --- Price subplot ---
        for ticker, series in norm_prices.items():
            ax_price.plot(series.index, series, label=ticker, linewidth=1.5)
        ax_price.set_title(self.title)
        ax_price.set_ylabel(column + (" (normalized)" if self.normalize else ""))
        if self.log_scale:
            ax_price.set_yscale("log")
        ax_price.grid(True)
        ax_price.legend(loc="upper left")

        # --- FIBO overlay ---
        if indicators:
            for ind_name, (ind_data, _) in indicators.items():
                if ind_name.startswith("FIBO") and self.normalize:
                    if isinstance(ind_data, pd.DataFrame):
                        fibo_avg = self.normalize_and_average_fibo(
                            ind_data, base_values
                        )
                        for level, value in fibo_avg.items():
                            ax_price.axhline(
                                y=value,
                                linestyle="--",
                                alpha=0.7,
                                label=f"FIBO {level}",
                            )
                    elif isinstance(ind_data, pd.Series):
                        mean_base = sum(base_values.values()) / len(base_values)
                        for level, value in ind_data.items():
                            ax_price.axhline(
                                y=value / mean_base,
                                linestyle="--",
                                alpha=0.7,
                                label=f"FIBO {level}",
                            )
            # Deduplicate legend
            handles, labels = ax_price.get_legend_handles_labels()
            unique = dict(zip(labels, handles))
            ax_price.legend(unique.values(), unique.keys(), loc="upper left")

        # --- Moving Averages subplot ---
        ma_plotted = False
        if indicators:
            for ind_name, (ind_data, _) in indicators.items():
                if ind_name.startswith("EMA") or ind_name.startswith("SMA"):
                    if isinstance(ind_data, pd.DataFrame):
                        for ticker, series in price_series.items():
                            if ticker in ind_data.columns:
                                ma_series = ind_data[ticker].reindex(series.index)
                                if self.normalize:
                                    ma_series = self.normalize_series(
                                        ma_series, base_values[ticker]
                                    )
                                ax_ma.plot(
                                    ma_series.index,
                                    ma_series,
                                    label=f"{ticker} {ind_name}",
                                    linewidth=1,
                                )
                                ma_plotted = True
        if ma_plotted:
            ax_ma.set_title("Moving Averages")
            ax_ma.set_ylabel("MA Value" + (" (normalized)" if self.normalize else ""))
            ax_ma.grid(True)
            ax_ma.legend(loc="upper left")
        else:
            ax_ma.set_visible(False)

        plt.tight_layout()
        if save:
            save_plot(fig, save_dir, save_format, save_dpi)
        else:
            plt.show()
