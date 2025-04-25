import click
from cli.options import common_options
from cli.run_handler import RunHandler
from cli.cli_handler import CLIHanlder


@click.command()
@common_options
def run_command(**kwargs):
    """
    Main entrypoint.
    """
    try:
        config = CLIHanlder().get_config(
            tickers=kwargs.get("tickers"),
            start_date=kwargs.get("start_date"),
            end_date=kwargs.get("end_date"),
            interval=kwargs.get("interval"),
            indicators=kwargs.get("indicators"),
            data_source=kwargs.get("data_source"),
            column=kwargs.get("column"),
        )

        config.update({k: v for k, v in kwargs.items() if k not in config})

    except Exception as e:
        print(f"Configuration error: {e}")
        return

    runner = RunHandler(config)
    runner.run()
