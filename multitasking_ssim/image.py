from dataclasses import dataclass, field
from typing import cast

import aiohttp
import cv2
from aiopath.path import AsyncPath

from multitasking_ssim.calculations import ImageCalculations
from multitasking_ssim.exceptions import ImageAlreadyExistsError
from multitasking_ssim.utils.configuration import ImageSectionConfig


@dataclass
class Image:
    id: int  # noqa: A003
    src: str
    _path: AsyncPath | None = field(default=None)

    @property
    def path(self) -> AsyncPath | None:
        return self._path

    @classmethod
    def from_config(cls, c: ImageSectionConfig):
        return cls(id=c.id, src=c.src)

    async def is_downloaded(self) -> bool:
        return self.path is not None and await self.path.exists()

    async def _download(
        self,
        *,
        force: bool = False,
        directory: AsyncPath,
        chunk_size: int = 1024,
        session: aiohttp.ClientSession,
    ):
        if await self.is_downloaded():
            if not force:
                raise ImageAlreadyExistsError("Image already downloaded")
            p = cast(AsyncPath, self.path)
            await p.unlink()
        async with session.get(self.src) as r:
            r.raise_for_status()
            img_ext = r.headers["Content-Type"].split("/")[-1]
            img_path = AsyncPath(f"{directory}/{self.id}.{img_ext}")
            async with img_path.open("wb") as f:
                while True:
                    chunk = await r.content.read(chunk_size)
                    if not chunk:
                        break
                    await f.write(chunk)
            self._path = img_path

    async def download(
        self,
        *,
        directory: AsyncPath,
        session: aiohttp.ClientSession,
        force: bool = False,
        chunk_size: int = 1024,
    ) -> None:
        """Download the image to the specified directory.

        If the image is already downloaded, this method will
        raise a ImageAlreadyExistsError unless force is set to True.
        After the image is downloaded, the path attribute will
        be set to the path
        """
        await self._download(
            force=force,
            directory=directory,
            chunk_size=chunk_size,
            session=session,
        )

    def compare(self, other: "Image", method: str = "mse") -> float:
        m = getattr(ImageCalculations, method, None)
        if m is None:
            raise ValueError(f"Invalid method {method}")
        c_img = cv2.imread(str(self.path))
        o_img = cv2.imread(str(other.path))
        c_img = cv2.cvtColor(c_img, cv2.COLOR_BGR2GRAY)
        o_img = cv2.cvtColor(o_img, cv2.COLOR_BGR2GRAY)
        h, w = c_img.shape
        o_img = cv2.resize(o_img, (w, h))
        return m(c_img, o_img)
