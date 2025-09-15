from logger import LoggerSingleton

logger = LoggerSingleton().get_instance()


def test_logger():
    logger.info("LOGGER INFO")
    logger.debug("LOGGER DEBUG")
    logger.error("LOGGER ERROR")
    
    
if __name__ == "__main__":
    test_logger()
    