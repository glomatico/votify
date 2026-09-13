import importlib.util
import os

__version__ = "1.9.9"

# librespot 0.0.1 ships protobuf gencode that predates protoc 3.19 and only
# loads under the pure-Python protobuf implementation, which must be selected
# before protobuf is imported anywhere in the process. Only opt in when
# librespot is installed so users without it keep the faster default backend;
# librespot users get pure-Python protobuf even on other session types, which
# is negligible for votify's small, low-volume messages.
if importlib.util.find_spec("librespot") is not None:
    os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
