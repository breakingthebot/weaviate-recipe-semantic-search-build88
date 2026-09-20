"""
Weaviate Client and Engine Singleton Provider.
Exposes access to the active Weaviate vector engine instance and handles resets.
"""

from src.config import settings
from src.engine.memory_weaviate import MemoryWeaviate

_weaviate_instance: MemoryWeaviate = MemoryWeaviate(class_name=settings.WEAVIATE_CLASS_NAME)


def get_weaviate_engine() -> MemoryWeaviate:
    """
    Returns the singleton Weaviate vector engine instance.
    """
    global _weaviate_instance
    return _weaviate_instance


def reset_weaviate_engine() -> None:
    """
    Resets all stored objects within the Weaviate vector engine for clean test isolation.
    """
    global _weaviate_instance
    _weaviate_instance.reset()
