from abc import ABC, abstractmethod
import pandas as pd


class BaseIndicator(ABC):
    """
    Abstract base class for all technical indicators.
    """

    def __init__(self, column: str = "Close"):
        self.column = column

    @abstractmethod
    def calculate(self, data: pd.DataFrame, columns: str | list[str]) -> pd.Series:
        pass
