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
        df = data.copy()

        required_cols = [self.high_column, self.low_column, self.close_column]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(
                f"Input DataFrame missing required columns: {required_cols}"
            )

        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(subset=required_cols, inplace=True)
        if df.empty:
            print(f"DataFrame is empty after handling non-numeric data or NaNs.")
            return pd.DataFrame(columns=["plus_DI", "minus_DI", "ADX"])

        # Calculate True Range (max of 3 different differencials)
        df["TR1"] = df[self.high_column] - df["Low"]
        df["TR2"] = abs(df["High"] - df["Close"].shift(1))
        df["TR3"] = abs(df["Low"] - df["Close"].shift(1))
        df["TR"] = df[["TR1", "TR2", "TR3"]].max(axis=1)
        df.drop(columns=["TR1", "TR2", "TR3"], inplace=True)

        # Calculate Directional Movement (+DM and -DM)
        # +DM = curr High - prev High if > prev Low - curr Low and > 0
        # -DM = prev Low - curr Low if > curr High - prev High and > 0
        move_up = df[self.high_column] - df[self.high_column].shift(1)
        move_down = df[self.low_column].shift(1) - df[self.low_column]
        plus_DM = move_up.clip(lower=0)
        minus_DM = move_down.clip(lower=0)

        # If move_up > move_down, use plus_DM, otherwise 0
        # if move_down > move_up, use minus_DM, oterwise 0
        df["plus_DM"] = np.where((move_up > move_down) & (move_up > 0), move_up, 0)
        df["minus_DM"] = np.where((move_down > move_up) & (move_down > 0), move_down, 0)

        # Apply Wilder's Smoothing (type of EMA)
        # SMV = Previous_SMV - (Previous_SMV / window) + Current_Value
        # or SMV = (Previous_SMV * (window - 1) + Current_Value) / window

        def wilders_smoothing_series(series: pd.Series):
            series = series.astype(float)
            # Calculate the first sum (for the value at index window - 1)
            first_smoothed_val = series.iloc[: self.window].sum()

            smv = pd.Series(np.nan, index=series.index)

            if len(series) >= self.window:
                smv.iloc[self.window - 1] = first_smoothed_val
                for i in range(self.window, len(series)):
                    if pd.isna(smv.iloc[i - 1]) or pd.isna(series.iloc[i]):
                        smv.iloc[i] = np.nan
                    else:
                        smv.iloc[i] = (
                            smv.iloc[i - 1] * (self.window - 1) + series.iloc[i]
                        ) / self.window
            return smv

        df["Smoothed_TR"] = wilders_smoothing_series(df["TR"])
        df["Smoothed_plus_DM"] = wilders_smoothing_series(df["plus_DM"])
        df["Smoothed_minus_DM"] = wilders_smoothing_series(df["minus_DM"])

        # Calculate Directional Indicators
        df["plus_DI"] = (df["Smoothed_plus_DM"] / df["Smoothed_TR"]) * 100
        df["minus_DI"] = (df["Smoothed_minus_DM"] / df["Smoothed_TR"]) * 100

        # Handle potential division by 0 if Smoothed_TR is 0
        df["plus_DI"] = np.where(
            df["Smoothed_TR"] != 0,
            (df["Smoothed_plus_DM"] / df["Smoothed_TR"]) * 100,
            0,
        )
        df["minus_DI"] = np.where(
            df["Smoothed_TR"] != 0,
            (df["Smoothed_minus_DM"] / df["Smoothed_TR"]) * 100,
            0,
        )

        # Calculate Directional Index (DX)
        di_diff = abs(df["plus_DI"] - df["minus_DI"])
        di_sum = df["plus_DI"] + df["minus_DI"]
        # Use np.where for save division
        df["DX"] = np.where(di_sum != 0, (di_diff / di_sum) * 100, 0)

        # Average Directional Index
        df["ADX"] = wilders_smoothing_series(df["DX"])

        df = df.drop(
            columns=[
                "TR",
                "plus_DM",
                "minus_DM",
                "Smoothed_TR",
                "Smoothed_plus_DM",
                "Smoothed_minus_DM",
                "DX",
            ]
        )

        return df[["plus_DI", "minus_DI", "ADX"]]
