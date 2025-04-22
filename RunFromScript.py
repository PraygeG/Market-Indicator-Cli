from cli.cli_handler import CLIHanlder
from services.data_fetcher import DataFetcher
from services.indicator_runner import IndicatorRunner
from services.plot_service import PlotService


def main():
    try:
        config = CLIHanlder().get_config()
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
    main()
