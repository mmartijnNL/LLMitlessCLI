from abc import ABC, abstractmethod
from typing import Any
from ..context import Context

class BaseTool(ABC):

    @property
    @abstractmethod
    def definition(self) -> dict[str, Any]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def invoke(self, context: Context, **kwargs) -> str:
        pass

