from backend.app.services.datasource.base import BaseDataSource
from backend.app.services.datasource.akshare_source import AkshareDataSource
from backend.app.services.datasource.eastmoney_source import EastmoneyDataSource

__all__ = ["BaseDataSource", "AkshareDataSource", "EastmoneyDataSource", "get_datasource"]


def get_datasource(name: str = "auto") -> BaseDataSource:
    """Factory to get the configured data source.

    Args:
        name: Data source name. "auto" picks the primary from config, then tries backup.

    Returns:
        Configured BaseDataSource instance.
    """
    from backend.app.config import DATA_SOURCE, BACKUP_DATA_SOURCE

    sources: dict[str, BaseDataSource] = {
        "akshare": AkshareDataSource(),
        "eastmoney": EastmoneyDataSource(),
    }

    if name == "auto":
        name = DATA_SOURCE if DATA_SOURCE in sources else "akshare"

    source = sources.get(name, sources["akshare"])
    source._backup = sources.get(BACKUP_DATA_SOURCE) if BACKUP_DATA_SOURCE else None
    return source


def _get_source_or_fallback(primary_name: str) -> BaseDataSource:
    """Internal: get primary source with fallback configuration."""
    from backend.app.config import DATA_SOURCE, BACKUP_DATA_SOURCE

    sources = {
        "akshare": AkshareDataSource(),
        "eastmoney": EastmoneyDataSource(),
    }

    if primary_name in sources:
        source = sources[primary_name]
        if BACKUP_DATA_SOURCE and BACKUP_DATA_SOURCE in sources:
            source._backup = sources[BACKUP_DATA_SOURCE]
        return source
    return sources["akshare"]
