import click
from cli.cli_handler import CLIHanlder
from services.data_fetcher import DataFetcher
from services.indicator_runner import IndicatorRunner
from services.plot_service import PlotService


@click.command()
@click.option(
    "--tickers", default=None, help="Comma-separated list of tickers (e.g., AAPL, MSFT)"
)
@click.option("--start-date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD)")
@click.option(
    "--interval",
    default=None,
    help="""Interval in which data is downloaded. 
Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo Intraday data cannot extend last 60 days.""",
)
@click.option(
    "--indicators",
    default=None,
    help="Comma-separated list of indicators (e.g., RSI:14,EMA:50,SMA:100,MACD:12-26-9)",
)
@click.option(
    "--data-source", default="yfinance", help="Data source to use (default: yfinance)"
)
@click.option("--api-key", default=None, help="API key for AlphaVantage data source")
@click.option(
    "--column",
    default="Close",
    help="Column to use for calculations (e.g., Open, High, Low, Close, Volume)",
)
@click.option(
    "--plot-style",
    default="line",
    type=click.Choice(["line", "candlestick"]),
    help="Chart visualization style (default: line)",
)
@click.option(
    "--color-scheme",
    default="default",
    type=click.Choice(["default", "monochrome", "tradingview", "dark"]),
    help="Color scheme for the chart (default: default)",
)
@click.option(
    "--up-color",
    default=None,
    help="Custom color for up candles/bars (overrides color scheme)",
)
@click.option(
    "--down-color",
    default=None,
    help="Custom color for down candles/bars (overrides color scheme)",
)
@click.option("--save", is_flag=True, help="Save the plot(s) to file automatically. ")
@click.option("--save-dir", default=None, help="Directory to save plots")
@click.option(
    "--save-format",
    default="png",
    type=click.Choice(["png", "pdf", "svg", "jpg"]),
    help="Format to save (png, pdf, svg, jpg)",
)
@click.option("--save-dpi", default=None, type=int, help="DPI for raster formats")
def cli(
    tickers,
    start_date,
    end_date,
    interval,
    indicators,
    data_source,
    api_key,
    column,
    plot_style,
    color_scheme,
    up_color,
    down_color,
    save,
    save_dir,
    save_format,
    save_dpi,
):
    try:
        config = CLIHanlder().get_config(
            tickers, start_date, end_date, interval, indicators, data_source, column
        )
    except Exception as e:
        print(f"Configuration error: {e}")
        return

    fetcher = DataFetcher(config["data_source"])
    indicator_runner = IndicatorRunner()
    plot_service = PlotService()

    all_data = fetcher.fetch_all(
        config["tickers"], config["start_date"], config["end_date"], config["interval"]
    )

    for ticker, data in all_data.items():
        if data.empty:
            print(f"No data found for {ticker}. Skipping...")
            continue
        indicators = indicator_runner.run(data, config["indicators"], config["column"])
        plot_service.plot(
            data,
            indicators,
            config["column"],
            ticker,
            plot_style=plot_style,
            color_scheme=color_scheme,
            up_color=up_color,
            down_color=down_color,
            save=save,
            save_dir=save_dir,
            save_format=save_format,
            save_dpi=save_dpi,
            interval=config["interval"],
            start_date=config["start_date"],
            end_date=config["end_date"],
        )


if __name__ == "__main__":
    cli()
