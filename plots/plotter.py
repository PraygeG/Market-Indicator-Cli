import matplotlib.pyplot as plt
import pandas as pd

class Plotter:

    def __init__(self, title: str = "Stock Data with Indicators"):
        self.title = title

    def plot(self, data: pd.DataFrame, indicators: dict, column: str = 'Close', company_name: str = "Unknown"):
        if column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{column}' column.")

        has_macd = "MACD" in indicators

        if has_macd:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios':[3, 1]})
            ax_price = ax1
            ax_macd = ax2
        else:
            fig, ax_price = plt.subplots(figsize=(12, 6))
            ax_macd = None

        fig.suptitle(f"{self.title} - {company_name}")

        ax_price.plot(data.index, data[column], label=column, color='blue', linewidth=1.5)
        for name, (series, params) in indicators.items():
            if name != "MACD":
                series = series.dropna()
                param_str = ",".join(map(str, params))
                ax_price.plot(series.index, series, label=f"{name} ({param_str})", linewidth=1.2)
        ax_price.set_label("Price")
        ax_price.legend()
        ax_price.grid()

        if has_macd:
            macd_data, params = indicators["MACD"]
            macd_line = macd_data["MACD"]
            signal_line = macd_data["Signal"]
            ax_macd.plot(macd_data.index, macd_line, label="MACD Line", color='orange', linewidth=1.2)
            ax_macd.plot(macd_data.index, signal_line, label="Signal Line", color='green', linewidth=1.2)
            ax_macd.axhline(0, color='gray', linestyle='--', linewidth=0.8)
            ax_macd.set_ylabel("MACD")
            ax_macd.legend()
            ax_macd.grid()

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()











        #plt.figure(figsize=(12, 6))
        #plt.plot(data.index, data[column], label=column, color='blue', linewidth=1.5)
        ## Overlay indicators
        #for name, (series, params) in indicators.items():
        #    series = series.dropna()
        #    param_str = ",".join(map(str, params))
        #    plt.plot(series.index, series, label=f"{name} ({param_str})", linewidth=1.2)
#
        #plt.title(f"{self.title} - {company_name}")
        #plt.xlabel("Date")
        #plt.ylabel("Price")
        #plt.legend()
        #plt.grid()
        #plt.show()

