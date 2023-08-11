from dataclasses import dataclass, field
from typing import Any

from .validators import validate_type_to_value


@dataclass(frozen=True)
class ImageSectionConfig:
    id: int  # noqa: A003
    src: str


@dataclass(frozen=True)
class ImagesSectionConfig:
    main: ImageSectionConfig
    others: list[ImageSectionConfig]


@dataclass(frozen=True)
class OutputSectionConfig:
    file: str


@dataclass(frozen=True)
class Configuration:
    download_directory: str
    output: OutputSectionConfig
    images: ImagesSectionConfig
    concurrency: int = field(default=5)

    @classmethod
    def _validate_dict(cls, config_dict: dict[str, Any]) -> None:
        validate_type_to_value(cls, config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "Configuration":
        cls._validate_dict(config_dict)
        return cls(
            download_directory=config_dict["download_directory"],
            output=OutputSectionConfig(
                file=config_dict["output"]["file"],
            ),
            images=ImagesSectionConfig(
                main=ImageSectionConfig(
                    id=config_dict["images"]["main"]["id"],
                    src=config_dict["images"]["main"]["src"],
                ),
                others=[
                    ImageSectionConfig(
                        id=image["id"],
                        src=image["src"],
                    )
                    for image in config_dict["images"]["others"]
                ],
            ),
            concurrency=config_dict["concurrency"],
        )
