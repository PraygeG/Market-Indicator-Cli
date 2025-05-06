import yfinance as yf
import pandas as pd
from data_sources.base_source import BaseSource


class YfinanceSource(BaseSource):
    """
    Data source implementation using yfinance.
    """

    def fetch_data(
        self, ticker: str, start_date: str, end_date: str, interval: str = "1d"
    ) -> pd.DataFrame:
        print(
            f"Fetching data for {ticker} from {start_date} to {end_date} using yfinance"
        )
        data = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            multi_level_index=False,
        )
        data = data.dropna()
        return data
