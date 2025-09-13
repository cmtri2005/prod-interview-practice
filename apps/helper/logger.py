import inspect
import logging
import threading


class LoggerSingleton:
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            frame = inspect.stack()[8]
            module = inspect.getmodule(frame[0])
            module_name = module.__name__ if module else ""
            class_name = ""
            if "self" in frame[0].f_locals:
                class_name = frame[0].f_locals["self"].__class__.__name__
            function_name = frame[3]
            caller_name = f"{module_name}.{class_name}.{function_name}".strip(".")

            color = Colors.WHITE
            if record.levelno == logging.DEBUG:
                color = Colors.PURPLE
            elif record.levelno == logging.INFO:
                color = Colors.GREEN
            elif record.levelno == logging.WARNING:
                color = Colors.YELLOW
            elif record.levelno == logging.ERROR:
                color = Colors.RED
            elif record.levelno == logging.CRITICAL:
                color = Colors.PURPLE

            record.msg = f"{color}{record.msg}{Colors.RESET}"
            record.name = caller_name
            return super().format(record)

    __instance = None
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = super().__new__(cls)
                    cls.__instance.__initialize(*args, **kwargs)
        return cls.__instance

    def __initialize(self, level=logging.DEBUG):
        self.__instance = logging.getLogger("LoggerSingleton")
        self.__instance.setLevel(level)
        self.__instance.propagate = False

        if not self.__instance.handlers:
            formatter = self.__get_color_formatter()

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.__instance.addHandler(console_handler)


    def __get_color_formatter(self):
        return self.ColoredFormatter(
            "%(asctime)s | %(name)s [%(levelname)s]: %(message)s (%(filename)s:%(lineno)d"
        )

    def set_level(self, level):
        self.__instance.setLevel(level)

    def get_instance(self):
        return self.__instance


class Colors:
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    DARKCYAN = "\033[36m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"