from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from datetime import date
from typing import List, Tuple, Optional, Dict, Any, Union
from validators.input_and_validation import (
    valid_intervals,
    supported_indicators,
    validate_parsed_indicators,
    validate_tickers,
)


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
                if param_str:
                    p_str = param_str[0]
                    params = [float(p) for p in p_str.split("-")]
                else:
                    params = []
                parsed.append({"name": name.strip(), "params": params})
            values["indicators"] = parsed
        elif isinstance(raw_inds, dict):
            values["indicators"] = [
                {"name": name, "params": ([val] if not isinstance(val, list) else val)}
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
                    param_strs.append(str(int(p)))
                else:
                    param_strs.append(str(p))

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
