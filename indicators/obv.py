import pandas as pd
from indicators.base_indicator import BaseIndicator


class OBV(BaseIndicator):
    """
    On balance volume
    """

    def __init__(self, column: str):
        super().__init__(column=None)

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        if "Close" not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.column}' column")
        if "Volume" not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.volume_column}' column")

        direction = data["Close"].diff()
        direction = (direction > 0).astype(int) - (direction < 0).astype(int)

        volume_flow = direction * data["Volume"]
        obv = volume_flow.cumsum()

        return obv
