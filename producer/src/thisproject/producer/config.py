import thisproject.boilerplate
from pydantic import constr
from pydantic.types import SecretStr


class ProducerSettings(thisproject.boilerplate.AppSettings):
    kafka_host: constr(min_length=1)
    kafka_cert: SecretStr
    kafka_key: SecretStr
    kafka_ca: SecretStr
    kafka_topic: constr(min_length=1)


settings = ProducerSettings()
