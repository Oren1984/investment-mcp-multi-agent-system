class BaseComponent:
    def __init__(self, component_name: str):
        self.component_name = component_name

    def info(self) -> dict:
        return {"component": self.component_name}