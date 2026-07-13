from app.services.datasource.base import BaseDataSource
from app.services.datasource.akshare_source import AkshareDataSource
from app.services.datasource.eastmoney_source import EastmoneyDataSource

__all__ = ["BaseDataSource", "AkshareDataSource", "EastmoneyDataSource", "get_datasource"]


def get_datasource(name: str = "auto") -> BaseDataSource:
    """Factory to get the configured data source.

    Args:
        name: Data source name. "auto" picks the primary from config, then tries backup.

    Returns:
        Configured BaseDataSource instance.
    """
    from app.config import DATA_SOURCE, BACKUP_DATA_SOURCE

    sources: dict[str, BaseDataSource] = {
        "akshare": AkshareDataSource(),
        "eastmoney": EastmoneyDataSource(),
    }

    if name == "auto":
        name = DATA_SOURCE if DATA_SOURCE in sources else "akshare"

    source = sources.get(name, sources["akshare"])
    source._backup = sources.get(BACKUP_DATA_SOURCE) if BACKUP_DATA_SOURCE else None
    return source
