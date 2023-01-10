class Dao:
    @classmethod
    def of(cls, daoId: str) -> "Dao":
        pass

    def __init__(self, daoId: str):
        self.daoId = daoId
        pass

    def getNumMembers(self) -> int:
        pass

    def getQuorumSize(self) -> int:
        pass

    def establish(self):
        pass

    def getProperties(self) -> dict:
        pass
