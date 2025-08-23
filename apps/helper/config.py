import dotenv
import json
import threading 
from helper.logger import LoggerSingleton

logger = LoggerSingleton().get_instance()

class ConfigSingleton:
    __instance = None 
    __lock = threading.Lock()
    
    def __new(cls, *args, **kwargs):
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = super().__new__(cls)
                    cls.__instance.__initialize(*args, **kwargs)
                    
    
    def __initialize(self):
        #config = dotenv.dotenv_values(".env")
        self.__instance = ConfigSingleton()
        
        logger.info(f"Config: {self.__instance.__dict__}")
        
    def get_instance(self):
        return self.__instance