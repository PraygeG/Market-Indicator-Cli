from typing import Any


class MarketIndicatorError(Exception):
    """Base exception for all market indicator errors."""


class ConfigError(MarketIndicatorError):
    """Raised for configuration-related errors."""


class DataSourceError(MarketIndicatorError):
    """Raised for data source errors."""


class IndicatorError(MarketIndicatorError):
    """Raised for indicator calculation errors."""


class PlotError(MarketIndicatorError):
    """Raised for plotting errors."""


class ValidationError(MarketIndicatorError):
    """Raised for validation errors."""

    def __init__(
        self, message: str, field: str | None = None, value: Any = None
    ) -> None:
        super().__init__(message)
        self.field = field
        self.value = value
