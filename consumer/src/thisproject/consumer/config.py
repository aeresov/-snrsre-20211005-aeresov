import thisproject.boilerplate
from pydantic import constr
from pydantic.networks import PostgresDsn
from pydantic.types import SecretStr


class ConsumerSettings(thisproject.boilerplate.AppSettings):
    kafka_host: constr(min_length=1)
    kafka_cert: SecretStr
    kafka_key: SecretStr
    kafka_ca: SecretStr
    kafka_topic: constr(min_length=1)
    pg_dsn: PostgresDsn


settings = ConsumerSettings()
