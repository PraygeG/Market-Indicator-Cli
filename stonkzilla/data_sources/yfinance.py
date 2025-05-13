import yfinance as yf
import pandas as pd
from stonkzilla.data_sources.base_source import BaseSource
from stonkzilla.cli.exceptions import DataSourceError


class YfinanceSource(BaseSource):
    """
    Data source implementation using yfinance.
    """

    def fetch_data(
        self, ticker: str, start_date: str, end_date: str, interval: str = "1d"
    ) -> pd.DataFrame:
        try:
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
            if data is None or data.empty:
                raise DataSourceError(f"No data returned for ticker {ticker}")
            data = data.dropna()
            return data
        except Exception as e:
            raise DataSourceError(
                f"Failed to fetch data for {ticker} from yfinance: {e}"
            ) from e
