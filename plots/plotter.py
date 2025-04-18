import matplotlib.pyplot as plt
import pandas as pd

class Plotter:

    def __init__(self, title: str = "Stock Data with Indicators"):
        self.title = title

    def plot(self, data: pd.DataFrame, indicators: dict, column: str = 'Close'):
        if column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{column}' column.")
        
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data[column], label=column, color='blue', linewidth=1.5)

        # Overlay indicators
        for name, series in indicators.items():
            series = series.dropna()
            plt.plot(series.index, series, label=name, linewidth=1.2)

        plt.title(self.title)
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid()
        plt.show()