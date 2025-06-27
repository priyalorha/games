class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    def __init__(self):
        print("Logger")

    def log(self, msg):
        print(f"log {msg}")


log1 = Logger()

log2 = Logger()
print(log1 is log2)
