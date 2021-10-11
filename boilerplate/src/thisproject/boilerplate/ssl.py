import contextlib
import ssl
import tempfile
from ssl import SSLContext


def _temp_file(content: str):
    # quickly create temp file with required content
    file = tempfile.NamedTemporaryFile(mode="w")
    file.write(content)
    file.flush()
    file.seek(0)
    return file


def create_context(cert: str, key: str, ca: str) -> SSLContext:
    with contextlib.ExitStack() as stack:
        cert_file = stack.enter_context(_temp_file(cert))
        key_file = stack.enter_context(_temp_file(key))
        ca_file = stack.enter_context(_temp_file(ca))

        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile=ca_file.name,
        )
        ssl_context.load_cert_chain(
            certfile=cert_file.name,
            keyfile=key_file.name,
        )
        return ssl_context
