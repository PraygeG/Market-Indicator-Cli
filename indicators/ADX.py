import pandas as pd
import numpy as np
from indicators.base_indicator import BaseIndicator


class ADX(BaseIndicator):
    """
    Average Directional Index (ADX)
    """

    def __init__(
        self,
        window: int = 14,
        close_column: str = "Close",
        high_column: str = "High",
        low_column: str = "Low",
    ):
        super().__init__(close_column)
        self.window = window
        self.high_column = high_column
        self.low_column = low_column
        self.close_column = close_column

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        result = pd.DataFrame(index=data.index)

        try:
            high_data, low_data, close_data = self._extract_price_data(data)
            df = pd.DataFrame(
                {
                    "High": pd.to_numeric(high_data, errors="coerce"),
                    "Low": pd.to_numeric(low_data, errors="coerce"),
                    "Close": pd.to_numeric(close_data, errors="coerce"),
                },
                index=data.index,
            )
            df.dropna(inplace=True)

            if df.empty:
                return pd.DataFrame(
                    columns=["plus_DI", "minus_DI", "ADX"], index=data.index
                )

            # Calculate True Range and Directional Movement
            high_shift = df["High"].shift(1)
            low_shift = df["Low"].shift(1)
            close_shift = df["Close"].shift(1)

            tr1 = df["High"] - df["Low"]
            tr2 = (df["High"] - close_shift).abs()
            tr3 = (df["Low"] - close_shift).abs()

            df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            up_move = df["High"] - high_shift
            down_move = low_shift - df["Low"]

            df["plus_DM"] = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
            df["minus_DM"] = np.where(
                (down_move > up_move) & (down_move > 0), down_move, 0
            )

            # Apply smoothing
            df["smoothed_TR"] = self._wilders_smoothing(df["TR"])
            df["smoothed_plus_DM"] = self._wilders_smoothing(df["plus_DM"])
            df["smoothed_minus_DM"] = self._wilders_smoothing(df["minus_DM"])

            df["plus_DI"] = np.where(
                df["smoothed_TR"] > 0,
                (df["smoothed_plus_DM"] / df["smoothed_TR"]) * 100,
                0,
            )
            df["minus_DI"] = np.where(
                df["smoothed_TR"] > 0,
                (df["smoothed_minus_DM"] / df["smoothed_TR"]) * 100,
                0,
            )

            # Calculate DX
            di_diff = abs(df["plus_DI"] - df["minus_DI"])
            di_sum = df["plus_DI"] + df["minus_DI"]
            df["DX"] = np.where(di_sum > 0, (di_diff / di_sum) * 100, 0)

            # Calculate ADX
            df["ADX"] = w(df["DX"], self.window)

            result = pd.DataFrame(index=data.index)
            result.loc[df.index, "ADX"] = df["ADX"]
            result.loc[df.index, "plus_DI"] = df["plus_DI"]
            result.loc[df.index, "minus_DI"] = df["minus_DI"]

            return result

        except Exception as e:
            print(f"Error calculating ADX: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame(
                columns=["plus_DI", "minus_DI", "ADX"], index=data.index
            )

    def _extract_price_data(self, data: pd.DataFrame):
        if isinstance(data.columns, pd.MultiIndex):
            high_col = self._find_matching_column(data.columns, self.high_column)
            low_col = self._find_matching_column(data.columns, self.low_column)
            close_col = self._find_matching_column(data.columns, self.close_column)

            if not all([high_col, low_col, close_col]):
                missing = []
                if not high_col:
                    missing.append(self.high_column)
                if not low_col:
                    missing.append(self.low_column)
                if not close_col:
                    missing.append(self.close_column)
                raise ValueError(
                    f"Could not find required columns in MultiIndex: {','.join(missing)}"
                )
            print(f"Using columns: High={high_col}, Low={low_col}, Close={close_col}")

            try:
                high_series = data[high_col]
                low_series = data[low_col]
                close_series = data[close_col]
                return high_series, low_series, close_series
            except Exception as e:
                print(f"Error extracting data from MultiIndex: {e}")
                raise
        else:
            required_cols = [self.high_column, self.low_column, self.close_column]
            missing_cols = [col for col in required_cols if col not in data.columns]

            if missing_cols:
                raise ValueError(f"DataFrame missing required columns: {missing_cols}")

            return (
                data[self.high_column],
                data[self.low_column],
                data[self.close_column],
            )

    def _find_matching_column(self, columns, column_name):
        if column_name in columns:
            return column_name

        matches = [col for col in columns if column_name if str(col)]
        return matches[0] if matches else None

    def _wilders_smoothing(self, series: pd.Series) -> pd.Series:
        series = pd.Series(series).astype(float)

        smoothed = pd.Series(index=series.index, dtype=float)

        if len(series) >= self.window:
            smoothed.iloc[self.window - 1] = (
                series.iloc[: self.window].mean() * self.window
            )

            for i in range(self.window, len(series)):
                smoothed.iloc[i] = (
                    smoothed.iloc[i - 1]
                    - (smoothed.iloc[i - 1] / self.window)
                    + series.iloc[i]
                )

        smoothed = smoothed / self.window
        return smoothed
