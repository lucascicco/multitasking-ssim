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
    index: int = 0,
) -> str:
    async with sem:
        await asyncio.sleep(index)
        log.debug(f"Downloading image {key}")
        await image.download(
            directory=directory,
            session=session,
            force=force,
        )
        return key
