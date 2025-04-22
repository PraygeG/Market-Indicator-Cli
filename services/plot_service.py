from plots.plotter import Plotter


class PlotService:
    def __init__(self):
        self.plotter = Plotter()

    def plot(self, data, indicators, column, company_name):
        self.plotter.plot(data, indicators, column=column, company_name=company_name)
