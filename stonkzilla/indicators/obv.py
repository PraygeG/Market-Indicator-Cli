import pandas as pd
from stonkzilla.indicators.base_indicator import BaseIndicator


class OBV(BaseIndicator):
    """
    On balance volume
    """

    def __init__(self) -> None:
        """Initialize OBV indicator."""
        super().__init__(column=None)

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate the OBV indicator."""
        if "Close" not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column")
        if "Volume" not in data.columns:
            raise ValueError("DataFrame must contain a 'Volume' column")

        direction = data["Close"].diff().fillna(0)
        direction = (direction > 0).astype(int) - (direction < 0).astype(int)
        volume_flow = direction * data["Volume"]
        obv = volume_flow.cumsum()
        obv.name = "OBV"
        return obv
