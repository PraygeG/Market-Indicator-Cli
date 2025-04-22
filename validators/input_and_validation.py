from datetime import datetime
import yfinance as yf


class ValidationError(Exception):
    """Validation error exception"""

    pass


valid_intervals = {
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "60m",
    "90m",
    "1h",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
}
intraday_intervals = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}

supported_indicators = {
    "EMA": (1, lambda p: p.isdigit() and int(p) > 0),
    "SMA": (1, lambda p: p.isdigit() and int(p) > 0),
    "RSI": (1, lambda p: p.isdigit() and int(p) > 0),
    "MACD": (3, lambda p: p.isdigit() and int(p) > 0),
    "BBANDS": (2, lambda p: p.isdigit() and int(p) > 0),
    "OBV": (0, None),
}


def prompt_until_valid(value, validator: callable, prompt_msg: str):
    """Prompt/validation loop"""
    while True:
        try:
            return validator(value)
        except ValidationError as e:
            print(e)
            value = input(prompt_msg)


def validate_tickers(tickers_str: str) -> list[str]:
    if not tickers_str:
        raise ValidationError("No tickers provided.")
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    if not tickers:
        raise ValidationError("No tickers provided.")
    invalid = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            if "regularMarketPrice" not in info or info["regularMarketPrice"] is None:
                invalid.append(ticker)
        except Exception as e:
            error_msg = str(e).lower()
            if "404" in error_msg or "not found" in error_msg:
                invalid.append(ticker)
            else:
                print(f"[DEBUG] Unexpected error for '{ticker}: {e}")
                invalid.append(ticker)
    if invalid:
        raise ValidationError(f"Invalid or inactive tickers: {', '.join(invalid)}")
    return tickers


def get_valid_tickers(tickers_str: str | None) -> list[str]:
    return prompt_until_valid(
        tickers_str,
        validate_tickers,
        "Enter tickers (comma-separated, e.g., AAPL, MSFT, TSLA):\n",
    )


def validate_date(date: str) -> str:
    if not date:
        raise ValidationError()
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        if date_obj.year > datetime.now().year:
            raise ValidationError("The year cannot be greater than the current year.")
        return date
    except ValueError:
        raise ValidationError(f"Invalid date format. Please use YYYY-MM-DD")


def get_valid_date(date: str | None) -> str:
    return prompt_until_valid(date, validate_date, "Enter a valid date (YYYY-MM-DD):\n")


def validate_date_range(start_date: str, end_date: str) -> None:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Invalid date format. Please use YYYY-MM-DD")
    if start > end:
        raise ValidationError("Start date cannot be after the end date.")


def validate_interval(interval: str) -> str:
    if interval in valid_intervals:
        return interval
    raise ValidationError("Invalid interval. Try again.")


def get_valid_interval(interval: str | None) -> str:
    return prompt_until_valid(
        interval,
        validate_interval,
        "Enter a valid interval (e.g., 1d, 5m, 1h, 1wk, 1mo):\n",
    )


def parse_indicators(indicator_str: str) -> list[tuple[str, list[int]]]:
    """Parse indicator string to list of (name, parameters) tuples."""
    if not indicator_str:
        return []
    result = []
    pairs = indicator_str.split(",")
    for pair in pairs:
        if ":" not in pair:
            name = pair.strip().upper()
            params = []
        else:
            name, param = pair.split(":", 1)
            name = name.strip().upper()
            if name in {"MACD", "BBANDS"} and "-" in param:
                params = [int(p.strip()) for p in param.split("-")]
            else:
                params = [int(p.strip()) for p in param.split(",")]
        result.append((name, params))
    return result


def validate_parsed_indicators(parsed_ind: list[tuple[str, list[int]]]):
    for name, params in parsed_ind:
        if name not in supported_indicators:
            raise ValidationError(f"Unsupported indicator: '{name}'")
        required_count, validator_fn = supported_indicators[name]
        if required_count == 0:
            if params:
                raise ValidationError(
                    f"'{name}' does not require any parameters, but got '{params}'"
                )
            continue
        if len(params) != required_count:
            raise ValidationError(
                f"'{name}' requires {required_count} parameter(s), got {len(params)}."
            )
        if validator_fn and not all(validator_fn(str(p)) for p in params):
            raise ValidationError(f"Invalid parameters for '{name}': '{params}'")


def get_valid_indicators(indicator_str: str | None) -> list[tuple[str, list[int]]]:
    def validator(s):
        if not s:
            raise ValidationError("No indicators provided.")
        parsed = parse_indicators(s)
        validate_parsed_indicators(parsed)
        return parsed

    return prompt_until_valid(
        indicator_str, validator, "Enter indicators (e.g., EMA:14, SMA:50, RSI:14):\n"
    )
