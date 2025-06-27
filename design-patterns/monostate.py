class Monostate:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Settings(Monostate):
    def __init__(self):
        super().__init__()
        self.theme="Light"


x = Settings()
y=Settings()
print(x.theme)
y.theme = "Dark"
print(x.theme)
print(y.theme)
print(y==x)