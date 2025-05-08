import os
from typing import Optional, Any, Dict
import yaml
import click
import sys
from cli.config_model import ConfigModel, ValidationError
from cli.options import common_options
from cli.services import (
    fetch_all_data,
    run_indicators,
    run_multi_ticker_indicators,
    plot_data,
    plot_multi,
)
from validators.input_and_validation import (
    get_valid_date,
    get_valid_indicators,
    get_valid_interval,
    get_valid_tickers,
    validate_date_range,
)


class ConfigError(Exception):
    pass


def load_config(config_file_path: Optional[str]) -> dict[str, Any]:
    if not config_file_path:
        return {}

    if not os.path.exists(config_file_path):
        raise ConfigError(f"Configuration file not found: {config_file_path}")

    try:
        with open(config_file_path, "r") as f:
            config_data = yaml.safe_load(f)
        if config_data is None:
            return {}
        if not isinstance(config_data, dict):
            raise ConfigError(
                f"Configuration file {config_file_path} must contain a dictionary at the top level."
            )
        return config_data
    except yaml.YAMLError as e:
        error_context = ""
        if hasattr(e, "problem_mark") and e.problem_mark is not None:
            error_context = f" at line {e.problem_mark.line + 1}, column {e.problem_mark.column + 1}"
        raise ConfigError(
            f"Error parsing YAML configuration file {config_file_path}: {e}"
        )
    except Exception as e:
        raise ConfigError(f"Could not load configuration file {config_file_path}: {e}")


def _build_config(config_file: str, **cli_overrides) -> Dict[str, Any]:
    raw = load_config(config_file)
    merged = {**raw, **cli_overrides}
    
    cfg = ConfigModel.model_validate(merged)
    result = cfg.model_dump()
    result["indicators"] = cfg.tuples()
    return result


def _run_pipeline(config: dict[str, any]):
    all_data = fetch_all_data(
        tickers=config["tickers"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        interval=config["interval"],
        source=config["data_source"],
        api_key=config["api_key"],
    )
    if config["multi_plot"]:
        indicators = run_multi_ticker_indicators(
            ticker_data=all_data,
            indicators=config["indicators"],
            column=config["column"],
        )
        plot_multi(
            data=all_data,
            indicators=indicators,
            column=config["column"],
            save=config["save"],
            save_dir=config["save_dir"],
            save_format=config["save_format"],
            save_dpi=config["save_dpi"],
            normalize=config["normalize"],
            log_scale=config["log_scale"],
        )
    else:
        for ticker, data in all_data.items():
            if data.empty:
                print(f"No data found for {ticker}. Skipping...")
                continue
            indicators = run_indicators(data, config["indicators"], config["column"])
            plot_data(
                data,
                indicators,
                config["column"],
                ticker,
                plot_style=config.get("plot_style"),
                color_scheme=config.get("color_scheme"),
                up_color=config.get("up_color"),
                down_color=config.get("down_color"),
                save=config.get("save"),
                save_dir=config.get("save_dir"),
                save_dpi=config.get("save_dpi"),
                interval=config["interval"],
                start_date=config["start_date"],
                end_date=config["end_date"],
                interactive=config["interactive"],
            )


@click.command()
@common_options
@click.option(
    "--config-file",
    "-c",
    type=click.Path(exists=True),
    help="Path to YAML configuration file",
)
def run_command(**kwargs):
    """
    Main entrypoint.
    """
    config_file = kwargs.get("config_file")
    if not config_file:
        tickers = get_valid_tickers(kwargs.get("tickers"))
        start = get_valid_date(
            kwargs.get("start_date"), "Enter start date (YYYY-MM-DD):\n"
        )
        end = get_valid_date(kwargs.get("end_date"), "Enter end date (YYYY-MM-DD):\n")
        interval =  get_valid_interval(kwargs.get("interval"))
        indicators = get_valid_indicators(kwargs.get("indicators"))
        config = {
            "tickers": tickers,
            "start_date": start,
            "end_date": end,
            "interval": interval,
            "indicators": indicators,
            "data_source": kwargs.get("data_source"),
            "api_key": kwargs.get("api_key"),
            "column": kwargs.get("column"),
            "plot_style": kwargs.get("plot_style"),
            "color_scheme": kwargs.get("color_scheme"),
            "up_color": kwargs.get("up_color"),
            "down_color": kwargs.get("down_color"),
            "interactive": kwargs.get("interactive"),
            "multi_plot": kwargs.get("multi_plot"),
            "normalize": kwargs.get("normalize"),
            "log_scale": kwargs.get("log_scale"),
            "save": kwargs.get("save"),
            "save_dir": kwargs.get("save_dir"),
            "save_format": kwargs.get("save_format"),
            "save_dpi": kwargs.get("save_dpi"),
        }
    else:
        argv = sys.argv[1:]
        ctx = click.get_current_context()
        provided = set()
        for param in ctx.command.params:
            for opt in param.opts:
                for arg in argv:
                    if arg == opt or arg.startswith(opt + "="):
                        provided.add(param.name)

        cli_overrides = {
            name: kwargs[name] for name in provided if name != "config_file"
        }
        try:
            config = _build_config(config_file=config_file, **cli_overrides)
            print(config)
        except ConfigError as e:
            click.echo(f"Configuration validation error:\n{e}", err=True)
            raise click.Abort()

    _run_pipeline(config)
