import logging
import os
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import yaml
from pydantic import BaseSettings, constr
from pydantic.env_settings import SettingsSourceCallable
from pydantic.networks import PostgresDsn
from pydantic.types import SecretStr

logger = logging.getLogger(__name__)

CONFIG_DEFAULT = "config/settings.yml"
CONFIG = os.getenv("CONFIG", CONFIG_DEFAULT)


class YamlSettingsSource:
    __slots__ = ('yml_file',)

    def __init__(self, yml_file: Union[Path, str, None]):
        self.yml_file: Union[Path, str, None] = yml_file or Path(CONFIG_DEFAULT)

    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        logger.info(f"retrieving configuration from {self.yml_file}")
        with self.yml_file.open() as f:
            config_raw = yaml.safe_load(f) or {}
            return config_raw

    def __repr__(self) -> str:
        return f"YamlSettingsSource(yml_file={self.yml_file!r})"


class AppSettings(BaseSettings):
    kafka_host: constr(min_length=1)
    kafka_cert: SecretStr
    kafka_key: SecretStr
    kafka_ca: SecretStr
    kafka_topic: constr(min_length=1)
    pg_dsn: PostgresDsn

    class Config:
        case_sensitive = False

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            yml_settings = YamlSettingsSource(yml_file=Path(CONFIG))
            return (
                init_settings,
                env_settings,
                yml_settings,
                file_secret_settings,
            )


settings = AppSettings()
