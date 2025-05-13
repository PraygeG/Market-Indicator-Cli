import os
import sys
import logging
from typing import Optional, Any, Dict
import yaml
import click
from stonkzilla.cli.config_model import ConfigModel, build_config_interactive
from stonkzilla.cli.options import common_options
from stonkzilla.cli.services import (
    fetch_all_data,
    run_indicators,
    run_multi_ticker_indicators,
    plot_data,
    plot_multi,
)
from stonkzilla.cli.exceptions import (
    ConfigError,
    DataSourceError,
    IndicatorError,
    PlotError,
    ValidationError,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("market-indicator-cli")


def load_config(config_file_path: Optional[str]) -> dict[str, Any]:
    if not config_file_path:
        return {}

    if not os.path.exists(config_file_path):
        raise ConfigError(f"Configuration file not found: {config_file_path}")

    try:
        with open(config_file_path, "r", encoding="utf-8") as f:
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
            f"Error parsing YAML configuration file {config_file_path}{error_context}: {e}"
        )
    except Exception as e:
        raise ConfigError(f"Could not load configuration file {config_file_path}: {e}")


def _build_config(config_file: str, **cli_overrides) -> Dict[str, Any]:
    try:
        raw = load_config(config_file)
        filtered_overrides = {k: v for k, v in cli_overrides.items() if v is not None}
        merged = {**raw, **filtered_overrides}

        cfg = ConfigModel.model_validate(merged)
        return cfg
    except Exception as e:
        logger.error("Failed to build configuration: %s", e, exc_info=True)
        raise ConfigError("Failed to build configuration") from e


def _run_pipeline(config: dict[str, Any]) -> None:
    try:
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
                indicators = run_indicators(
                    data, config["indicators"], config["column"]
                )
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
                )
    except (
        DataSourceError,
        IndicatorError,
        PlotError,
        ValidationError,
        ConfigError,
    ) as e:
        logger.error("Pipeline error: %s", e, exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.critical("Unexpected error: %s", e, exc_info=True)
        click.echo(f"Unexpected erro: {e}", err=True)
        sys.exit(2)


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
    try:
        config_file = kwargs.get("config_file")
        if config_file:
            config_model = _build_config(config_file)
            config = config_model.model_dump()
            config["indicators"] = config_model.tuples()
            _run_pipeline(config)
        else:
            config_model = build_config_interactive(kwargs)
            config = config_model.model_dump()
            config["indicators"] = config_model.tuples()
            _run_pipeline(config)
    except (ConfigError, ValidationError) as e:
        logger.error("Configuration error: %s", e, exc_info=True)
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.critical("Fatal error: %s", e, exc_info=True)
        click.echo("Fatal error: %s", e, err=True)
        sys.exit(2)
