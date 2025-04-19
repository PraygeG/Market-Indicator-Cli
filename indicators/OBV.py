import pandas as pd
from indicators.base_indicator import BaseIndicator

class OBV(BaseIndicator):
    """
    On balance volume
    """
    def __init__(self, column = 'Close'):
        super().__init__(column)