from plots.plotter import Plotter
from plots.candlestick_plotter import CandlestickPlotter


class PlotService:
    def __init__(self):
        pass

    def plot(
        self,
        data,
        indicators,
        column,
        ticker,
        plot_style="line",
        color_scheme="default",
        up_color=None,
        down_color=None,
        save=False,
        save_dir=None,
        save_format="png",
        save_dpi=300,
        interval=None,
        start_date=None,
        end_date=None,
    ):
        title = f"Stock analysis for {ticker}"

        if plot_style == "candlestick":
            plotter = CandlestickPlotter(
                title=title,
                color_scheme=color_scheme,
                up_color=up_color,
                down_color=down_color,
            )
        else:
            plotter = Plotter(
                title="Stock Data with indicators",
                color_scheme=color_scheme,
                up_color=up_color,
                down_color=down_color,
            )

        plotter.plot(
            data,
            indicators,
            column,
            ticker,
            save=save,
            save_dir=save_dir,
            save_format=save_format,
            save_dpi=save_dpi,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )
