import logging
import logging.config
import os

LOG_FORMAT = "%(asctime)s %(message)s"
DEFAULT_LEVEL = logging.DEBUG

class LogWrapper:
    PATH = './logs'

    def __init__(self,name,mode="w"):
        self.createLogsFolder(LogWrapper.PATH)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEFAULT_LEVEL)
        filename=f"{LogWrapper.PATH}/{name}.log"
        fileHandler = logging.FileHandler(filename,mode)
        formatter = logging.Formatter("%(asctime)s %(message)s",datefmt="%Y-%m-%d *** %H:%M:%S")
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)
        self.logger.info(f"LogWrapper init() {filename}")


    def createLogsFolder(self,path):
        if (not os.path.exists(path)):
            os.makedirs(path)

        