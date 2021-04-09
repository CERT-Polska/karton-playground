from mwdb.core.config import AppConfig, app_config
from typedconfig import Config, group_key, key, section


@section("karton")
class KartonConfig(Config):
    config_path = key(cast=str, required=False, default=None)


class KartonAppConfig(AppConfig):
    karton = group_key(KartonConfig)


config = KartonAppConfig(provider=app_config.provider)
