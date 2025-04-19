import pandas as pd
from indicators.base_indicator import BaseIndicator

class OBV(BaseIndicator):
    """
    On balance volume
    """
    def __init__(self, price_column = 'Close', volume_column = 'Volume'):
        super().__init__(price_column)
        self.volume_column = volume_column

    def calculate(self, data: pd.DataFrame)-> pd.Series:
        if self.column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.column}' column")
        if self.volume_column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{self.volume_column}' column")
        
        direction = data[self.column].diff()
        direction = (direction > 0).astype(int) - (direction < 0).astype(int)

        volume_flow = direction * data[self.volume_column]
        obv = volume_flow.cumsum()
        
        return obv