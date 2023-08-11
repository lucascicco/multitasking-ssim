import asyncio
import logging

import aiohttp
from aiopath.path import AsyncPath

from . import image

log = logging.getLogger()


async def download_image_ret_key(
    *,
    key: str,
    image: image.Image,
    sem: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    directory: AsyncPath,
    force: bool = False,
) -> str:
    async with sem:
        log.debug(f"Downloading image {key}")
        await image.download(
            directory=directory,
            session=session,
            force=force,
        )
        return key
