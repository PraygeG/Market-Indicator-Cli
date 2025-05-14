import os
import sys
import logging
from typing import Optional, Any, Dict
import importlib.resources
from pathlib import Path
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

def resolve_path(path: str, base_dir: str = None) -> str:
    if not path:
        return None
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(base_dir or "", path))


def load_config(config_file_path: Optional[str]) -> dict[str, Any]:
    if config_file_path:
        abs_path = os.path.abspath(config_file_path)
        if os.path.exists(abs_path):
            chosen = Path(abs_path)
        else:
            click.echo(f"Warning: {abs_path!r} not found; using built-in config", err=True)
            chosen = None
    else:
        chosen = None

    if chosen is None:
        pkg_file = importlib.resources.files("stonkzilla").joinpath("config.yaml")
        with importlib.resources.as_file(pkg_file) as fp:
            chosen = fp

    try:
        with open(chosen, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        ctx = f" at line {mark.line+1}, col {mark.column+1}" if mark else ""
        raise ConfigError(f"YAML parse error{ctx}: {e}")
    except Exception as e:
        raise ConfigError(f"Could not open config file {chosen!r}: {e}")
    
    if not isinstance(data, dict):
        raise ConfigError("Top-level of config must be a mapping/dict")
    base_dir = chosen.parent
    if "save_dir" in data:
        data["save_dir"] = resolve_path(data["save_dir"], str(base_dir))
    return data


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
    type=click.Path(dir_okay=False, file_okay=True),
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
