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
@click.option(
    "--column",
    default="Close",
    help="Column to use for calculations (e.g., Open, High, Low, Close, Volume)",
)
def cli(tickers, start_date, end_date, interval, indicators, data_source, column):
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
        plot_service.plot(data, indicators, config["column"], ticker)

if __name__ == "__main__":
    cli()