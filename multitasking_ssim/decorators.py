import asyncio
from functools import wraps

import click
from aiopath.path import AsyncPath

from .utils.configuration import Configuration
from .utils.parsers import YamlParser


def click_config_injector():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs.pop("debug"):
                import logging

                logging.getLogger().setLevel(logging.DEBUG)
                click.echo("Running in debug mode")

            async def parse_options(*args, **kwargs):
                config_path = kwargs.pop("config")
                if not config_path:
                    raise click.UsageError(
                        "Config file path is required",
                    )
                c_path = await AsyncPath(config_path).expanduser()
                if not (await c_path.exists() or await c_path.is_file()):
                    raise click.UsageError(
                        f"Config file {c_path} does not exist",
                    )
                c_dict = await YamlParser.load_values_from_file(
                    fp=str(c_path),
                )
                c = Configuration.from_dict(c_dict)
                return {"config": c}

            loop = asyncio.get_event_loop()
            opts = loop.run_until_complete(
                parse_options(*args, **kwargs),
            )
            kwargs |= opts
            return func(*args, **kwargs)

        wrapper = click.option(
            "-c",
            "--config",
            required=True,
            type=str,
        )(wrapper)
        wrapper = click.option(
            "--debug",
            default=False,
            required=False,
            is_flag=True,
            help="Enable debug mode.",
        )(wrapper)
        return wrapper

    return decorator


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time

        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        click.echo(f"Execution time: {end - start:.2f}s")
        return result

    return wrapper
