

from ssl import SSLContext

import ssl
import contextlib
import tempfile
from .config import settings


def _temp_file(content: str):
    # quickly create temp file with required content
    file = tempfile.NamedTemporaryFile(mode="w")
    file.write(content)
    file.flush()
    file.seek(0)
    return file


def create_context() -> SSLContext:
    with contextlib.ExitStack() as stack:
        cert_file = stack.enter_context(_temp_file(settings.kafka_cert.get_secret_value()))
        key_file = stack.enter_context(_temp_file(settings.kafka_key.get_secret_value()))
        ca_file = stack.enter_context(_temp_file(settings.kafka_ca.get_secret_value()))

        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile=ca_file.name,
        )
        ssl_context.load_cert_chain(
            certfile=cert_file.name,
            keyfile=key_file.name,
        )
        return ssl_context
