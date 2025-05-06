from indicators.base_indicator import BaseIndicator
import pandas as pd


class FibonacciRetracement(BaseIndicator):
    def __init__(
        self,
        *ratios: float | list[float],
    ):
        super().__init__(column=None)
        self.high_col = "High"
        self.low_col = "Low"
        self.ratios = ratios

        if isinstance(ratios, (int, float)):
            self.ratios = [float(ratios)]
        elif isinstance(ratios, list) and ratios:
            self.ratios = [float(r) for r in ratios]

    def calculate(self, data: pd.DataFrame) -> pd.  DataFrame:
        if self.high_col not in data or self.low_col not in data:
            raise ValueError(
                f"Data must contain '{self.high_col}' and '{self.low_col}' columns."
            )

        high = data[self.high_col].max()
        low = data[self.low_col].min()
        diff = high - low
        
        level_values = {
            f"fib_{int(r*1000)/10:.1f}%": high - diff * r
            for r in self.ratios
        }

        levels_df = pd.DataFrame(level_values, index=data.index)

        return levels_df
