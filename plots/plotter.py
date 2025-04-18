import matplotlib.pyplot as plt
import pandas as pd

class Plotter:

    def __init__(self, title: str = "Stock Data with Indicators"):
        self.title = title

    def plot(self, data: pd.DataFrame, indicators: dict, column: str = 'Close', company_name: str = "Unknown"):
        if column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{column}' column.")

        has_macd = any("MACD" in name for name in indicators)
        has_bbands = any("BBANDS" in name for name in indicators)

        subplot_count = 1 + has_macd + has_bbands
        fig, axes = plt.subplots(subplot_count, 1, figsize=(12, 6 + 2 * subplot_count), gridspec_kw={'height_ratios': [3] + [1] * (subplot_count - 1)})

        if subplot_count == 1:
            axes = [axes]
            
        ax_price = axes[0]
        ax_macd = axes[1] if has_macd else None
        ax_bbands = axes[2] if has_bbands else (axes[1] if has_bbands and not has_macd else None)

        fig.suptitle(f"{self.title} - {company_name}")

        ax_price.plot(data.index, data[column], label=column, color='blue', linewidth=1.5)
        for name, (series, params) in indicators.items():
            if "MACD" in name or "BBANDS" in name:
                continue
            series = series.dropna()
            param_str = ",".join(map(str, params))
            ax_price.plot(series.index, series, label=f"{name} ({param_str})", linewidth=1)
        ax_price.set_label("Price")
        ax_price.legend()
        ax_price.grid()

        if has_macd:
            macd_key = next(name for name in indicators if "MACD" in name)
            macd_data, params = indicators[macd_key]
            macd_line = macd_data["MACD"]
            signal_line = macd_data["Signal"]
            ax_macd.plot(macd_data.index, macd_line, label="MACD Line", color='orange', linewidth=1.2)
            ax_macd.plot(macd_data.index, signal_line, label="Signal Line", color='green', linewidth=1.2)
            ax_macd.axhline(0, color='gray', linestyle='--', linewidth=0.8)
            ax_macd.set_ylabel("MACD")
            ax_macd.legend()
            ax_macd.grid()

        if has_bbands:
            bbands_key = next(name for name in indicators if "BBANDS" in name)
            bbands_data, params = indicators[bbands_key]
            upper_band = bbands_data["upper_band"]
            lower_band = bbands_data["lower_band"]
            middle_band = bbands_data["middle_band"]
            ax_bbands.plot(bbands_data.index, middle_band, label="Middle Band", color='blue', linewidth=1.2)
            ax_bbands.plot(bbands_data.index, upper_band, label="Upper Band", color='red', linestyle='--', linewidth=1.2)
            ax_bbands.plot(bbands_data.index, lower_band, label="Lower Band", color='green', linestyle='--', linewidth=1.2)
            ax_bbands.fill_between(bbands_data.index, lower_band, upper_band, color='grey', alpha=0.3)
            ax_bbands.set_ylabel("BBANDS")
            ax_bbands.legend()
            ax_bbands.grid()

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()










