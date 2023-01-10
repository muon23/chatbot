from abc import ABC, abstractmethod
from typing import TypeVar


class Reactivation(ABC):
    Rule = TypeVar("Rule")

    @abstractmethod
    def tryActivate(self, rule: Rule):
        pass
