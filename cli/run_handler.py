class RunHandler:
    def __init__(self, config):
        from services.data_fetcher import DataFetcher
        from services.indicator_runner import IndicatorRunner
        from services.plot_service import PlotService

        self.config = config
        self.fetcher = DataFetcher(config["data_source"])
        self.indicator_runner = IndicatorRunner()
        self.plot_service = PlotService()

    def run(self):
        all_data = self.fetcher.fetch_all(
            self.config["tickers"],
            self.config["start_date"],
            self.config["end_date"],
            self.config["interval"],
        )

        for ticker, data in all_data.items():
            if data.empty:
                print(f"No data found for {ticker}. Skipping...")
                continue

            indicators = self.indicator_runner.run(
                data, self.config["indicators"], self.config["column"]
            )

            self.plot_service.plot(
                data=data,
                indicators=indicators,
                column=self.config["column"],
                ticker=ticker,
                plot_style=self.config["plot_style"],
                color_scheme=self.config["color_scheme"],
                up_color=self.config["up_color"],
                down_color=self.config["down_color"],
                save=self.config["save"],
                save_dir=self.config["save_dir"],
                save_format=["save_format"],
                save_dpi=self.config["save_dpi"],
                interval=self.config["interval"],
                start_date=self.config["start_date"],
                end_date=self.config["end_date"],
            )
