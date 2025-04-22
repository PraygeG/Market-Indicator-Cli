from abc import ABC, abstractmethod
import pandas as pd


class BasePlotter(ABC):
    """
    Abstract base class for different plot methods
    """

    def __init__(self, title: str):
        self.title = title

    @abstractmethod
    def plot(
        self, data: pd.DataFrame, indicators: dict, column: str, company_name: str
    ):
        pass
