import pandas as pd
from stonkzilla.indicators.base_indicator import BaseIndicator


class BBANDS(BaseIndicator):
    """
    Bollinger bands
    """

    def __init__(
        self, window: int, standard_dev_num: int, column: str = "Close"
    ) -> None:
        """Initialize BBANDS indicator."""
        super().__init__(column)
        self.window = window
        self.standard_dev_num = standard_dev_num

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate the Bollinger Bands indicator."""
        if self.column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.column}' column.")

        middle_band = data[self.column].rolling(window=self.window).mean()
        std_deviation = data[self.column].rolling(window=self.window).std()
        upper_band = middle_band + (self.standard_dev_num * std_deviation)
        lower_band = middle_band - (self.standard_dev_num * std_deviation)

        result = pd.DataFrame(index=data.index)
        result["middle_band"] = middle_band
        result["upper_band"] = upper_band
        result["lower_band"] = lower_band

        return result
