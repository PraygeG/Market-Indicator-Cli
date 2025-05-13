import time
import logging
import requests
from requests.exceptions import RequestException
import pandas as pd
from stonkzilla.data_sources.base_source import BaseSource
from stonkzilla.cli.exceptions import DataSourceError

logger = logging.getLogger("market-indicator-cli")


class AlphavantageSource(BaseSource):
    """
    Data source implementation using alpha vantage API
    """

    BASE_URL = "https://www.alphavantage.co/query"
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2

    def __init__(self, api_key: str = None) -> None:
        """
        Initialize AlphaVantage source with API key.
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError(
                "AlphaVantage API key is required. Set it via constructor or environment variable."
            )

    def _map_interval(self, interval: str):
        interval_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "60m": "60min",
            "1d": "daily",
            "1wk": "weekly",
            "1mo": "monthly",
        }
        if interval not in interval_map:
            raise ValueError(
                f"Unsupported interval: {interval}. Supported intervals: {', '.join(interval_map.keys())}"
            )
        return interval_map[interval]

    def _request(self, params: dict) -> dict:
        """Internal: perform HTTP request with retries and backoff."""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = requests.get(self.BASE_URL, params=params, timeout=(5, 20))
                response.raise_for_status()
                data = response.json()
            except RequestException as e:
                logger.warning("HTTP error on attempt %d: %s", attempt, e)
                if attempt == self.MAX_RETRIES:
                    raise DataSourceError(
                        "Network error contacting Alpha Vantage"
                    ) from e
                time.sleep(self.BACKOFF_FACTOR ** (attempt - 1))
            except ValueError as e:
                raise DataSourceError("Invalid JSON in Alpha Vantage response") from e

            if "Error Message" in data:
                raise DataSourceError(
                    f"Alpha Vantage API error: {data["Error Message"]}"
                )
            if "Note" in data:
                logger.info("Rate limit reached: %s", data["Note"])
                if attempt == self.MAX_RETRIES:
                    raise DataSourceError(f"Rate limit exceeded: {data["Note"]}")
                time.sleep(self.BACKOFF_FACTOR ** (attempt - 1))
                continue
            print(data)
            return data
        raise DataSourceError("Exceeded retries without success")

    def fetch_data(
        self, ticker: str, start_date: str, end_date: str, interval: str
    ) -> pd.DataFrame:
        """Fetch data using alphavantage."""
        print(
            f"Fetching data for {ticker} from {start_date} to {end_date} using AlphaVantage"
        )

        av_interval = self._map_interval(interval)

        if av_interval in ["1min", "5min", "15min", "30min", "60min"]:
            function = "TIME_SERIES_INTRADAY"
            params = {
                "function": function,
                "symbol": ticker,
                "interval": av_interval,
                "outputsize": "full",
                "apikey": self.api_key,
            }
            time_series_key = f"Time Series ({av_interval})"
        else:
            function_map = {
                "daily": "TIME_SERIES_DAILY",
                "weekly": "TIME_SERIES_WEEKLY",
                "monthly": "TIME_SERIES_MONTHLY",
            }
            function = function_map[av_interval]
            params = {
                "function": function,
                "symbol": ticker,
                "outputsize": "full",
                "apikey": self.api_key,
            }
            time_series_key = f"Time Series ({function.split('_')[-1].capitalize()})"

        try:
            data = self._request(params)
        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError("Unexpected error in AlphaVantage")

        if time_series_key not in data:
            available_keys = list(data.keys())
            raise DataSourceError(
                f"Expected key '{time_series_key}' not found in response. Available keys: {available_keys}"
            )

        time_series = data[time_series_key]
        df = pd.DataFrame.from_dict(time_series, orient="index")

        df.columns = [col.split(". ")[1] if ". " in col else col for col in df.columns]
        df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            },
            inplace=True,
        )

        for col in ["Open", "High", "Low", "Close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col])

        if "Volume" in df.columns:
            df["Volume"] = pd.to_numeric(df["Volume"])

        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df.index >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df.index <= end_date]

        return df
