from data_sources.yfinance_source import YfinanceSource
from data_sources.alphavantage_source import AlphavantageSource
import time


class DataFetcher:
    def __init__(self, source="yfinance"):
        if source == "yfinance":
            self.source = YfinanceSource()
        elif source == "alphavantage":
            self.source = AlphavantageSource()
        else:
            raise NotImplementedError("Only yfinance is supported for now.")

    def fetch(self, ticker, start_date, end_date, interval):
        return self.source.fetch_data(ticker, start_date, end_date, interval)

    def fetch_all(self, tickers, start_date, end_date, interval, delay=1):
        data_dict = {}
        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            data = self.fetch(ticker, start_date, end_date, interval)
            time.sleep(delay)
            data_dict[ticker] = data
        return data_dict
