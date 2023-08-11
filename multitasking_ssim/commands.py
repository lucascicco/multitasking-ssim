import click

from multitasking_ssim.processor import ImageComparisonProcessor
from multitasking_ssim.utils.configuration import Configuration

from . import decorators
from .utils.aio import coro


@click.group(name="ai", hidden=False)
def ai():
    ...


@ai.command(name="compare_images")
@decorators.click_config_injector()
@decorators.timer
@coro
async def compare_images(config: Configuration, *args, **kwargs):
    p = await ImageComparisonProcessor.from_config(config=config)
    await p.initialize()
    await p.process()
