import asyncio
import functools
from collections.abc import Coroutine


def coro(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(*args, **kwargs))

    return wrapper


async def run_coro_with_limits(
    c: Coroutine,
    sem: asyncio.Semaphore,
    timeout: int,
):
    async with sem:
        await asyncio.wait_for(c, timeout)
