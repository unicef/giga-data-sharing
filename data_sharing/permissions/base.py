from abc import ABC, abstractmethod


class BasePermission(ABC):
    raise_exceptions: bool

    def __init__(self, raise_exceptions: bool):
        self.raise_exceptions = raise_exceptions

    @classmethod
    def raises(cls, raise_exceptions: bool):
        return cls(raise_exceptions)

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass
