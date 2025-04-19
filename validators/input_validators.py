from datetime import datetime
import yfinance as yf
from requests.exceptions import HTTPError

valid_intervals={"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}
intraday_intervals={"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}

supported_indicators = {
    "EMA": (1, lambda p: p.isdigit() and int(p)>0),
    "SMA": (1, lambda p: p.isdigit() and int(p)>0),
    "RSI": (1, lambda p: p.isdigit() and int(p)>0),
    "MACD": (3, lambda p: p.isdigit() and int(p)>0),
    "BBANDS": (2, lambda p: p.isdigit() and int(p)>0)
}

def get_valid_tickers(tickers_str: str | None)-> list[str]:
    if tickers_str is None:
        prompt = True
    else:
        tickers = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
        valid, message = validate_tickers(tickers)
        print(message)
        prompt = not valid

    while prompt:
        tickers_str = input("Enter tickers (comma-separated, e.g., AAPL, MSFT, TSLA):\n")
        tickers = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
        valid, message = validate_tickers(tickers)
        print(message)
        if valid:
            break

    return tickers

def validate_tickers(tickers: list[str])-> tuple[bool, str]:
    if not tickers:
        return False, "No tickers provided."
    
    invalid = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            if 'regularMarketPrice' not in info or info['regularMarketPrice'] is None:
                invalid.append(ticker)
        
        except Exception as e:
            error_msg = str(e).lower()
            if "404" in error_msg or "not found" in error_msg:
                invalid.append(ticker)
            else:
                print(f"[DEBUG] Unexpected error for '{ticker}': {e}")
                invalid.append(ticker)

    if invalid:
        return False, f"Invalid or inactive tickers: {', '.join(invalid)}"
    return True, "All tickers are valid."

def validate_date(date: str):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        if date_obj.year > datetime.now().year:
            return False, "The year cannot be greater than the current year."
        return True, "The date is valid"
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD"
    
def validate_interval(interval: str):
    if interval in valid_intervals:
        return True, "Valid interval."
    else:
        return False, "Invalid interval. Try again."
    
def get_valid_interval(interval: str)-> str:
    if interval is None:
        prompt = True
    else:
        valid, message = validate_interval(interval)
        print(message)
        prompt = not valid

    while prompt:
        interval = input("Enter a valid interval (e.g., 1d, 5m, 1h, 1wk, 1mo):\n")
        valid, message = validate_interval(interval)
        print(message)
        if valid:
            break
    return interval

def validate_indicators(indicator_str: str)-> tuple[bool, str]:
    if not indicator_str:
        return True, "No indicators provided. Skipping."
    
    pairs = indicator_str.split(',')
    for pair in pairs:
        if ':' not in pair:
            return False, f"Invalid format: '{pair}'. Use INDICATOR:PARAM syntax. For multiparameter INDICATOR:PARAM-PARAM-PARAM syntax."
        
        name, param = pair.split(':', 1)
        name = name.strip().upper()

        if name not in supported_indicators:
            return False, f"Unsupported indicator: '{name}'"
        
        required_count, validator_fn = supported_indicators[name]

        if name == "MACD" and '-' in param:
            param_list = param.split('-')
        elif name == "BBANDS" and '-' in param:
            param_list = param.split('-')
        else:
            param_list = param.split(',')

        if len(param_list) != required_count:
            return False, f"'{name}' requires {required_count} parameter(s), got {len(param_list)}."
        
        if validator_fn and not all(validator_fn(p) for p in param_list):
            return False, f"Invalid parameters for '{name}': '{param}'"
        
    return True, "All indicators are valid."

def get_valid_indicators(indicators: str)-> list[tuple[str, list[int]]]:
    if indicators is None:
        prompt = True
    else:
        valid, message = validate_indicators(indicators)
        print(message)
        prompt = not valid

    while prompt:
        indicators = input("Enter indicators (e.g., EMA:14,SMA:50,RSI:14):\n")
        valid, message = validate_indicators(indicators)
        print(message)
        if valid:
            break
    
    parsed_indicators = []
    if not indicators:
        return parsed_indicators
    
    indicator_pairs = indicators.split(',')

    for pair in indicator_pairs:
        if ':' not in pair:
            continue
        name, param_str = pair.split(':', 1)
        name = name.strip().upper()



        if name == "MACD" and '-' in param_str:
            params = [int(p.strip()) for p in param_str.split('-')]
        elif name == "BBANDS" and '-' in param_str:
            params = [int(p.strip()) for p in param_str.split('-')]
        else:
            params = [int(p.strip()) for p in param_str.split(',')]
        parsed_indicators.append((name, params))

    return parsed_indicators