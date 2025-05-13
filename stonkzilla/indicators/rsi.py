import pandas as pd
from stonkzilla.indicators.base_indicator import BaseIndicator


class RSI(BaseIndicator):
    """
    Relative Strength Index
    """

    def __init__(self, window: int, column: str = "Close") -> None:
        """Initialize RSI indicator."""
        super().__init__(column)
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate the RSI indicator."""
        if self.column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.column}' column")

        delta = data[self.column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi
