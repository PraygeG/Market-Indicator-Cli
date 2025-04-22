from indicators.EMA import EMA
from indicators.SMA import SMA
from indicators.RSI import RSI
from indicators.BBANDS import BBANDS
from indicators.MACD import MACD
from indicators.OBV import OBV

INDICATOR_CLASSES = {
    "EMA": EMA,
    "SMA": SMA,
    "RSI": RSI,
    "MACD": MACD,
    "BBANDS": BBANDS,
    "OBV": OBV,
}


class IndicatorRunner:
    def run(self, data, indicators, column):
        calculated = {}
        for name, params in indicators:
            indicator_class = INDICATOR_CLASSES.get(name)
            if not indicator_class:
                continue
            if name == "OBV":
                indicator = indicator_class()
                calculated_series = indicator.calculate(data)
                calculated[name] = (calculated_series, params)
            else:
                indicator = indicator_class(*params, column=column)
                calculated_series = indicator.calculate(data)
                calculated[f"{name}_{'_'.join(map(str, params))}"] = (
                    calculated_series,
                    params,
                )
        return calculated
