import click
from validators.input_and_validation import (
    get_valid_date,
    get_valid_indicators,
    get_valid_interval,
    get_valid_tickers,
    validate_date_range,
)


class CLIHanlder:
    def __init__(self):
        pass

    def get_config(
        self,
        tickers=None,
        start_date=None,
        end_date=None,
        interval=None,
        indicators=None,
        data_source="yfinance",
        column="Close",
    ):
        tickers = get_valid_tickers(tickers)
        start_date = get_valid_date(start_date)
        end_date = get_valid_date(end_date)
        validate_date_range(start_date, end_date)
        interval = get_valid_interval(interval)
        indicators = get_valid_indicators(indicators)
        data_source = data_source or "yfinance"
        column = column or "Close"
        return {
            "tickers": tickers,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "indicators": indicators,
            "data_source": data_source,
            "column": column,
        }
