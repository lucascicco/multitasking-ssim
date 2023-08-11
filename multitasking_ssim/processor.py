import asyncio
import logging
from dataclasses import dataclass, field

import aiohttp
from aiopath.path import AsyncPath

from multitasking_ssim.exceptions import ImageDuplicateError
from multitasking_ssim.executors import download_image_ret_key
from multitasking_ssim.image import Image
from multitasking_ssim.utils.csv import CSVTable

log = logging.getLogger()


CALC_ROWS = ["mse", "ssim", "psnr"]
IMG_ROWS = ["id", *CALC_ROWS]


@dataclass
class ImageComparisonProcessor:
    download_directory: AsyncPath
    output_file: AsyncPath
    main_image: Image
    other_images: dict[str, Image]
    csv_table: CSVTable = field(init=False)
    concurrency: int = field(default=10)

    def __post_init__(self):
        self.csv_table = CSVTable(
            rows=IMG_ROWS,
            dest=self.output_file,
        )

    @classmethod
    async def from_config(cls, config):
        d_dir = await AsyncPath(config.download_directory).expanduser()
        o_file = await AsyncPath(config.output.file).expanduser()
        o_images = {}
        for image in config.images.others:
            if image.id in o_images:
                raise ImageDuplicateError(
                    f"Duplicate image id {image.id} found",
                )
            o_images[image.id] = Image.from_config(image)
        return cls(
            download_directory=d_dir,
            output_file=o_file,
            main_image=Image.from_config(config.images.main),
            other_images=o_images,
            concurrency=config.concurrency,
        )

    async def initialize(self):
        await self.download_directory.mkdir(parents=True, exist_ok=True)

    async def _generate_download_tasks(
        self,
        session: aiohttp.ClientSession,
    ) -> list[asyncio.Task[str]]:
        log.debug(f"Concurrently downloading {self.concurrency} images")
        sem = asyncio.Semaphore(self.concurrency)
        tasks: list[asyncio.Task[str]] = []
        for key, image in self.other_images.items():
            tasks.append(
                asyncio.create_task(
                    download_image_ret_key(
                        key=key,
                        image=image,
                        sem=sem,
                        session=session,
                        directory=self.download_directory,
                        force=True,
                    ),
                ),
            )
        return tasks

    async def _batch_process_tasks(
        self,
        tasks: list[asyncio.Task[str]],
    ):
        for task in asyncio.as_completed(tasks):
            t_id = await task
            log.info(f"Processing image {t_id}")
            c_image = self.other_images[t_id]
            row: list = [t_id]
            for c in CALC_ROWS:
                log.debug(f"Calculating {c} for image {t_id}")
                r = self.main_image.compare(
                    other=c_image,
                    method=c,
                )
                r = round(r, 2)
                row.append(r)
            yield (t_id, row)

    async def process(self):
        log.info("Starting image processing")
        session = aiohttp.ClientSession()
        log.debug(f"Downloading main image {self.main_image.id}")
        await self.main_image.download(
            directory=self.download_directory,
            session=session,
            force=True,
        )
        tasks = await self._generate_download_tasks(session)
        async with self.csv_table.init_writer(force=True) as writer:
            async for t_id, row in self._batch_process_tasks(tasks):
                await writer.writerow(row)
                log.info(f"Image {t_id} processed")
        log.debug("Closing session")
        await session.close()
