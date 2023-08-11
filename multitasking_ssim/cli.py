import asyncio
import logging

import click
import click_log
import uvloop

from . import commands

ENV_PREFIX = "multitasking_ssim_CLI"


def create_cli():
    cmds = {
        "ai": commands.ai,
    }

    @click.group(
        commands=cmds,
        context_settings={
            "max_content_width": 120,
            "help_option_names": ["-h", "--help"],
        },
    )
    def group():
        ...

    return group


cli = create_cli()


def run():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    click_log.basic_config(logger)

    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(cli(auto_envvar_prefix=ENV_PREFIX))
