"Config model and validation module."

import time
from datetime import date, datetime
from typing import List, Tuple, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
import yfinance as yf


PROMPT_MESSAGES = {
    "tickers": "Enter tickers (comma-separated, e.g., AAPL, MSFT, TSLA):\n",
    "start_date": "Enter start date (YYYY-MM-DD):\n",
    "end_date": "Enter end date (YYYY-MM-DD):\n",
    "interval": "Enter a valid interval (e.g., 1d, 5m, 1h, 1wk, 1mo):\n",
    "indicators": "Enter indicators (e.g., EMA:14, SMA:50, RSI:14):\n",
    "data_source": "Enter data source (yfinance/alphavantage):\n",
    "api_key": "Enter API key (if using alphavantage):\n",
    "column": "Enter column for calculations (default: Close):\n",
    "plot_style": "Enter plot style (line/candlestick):\n",
    "color_scheme": "Enter color scheme (default, monochrome, tradingview, dark):\n",
    "up_color": "Custom up color (or leave blank):\n",
    "down_color": "Custom down color (or leave blank):\n",
    "interactive": "Enable interactive plot? (y/n):\n",
    "multi_plot": "Plot all tickers on same plot? (y/n):\n",
    "normalize": "Normalize data for multi-plot? (y/n):\n",
    "log_scale": "Use log scale for multi-plot? (y/n):\n",
    "save": "Save plot(s) to file? (y/n):\n",
    "save_dir": "Directory to save plots (or leave blank):\n",
    "save_format": "Save format (png/pdf/svg/jpg):\n",
    "save_dpi": "DPI for raster formats (or leave blank):\n",
}


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


def _is_positive_float(s: str) -> bool:
    try:
        return float(s) > 0
    except ValueError:
        return False


def _is_positive_number(p: str | int | float) -> bool:
    if isinstance(p, str):
        return p.isdigit() and int(p) > 0
    return isinstance(p, (int, float)) and p > 0


supported_indicators = {
    "EMA": (1, _is_positive_number),
    "SMA": (1, _is_positive_number),
    "RSI": (1, _is_positive_number),
    "MACD": (3, _is_positive_number),
    "BBANDS": (2, _is_positive_number),
    "ADX": (1, _is_positive_number),
    "OBV": (0, None),
    "FIBO": (-1, _is_positive_float),
}


def validate_tickers(tickers_str: str) -> list[str]:
    """Validate tickers by pinging yfinance for ticker info."""
    if not tickers_str:
        raise ValueError("No tickers provided.")

    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    if not tickers:
        raise ValueError("No tickers provided.")
    invalid = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            time.sleep(0.1)
            if "regularMarketPrice" not in info or info["regularMarketPrice"] is None:
                invalid.append(ticker)
        except Exception as e:
            error_msg = str(e).lower()
            if "404" in error_msg or "not found" in error_msg:
                invalid.append(ticker)
                print(f"Ticker: {ticker} does not exist.")
            elif "Rate" in error_msg or "limited" in error_msg:
                print(
                    error_msg
                    + "\nTry updating the yfinance package, it could be a bug that happens when the package is out of date."
                )
            else:
                print(f"[DEBUG] Unexpected error for '{ticker}: {e}")
                invalid.append(ticker)
    if invalid:
        raise ValueError(f"Invalid or inactive tickers: {', '.join(invalid)}")

    return tickers


def validate_date(date: str) -> str:
    if not date:
        raise ValueError()
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        if date_obj.year > datetime.now().year:
            raise ValueError("The year cannot be greater than the current year.")
        return date
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD")


def validate_interval(interval: str) -> str:
    if interval in valid_intervals:
        return interval
    raise ValueError("Invalid interval. Try again.")


def validate_parsed_indicators(parsed_ind: list[tuple[str, list[int | float]]]):
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

        if required_count < 0:
            min_req = abs(required_count)
            if len(params) < min_req:
                raise ValidationError(
                    f"'{name}' requires {required_count} parameter(s), got {len(params)}."
                )

        else:
            if len(params) != required_count:
                raise ValidationError(
                    f"'{name}' requires {required_count} parameter(s), got {len(params)}."
                )

        # if validator_fn and not all(validator_fn(str(p)) for p in params):
        if validator_fn and not all(validator_fn(p) for p in params):
            raise ValidationError(f"Invalid parameters for '{name}': '{params}'")


class Indicator(BaseModel):
    name: str = Field(..., description="Indicator name, e.g. 'EMA', 'RSI'")
    params: Union[List[Union[int, float]], int, float, None] = None

    @model_validator(mode="before")
    def normalize_params(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        raw = values.get("params")
        if raw is None:
            values["params"] = []

        elif isinstance(raw, (int, float)):
            values["params"] = [
                int(raw) if isinstance(raw, float) and raw.is_integer() else raw
            ]

        elif isinstance(raw, list):
            normalized = []
            for p in raw:
                if isinstance(p, float) and p.is_integer():
                    normalized.append(int(p))
                elif isinstance(p, (int, float)):
                    normalized.append(p)
                else:
                    raise TypeError(f"Invalid indicator param: {p}")
            values["params"] = normalized
        else:
            raise TypeError("params must be int, float, list, or None")

        return values


class ConfigModel(BaseModel):
    tickers: List[str] = Field(..., description="List of stock tickers to fetch")
    start_date: date = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: date = Field(..., description="End date in YYYY-MM-DD format")
    interval: str = Field(
        "1d", description="Data interval, e.g., 1d, 5m, 1h, 1wk, etc."
    )
    indicators: List[Indicator] = Field(
        default_factory=list,
        description='List of (list,tor name, parameters) tuples, e.g. [("EMA", [14]), ("RSI", [14])]',
    )
    data_source: str = Field("yfinance", description="Data source to use")
    api_key: Optional[str] = Field(
        None, description="API key for the data source (Alphavantage) if chosen."
    )
    column: str = Field("Close", description="Data column to calculate indicators on")
    plot_style: str = Field(
        "line", description="Plot style, e.g. 'line' or 'candlestick'"
    )
    color_scheme: str = Field("default", description="Color scheme for plots")
    up_color: Optional[str] = Field(
        None, description="Override color for up candles/bars"
    )
    down_color: Optional[str] = Field(
        None, description="Ovveride color for down candles/bars"
    )
    interactive: bool = Field(False, description="Enable interactive plotting")
    multi_plot: bool = Field(
        False, description="Plot multiple tickers on the same plot"
    )
    normalize: bool = Field(False, description="Normalize data in multi-plot mode")
    log_scale: bool = Field(
        False, description="Use logarithmic scale in multi-plot mode"
    )
    save: bool = Field(False, description="Save plots to files instead of showing")
    save_dir: Optional[str] = Field(None, description="Directory to save plot files")
    save_format: str = Field(
        "png", description="Format of saved plot files, e.g. 'png'"
    )
    save_dpi: Optional[int] = Field(None, description="DPI for saved raster plots")

    @field_validator("tickers", mode="before")
    def validate_tickers_input(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, list):
            v = ",".join(v)
        return validate_tickers(v)

    @model_validator(mode="before")
    def preprocess(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        raw_inds = values.get("indicators")
        if isinstance(raw_inds, str):
            parsed = []
            for part in raw_inds.split(","):
                name, *param_str = part.split(":")
                name = name.strip().upper()
                if param_str:
                    p_str = param_str[0]
                    params = [float(p) for p in p_str.split("-")]
                else:
                    params = []
                parsed.append({"name": name.strip(), "params": params})
            values["indicators"] = parsed
        elif isinstance(raw_inds, dict):
            values["indicators"] = [
                {
                    "name": name.strip().upper(),
                    "params": ([val] if not isinstance(val, list) else val),
                }
                for name, val in raw_inds.items()
            ]
        return values

    @field_validator("interval")
    def validate_intervals(cls, v, info):
        if v not in valid_intervals:
            raise ValueError(f"Invalid interval: {v}. Must be one of {valid_intervals}")
        return v

    @field_validator("indicators", mode="after")
    def validate_indicators(cls, v: List[Indicator]) -> List[Indicator]:
        for ind in v:
            if ind.name not in supported_indicators:
                raise ValueError(f"Unsupported indicator: {ind.name}")

            param_strs: list[str] = []
            for p in ind.params:
                if isinstance(p, float) and p.is_integer():
                    param_strs.append(int(p))
                else:
                    param_strs.append(p)
            validate_parsed_indicators([(ind.name, param_strs)])
        return v

    @field_validator("end_date")
    def check_date_order(cls, v, info):
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("end_date must be on or after start_date")
        return v

    def tuples(self) -> List[Tuple[str, List[float]]]:
        return [(ind.name, ind.params) for ind in self.indicators]


def build_config_interactive(initial: dict = None) -> ConfigModel:
    initial = initial or {}
    while True:
        try:
            return ConfigModel.model_validate(initial)
        except ValidationError as e:
            for err in e.errors():
                field = err["loc"][0]
                prompt = PROMPT_MESSAGES.get(field, f"Enter value for {field}: ")
                value = input(prompt)
                initial[field] = value
