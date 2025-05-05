from data_sources.base_source import BaseSource
import requests
import pandas as pd


class AlphavantageSource(BaseSource):
    """
    Data source implementation using alpha vantage API
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key=None):
        """
        Initialize AlphaVantage source with API key.
        """
        self.api_key = api_key
        if not self.api_key:
            import os

            self.api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "AlphaVantage API key is required. Set it via constructor or ALHPA_VANTAGE_API_KEY environment variable."
                )

    def _map_interval(self, interval):
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

    def fetch_data(
        self, ticker: str, start_date: str, end_date: str, interval: str
    ) -> pd.DataFrame:
        print(
            f"Fetching data for {ticker} from {start_date} to {end_date} using AlphaVantage"
        )

        av_interval = self._map_interval(interval)

        if av_interval in ["1min", "5min", "15min", "30min", "60min"]:
            function = f"TIME_SERIES_INTRADAY"
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

        response = requests.get(self.BASE_URL, params=params)
        if response.status_code != 200:
            raise Exception(
                f"API request failed with status code {response.status_code}: {response.text}"
            )

        data = response.json()

        if "Error Message" in data:
            raise Exception(f"API error: {data['Error Message']}")

        if time_series_key not in data:
            available_keys = list(data.keys())
            raise Exception(
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
