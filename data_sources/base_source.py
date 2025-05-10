from abc import ABC, abstractmethod
import pandas as pd


class BaseSource(ABC):
    """
    Abstract base class for data sources.
    All data sources must implement the fetch_data method.
    """

    @abstractmethod
    def fetch_data(
        self, ticker: str, start_date: str, end_date: str, interval: str
    ) -> pd.DataFrame:
        """
        Fetch data for given ticker and date range.
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        Returns:
            Data frame with stock data
        """
