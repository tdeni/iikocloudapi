from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("iikocloudapi")
except PackageNotFoundError:  # pragma: no cover - running from a source checkout without installing
    __version__ = "0+unknown"
