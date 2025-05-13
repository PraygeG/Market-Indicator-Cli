import pandas as pd
from stonkzilla.indicators.base_indicator import BaseIndicator


class MACD(BaseIndicator):
    """
    Moving average convergence/divergence
    """

    def __init__(
        self,
        short_window: int = 12,
        long_window: int = 26,
        signal_window: int = 9,
        column: str = "Close",
    ) -> None:
        """Initialize MACD indicator."""
        super().__init__(column)
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate the MACD indicator."""
        if self.column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.column}' column.")

        short_ema = data[self.column].ewm(span=self.short_window, adjust=False).mean()
        long_ema = data[self.column].ewm(span=self.long_window, adjust=False).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=self.signal_window, adjust=False).mean()

        result = pd.DataFrame(index=data.index)
        result["MACD"] = macd_line
        result["Signal"] = signal_line

        return result
