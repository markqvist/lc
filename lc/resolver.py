from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Context:
    """Context passed to resolvers during initialization."""
    
    def __init__(self, session=None, config=None):
        self.session = session
        self.config = config
        self._cache: Dict[str, Any] = {}
    
    def cache_get(self, key: str) -> Any: return self._cache.get(key)
    def cache_set(self, key: str, value: Any) -> None: self._cache[key] = value

class Resolver(ABC):
    """Base class for context resolvers."""
    
    @abstractmethod
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """
        Resolve context variables.
        
        Args:
            context: Execution context with session and config access
        
        Returns:
            Dictionary of variables to inject into template, or None if unavailable
        """
        pass
