import pandas as pd
from stonkzilla.indicators.base_indicator import BaseIndicator


class EMA(BaseIndicator):
    """
    Exponential moving average
    """

    def __init__(self, window: int, column: str = "Close") -> None:
        """Initialize EMA indicator."""
        super().__init__(column)
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate the exponential moving average."""
        if self.column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.column}' column")
        result = data[self.column].ewm(span=self.window, adjust=False).mean()
        result.index = data.index
        return result
