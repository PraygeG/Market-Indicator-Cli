from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class BaseIndicator(ABC):
    """
    Abstract base class for all technical indicators.
    """

    def __init__(self, column: Optional[str]) -> None:
        """Initialize the base indicator."""
        self.column = column

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate the indicator values."""

    def _check_required_columns(self, data: pd.DataFrame, required: list[str]) -> None:
        missing = [col for col in required if col not in data.columns]
        if missing:
            raise ValueError(f"DataFrame must contain columns: {missing}")
