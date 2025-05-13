import pandas as pd
import numpy as np
from stonkzilla.indicators.base_indicator import BaseIndicator


class ADX(BaseIndicator):
    """
    Average Directional Index (ADX)
    """

    def __init__(
        self,
        window: int = 14,
    ) -> None:
        """Initialize ADX indicator."""
        super().__init__(column=None)
        if not isinstance(window, int) or window <= 1:
            raise ValueError("Window must be an integer greater than 1.")
        self.window: int = window

    def _wilders_smoothing(self, series: pd.Series, window: int) -> pd.Series:
        """Apply Wilder's smoothing to a series."""
        if not isinstance(series, pd.Series):
            series = pd.Series(series)
        return series.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate the ADX, +DI, and -DI values."""
        data = data.copy()
        required_columns: list[str] = ["High", "Low", "Close"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError("DataFrame is missing columns for adx calculation.")

        high: pd.Series = data["High"]
        low: pd.Series = data["Low"]
        close: pd.Series = data["Close"]

        high_vals: np.ndarray = high.values.ravel()
        low_vals: np.ndarray = low.values.ravel()

        # Calculate Directional Movement
        move_up_vals: np.ndarray = np.concatenate(([np.nan], np.diff(high_vals)))
        move_down_vals: np.ndarray = np.concatenate(([np.nan], np.diff(low_vals)))

        plus_dm_vals: np.ndarray = np.where(
            (move_up_vals > move_down_vals) * (move_up_vals > 0), move_up_vals, 0.0
        )
        minus_dm_vals: np.ndarray = np.where(
            (move_down_vals > move_up_vals) & (move_down_vals > 0), move_down_vals, 0.0
        )
        plus_dm_vals: np.ndarray = np.nan_to_num(plus_dm_vals, nan=0.0)
        minus_dm_vals: np.ndarray = np.nan_to_num(minus_dm_vals, nan=0.0)

        plus_dm: pd.Series = pd.Series(plus_dm_vals, index=data.index)
        minus_dm: pd.Series = pd.Series(minus_dm_vals, index=data.index)

        # Calculate true range (TR)
        high_low: pd.Series = high - low
        high_close_prev: pd.Series = abs(high - close.shift(1))
        low_close_prev: pd.Series = abs(low - close.shift(1))

        tr_df = pd.concat([high_low, high_close_prev, low_close_prev], axis=1)
        tr: pd.Series = tr_df.max(axis=1)
        if len(tr) > 0:
            tr.iloc[0] = high.iloc[0] - low.iloc[0] if len(tr) > 0 else np.nan
        tr = tr.fillna(0.0)

        # Smoothing
        # Smooth +DM, -DM and TR
        smooth_plus_dm: pd.Series = self._wilders_smoothing(plus_dm, self.window)
        smooth_minus_dm: pd.Series = self._wilders_smoothing(minus_dm, self.window)
        atr: pd.Series = self._wilders_smoothing(tr, self.window)

        # Calculate directional indicators (+DI, -DI)
        atr_safe: pd.Series = atr.replace(0, np.nan)

        plus_di: pd.Series = 100 * (smooth_plus_dm / atr_safe)
        minus_di: pd.Series = 100 * (smooth_minus_dm / atr_safe)

        plus_di = plus_di.fillna(0)
        minus_di = minus_di.fillna(0)

        di_sum: pd.Series = plus_di + minus_di
        di_sum_safe: pd.Series = di_sum.replace(0, np.nan)

        dx: pd.Series = 100 * (abs(plus_di - minus_di) / di_sum_safe)

        dx = dx.fillna(0)

        adx: pd.Series = self._wilders_smoothing(dx, self.window)

        result_df = pd.DataFrame({"plus_di": plus_di, "minus_di": minus_di, "adx": adx})

        return result_df
