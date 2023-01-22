from abc import ABC, abstractmethod


class Summarizer(ABC):
    @abstractmethod
    async def summarize(self, **kwargs) -> str:
        pass
