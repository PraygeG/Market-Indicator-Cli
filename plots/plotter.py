import matplotlib.pyplot as plt
import pandas as pd

class Plotter:

    def __init__(self, title: str = "Stock Data with Indicators"):
        self.title = title

    def plot(self, data: pd.DataFrame, indicators: dict, column: str = 'Close', company_name: str = "Unknown"):
        if column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{column}' column.")
        
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data[column], label=column, color='blue', linewidth=1.5)

        # Overlay indicators
        for name, (series, params) in indicators.items():
            series = series.dropna()
            param_str = ",".join(map(str, params))
            plt.plot(series.index, series, label=f"{name} ({param_str})", linewidth=1.2)

        plt.title(f"{self.title} - {company_name}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid()
        plt.show()

