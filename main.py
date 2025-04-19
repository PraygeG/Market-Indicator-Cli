import click
import pandas as pd
import time
from data_sources.yfinance_source import YfinanceSource
from indicators.EMA import EMA
from indicators.SMA import SMA
from indicators.RSI import RSI
from indicators.BBANDS import BBANDS
from indicators.MACD import MACD
from plots.plotter import Plotter
from validators.input_validators import validate_date, get_valid_interval, get_valid_indicators, get_valid_tickers

INDICATOR_CLASSES = {
    "EMA": EMA,
    "SMA": SMA,
    "RSI": RSI,
    "MACD": MACD,
    "BBANDS": BBANDS
}

@click.command()
@click.option('--tickers', default=None, help="Comma-separated list of tickers (e.g., AAPL, MSFT)")
@click.option('--start-date', default=None, help="Start date (YYYY-MM-DD)")
@click.option('--end-date', default=None, help="End date (YYYY-MM-DD)")
@click.option("--interval", default=None, help="""Interval in which data is downloaded. 
Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo Intraday data cannot extend last 60 days.""")
@click.option('--indicators', default=None, help="Comma-separated list of indicators (e.g., RSI:14,EMA:50,SMA:100,MACD:12-26-9)")
@click.option('--data-source', default='yfinance', help="Data source to use (default: yfinance)")
@click.option('--column', default='Close', help="Column to use for calculations (e.g., Open, High, Low, Close, Volume)")
#@click.option('--save', )

def main(tickers, indicators, start_date, end_date, interval, data_source, column):
    if data_source == 'yfinance':
        data_source = YfinanceSource()

    tickers = get_valid_tickers(tickers)

    if start_date is None:
        while True:
            start_date = input("Please enter start date in the following format - (YYYY-MM-DD):\n")
            valid, message = validate_date(start_date)
            print(message)
            if valid:
                break
    
    if end_date is None:
        while True:
            end_date = input("Please enter end date in the following format - (YYYY-MM-DD):\n")
            valid, message = validate_date(end_date)
            if valid:
                if end_date < start_date:
                    print("The end date cannot be smaller than start date")
                    continue
                else:
                    print(message)
                    break

    interval = get_valid_interval(interval)
    indicators = get_valid_indicators(indicators)
    print()
    print(indicators)
    print(tickers)
    print(interval)
    

    plotter = Plotter()

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        data = data_source.fetch_data(ticker, start_date, end_date, interval)
        time.sleep(1)

        if data.empty:
            print(f"No data found for {ticker}. Skipping...")
            continue
        calculated_indicators = {}
        for name, params in indicators:
            indicator_class = INDICATOR_CLASSES.get(name)
            if not indicator_class:
                print(f"Indicator {name} is not supported. Skipping...")
                continue

            indicator = indicator_class(*params, column=column)
            calculated_series = indicator.calculate(data)
            #calculated_indicators[name] = (calculated_series, params)
            calculated_indicators[f"{name}_{'_'.join(map(str, params))}"] = (calculated_series,params)

        try:
            plotter.plot(data, calculated_indicators, column=column, company_name=ticker)
        except Exception as e:
            print(f"Error while plotting data for {ticker}: {e}")


if __name__ == "__main__":
    main()