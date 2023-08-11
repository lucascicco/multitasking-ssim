from typing import Any

import aiofiles
import yaml


class YamlParser:
    @staticmethod
    async def load_values_from_file(
        fp: str,
    ) -> dict[str, Any]:
        async with aiofiles.open(fp, "r") as f:
            contents = await f.read()
        try:
            file_artifacts = yaml.safe_load(contents)
        except yaml.YAMLError:
            raise
        else:
            return file_artifacts
