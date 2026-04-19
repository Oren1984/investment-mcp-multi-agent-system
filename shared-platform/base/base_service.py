class BaseService:
    def __init__(self, name: str):
        self.name = name

    def health(self) -> dict:
        return {"service": self.name, "status": "ok"}