import matplotlib.pyplot as plt
import pandas as pd
from plots.base_plotter import BasePlotter


class Plotter(BasePlotter):

    def __init__(
        self,
        title: str = "Stock Data with Indicators",
        color_scheme: str = "default",
        up_color: str = None,
        down_color: str = None,
    ):
        super().__init__(title, color_scheme, up_color, down_color)

    def plot(
        self,
        data: pd.DataFrame,
        indicators: dict,
        column: str = "Close",
        company_name: str = "Unknown",
        save: bool = False,
        save_dir: str = None,
        save_format: str = "png",
        save_dpi: int = 300,
        interval: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        if column not in data.columns:
            raise ValueError(f"DataFrame must contain a '{column}' column.")

        has_macd = any("MACD" in name for name in indicators)
        has_bbands = any("BBANDS" in name for name in indicators)
        has_rsi = any(name.startswith("RSI") for name in indicators)
        has_obv = any(name.startswith("OBV") for name in indicators)
        has_adx = any(name.startswith("ADX") for name in indicators)
        subplot_count = 1 + has_macd + has_bbands + has_rsi + has_obv
        fig, axes = plt.subplots(
            subplot_count,
            1,
            figsize=(12, 6 + 2 * subplot_count),
            gridspec_kw={"height_ratios": [3] + [1] * (subplot_count - 1)},
        )

        if subplot_count == 1:
            axes = [axes]

        self.apply_color_scheme(fig, axes)
        fig.suptitle(f"{self.title} - {company_name}", color=self.scheme["text"])

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
        if has_obv:
            current_index += 1
        ax_adx = axes[current_index] if has_adx else None

        ax_price.plot(
            data.index,
            data[column],
            label=column,
            color=self.scheme["up"],
            linewidth=1.5,
        )
        for name, (series, params) in indicators.items():
            if (
                name.startswith("MACD")
                or name.startswith("BBANDS")
                or name.startswith("RSI")
                or name.startswith("OBV")
            ):
                continue
            ax_price.plot(series.index, series, label=f"{name} ", linewidth=1)
        ax_price.set_label("Price")
        ax_price.legend()
        ax_price.grid(color=self.scheme.get("grid", None))

        if has_macd:
            macd_key = next(name for name in indicators if "MACD" in name)
            macd_data, params = indicators[macd_key]
            self.plot_macd(ax_macd, macd_data, params)

        if has_bbands:
            bbands_key = next(name for name in indicators if "BBANDS" in name)
            bbands_data, params = indicators[bbands_key]
            self.plot_bbands(ax_bbands, bbands_data, params)

        if has_rsi:
            rsi_key = next(name for name in indicators if name.startswith("RSI"))
            rsi_data, params = indicators[rsi_key]
            self.plot_rsi(ax_rsi, rsi_data, params)

        if has_obv:
            obv_key = next(name for name in indicators if name.startswith("OBV"))
            obv_data, _ = indicators[obv_key]
            self.plot_obv(ax_obv, obv_data)

        if has_adx:
            adx_key = next(name for name in indicators if name.startswith("ADX"))
            adx_data, params = indicators[adx_key]
            self.plot_adx(ax_adx, adx_data, params)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save plots to file logic
        if save:
            self.save_plot(
                fig,
                save_dir=save_dir,
                save_format=save_format,
                save_dpi=save_dpi,
                ticker=company_name,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
            )

        plt.show()
