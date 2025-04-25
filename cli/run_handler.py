import click
from cli.options import common_options
from cli.services import fetch_all_data, run_indicators, plot_data
from validators.input_and_validation import (
    get_valid_date,
    get_valid_indicators,
    get_valid_interval,
    get_valid_tickers,
    validate_date_range,
)


def _build_config(
    tickers: list[str] = None,
    start_date: str = None,
    end_date: str = None,
    interval: str = None,
    indicators: list[tuple[str, list[int]]] = None,
    data_source: str = "yfinance",
    column: str = "Close",
    **kwargs,
):
    tickers = get_valid_tickers(tickers)
    start_date = get_valid_date(start_date)
    end_date = get_valid_date(end_date)
    validate_date_range(start_date, end_date)
    interval = get_valid_interval(interval)
    indicators = get_valid_indicators(indicators)
    config = {
        "tickers": tickers,
        "start_date": start_date,
        "end_date": end_date,
        "interval": interval,
        "indicators": indicators,
        "data_source": data_source or "yfinance",
        "column": column or "Close",
    }
    config.update(kwargs)
    return config


def _run_pipeline(config: dict[any, any]):
    all_data = fetch_all_data(
        config["tickers"],
        config["start_date"],
        config["end_date"],
        config["interval"],
        config["data_source"],
    )
    # all_data = fetcher.fetch_all(
    #    config["tickers"], config["start_date"], config["end_date"], config["interval"]
    # )

    for ticker, data in all_data.items():
        if data.empty:
            print(f"No data found for {ticker}. Skipping...")
            continue
        indicators = run_indicators(data, config["indicators"], config["column"])

        plot_data(
            data,
            indicators,
            config["column"],
            ticker,
            plot_style=config.get("plot_style"),
            color_scheme=config.get("color_scheme"),
            up_color=config.get("up_color"),
            down_color=config.get("down_color"),
            save=config.get("save"),
            save_dir=config.get("save_dir"),
            save_dpi=config.get("save_dpi"),
            interval=config["interval"],
            start_date=config["start_date"],
            end_date=config["end_date"],
        )


@click.command()
@common_options
def run_command(**kwargs):
    """
    Main entrypoint.
    """
    try:
        config = _build_config(**kwargs)
    except Exception as e:
        print(f"Configuration error: {e}")
        return
    _run_pipeline(config)
