import pandas as pd
from indicators.base_indicator import BaseIndicator


class SMA(BaseIndicator):
    """
    Simple moving average
    """

    def __init__(self, window: int, column: str = "Close"):
        super().__init__(column)
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        if self.column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.column}' column")
        result = data[self.column].rolling(window=self.window).mean()
        result.index = data.index
        return result
