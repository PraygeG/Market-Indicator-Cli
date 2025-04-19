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
        has_rsi = any(name.startswith("RSI") for name in indicators)
        has_obv = any(name.startswith("OBV") for name in indicators)
        subplot_count = 1 + has_macd + has_bbands + has_rsi + has_obv
        fig, axes = plt.subplots(subplot_count, 1, figsize=(12, 6 + 2 * subplot_count), gridspec_kw={'height_ratios': [3] + [1] * (subplot_count - 1)})
        

        if subplot_count == 1:
            axes = [axes]
            

        ax_price = axes[0]
        current_index = 1
        ax_macd = axes[current_index] if has_macd else None
        if has_macd:
            current_index += 1
        ax_bbands = axes[current_index] if has_bbands else None
        if has_bbands:
            current_index += 1
        ax_rsi = axes[current_index] if has_rsi else None
        if has_rsi:
            current_index += 1
        ax_obv = axes[current_index] if has_obv else None

        fig.suptitle(f"{self.title} - {company_name}")

        ax_price.plot(data.index, data[column], label=column, color='blue', linewidth=1.5)
        for name, (series, params) in indicators.items():
            if "MACD" in name or "BBANDS" in name or "RSI" in name or "OBV":
                continue
            series = series.dropna()
            param_str = ",".join(map(str, params))
            ax_price.plot(series.index, series, label=f"{name}", linewidth=1)
        ax_price.set_label("Price")
        ax_price.legend()
        ax_price.grid()

        if has_macd:
            macd_key = next(name for name in indicators if "MACD" in name)
            macd_data, params = indicators[macd_key]
            macd_line = macd_data["MACD"]
            signal_line = macd_data["Signal"]
            histogram = macd_line - signal_line
            ax_macd.plot(macd_data.index, macd_line, label="MACD Line", color='orange', linewidth=1.2)
            ax_macd.plot(macd_data.index, signal_line, label="Signal Line", color='green', linewidth=1.2)
            positive_color = 'green'
            negative_color = 'red'
            colors = [positive_color if value > 0 else negative_color for value in histogram]
            ax_macd.bar(macd_data.index, histogram, label="Histogram", color=colors, alpha=0.7, width=1)
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

        if has_rsi:
            rsi_key = next(name for name in indicators if name.startswith("RSI"))
            rsi_data, params = indicators[rsi_key]
            ax_rsi.plot(rsi_data.index, rsi_data, label=f"RSI {params}", color='purple', linewidth=1.2)
            ax_rsi.axhline(70, color='red', linestyle='--', linewidth=0.8, label="Overbought")
            ax_rsi.axhline(30, color='green', linestyle='--', linewidth=0.8, label="Oversold")
            ax_rsi.set_ylabel("RSI")
            ax_rsi.legend()
            ax_rsi.grid()

        if has_obv:
            obv_key = next(name for name in indicators if name.startswith("OBV"))
            obv_data, _ = indicators[obv_key]
            ax_obv.plot(obv_data.index, obv_data, label="On balance volume", color='green' , linewidth=1)
            ax_obv.set_ylabel("OBV")
            ax_obv.legend()
            ax_obv.grid()

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()










