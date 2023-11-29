from abc import ABC, abstractmethod


class BasePermission(ABC):
    raise_exceptions: bool

    @classmethod
    def raises(cls, raise_exceptions: bool):
        cls.raise_exceptions = raise_exceptions
        return cls

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass
