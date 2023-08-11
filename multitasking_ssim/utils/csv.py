import contextlib

from aiocsv.writers import AsyncWriter
from aiofiles import open as aopen
from aiopath.path import AsyncPath


def convert_to_header_key(key: str) -> str:
    return key.replace("_", " ").title()


class CSVTable:
    def __init__(
        self,
        rows: list[str],
        dest: AsyncPath,
    ) -> None:
        self.rows = rows
        self._dest = dest

    @property
    def dest(self) -> AsyncPath:
        return self._dest

    def _normalize_dict(self, row: dict) -> dict:
        return {convert_to_header_key(k): v for k, v in row.items()}

    async def write_row(
        self,
        writer: AsyncWriter,
        row: dict | list,
        normalize: bool = True,
    ) -> None:
        if isinstance(row, dict) and normalize:
            row = self._normalize_dict(row)
        await writer.writerow(row)

    @contextlib.asynccontextmanager
    async def init_writer(
        self,
        *,
        dest: AsyncPath | None = None,
        force: bool = False,
    ):
        new_dest = dest or self.dest
        if await new_dest.exists():
            if force:
                await new_dest.unlink()
            else:
                raise FileExistsError(f"File {dest} already exists")
        async with aopen(
            new_dest,
            mode="w",
        ) as f:
            writer = AsyncWriter(f)
            # NOTE: The first row is the header
            await writer.writerow(self.rows)
            await f.flush()
            try:
                yield writer
            finally:
                await f.flush()
