import os
from typing import Optional, Any, Dict
import yaml
import click
import sys
from cli.config_model import ConfigModel, ValidationError, build_config_interactive
from cli.options import common_options
from cli.services import (
    fetch_all_data,
    run_indicators,
    run_multi_ticker_indicators,
    plot_data,
    plot_multi,
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
    filtered_overrides = {k: v for k, v in cli_overrides.items() if v is not None}
    merged = {**raw, **filtered_overrides}

    cfg = ConfigModel.model_validate(merged)
    return cfg


def _run_pipeline(config: dict[str, any]):
    print(f"Config values: plot_style={config.get('plot_style')}, color_scheme={config.get('color_scheme')}")

    all_data = fetch_all_data(
        tickers=config["tickers"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        interval=config["interval"],
        source=config["data_source"],
        api_key=config.get("api_key"),
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
            save=config.get("save", False),
            save_dir=config.get("save_dir"),
            save_format=config.get("save_format", "png"),
            save_dpi=config.get("save_dpi", False),
            normalize=config.get("normalize", False),
            log_scale=config.get("log_scale", False),
        )
    else:
        for ticker, data in all_data.items():
            print(config["plot_style"])
            print(config["color_scheme"])
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
                save=config.get("save", False),
                save_dir=config.get("save_dir"),
                save_dpi=config.get("save_dpi"),
                interval=config["interval"],
                start_date=config["start_date"],
                end_date=config["end_date"],
                interactive=config.get("interactive", False),
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
    if config_file:
        cli_overrides = {
            k: v for k, v in kwargs.items() if v is not None and k != "config_file"
        }
        config_model = _build_config(config_file)
        config = config_model.model_dump()
        config["indicators"] = config_model.tuples()
        _run_pipeline(config)
    else:
        config_model = build_config_interactive(kwargs)
        config = config_model.model_dump()
        config["indicators"] = config_model.tuples()
        _run_pipeline(config)
