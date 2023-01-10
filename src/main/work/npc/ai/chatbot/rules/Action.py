from abc import ABC, abstractmethod


class Action(ABC):

    @abstractmethod
    def act(self, userId: str = None):
        pass

    @abstractmethod
    def getProperties(self) -> dict:
        pass


signInJwt = {
    "device_id": "63b46ef822a55406be579b0d",
    "user_id": "63b4a76822a55406be579b0e",
    "tacit": "xxxxxxxxxxxxxxxxxxxxxxxx"
}
