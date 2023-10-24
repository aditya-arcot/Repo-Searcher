"""contains Logging Manager class"""

import os
import sys
import logging


class LoggingManager:
    """used for logging and printing"""

    def __init__(
        self, date: str, folder="results", filename="log.txt", level=logging.DEBUG
    ) -> None:
        self.filename = filename

        if not os.path.exists(os.path.join(folder, date)):
            os.makedirs(os.path.join(folder, date))

        self.__path = os.path.join(folder, date, self.filename)

        # set up logging configuration
        logging.basicConfig(
            level=level,
            filename=self.__path,
            filemode="a",  # append
            format="%(asctime)s - LOGGING.%(levelname)s - %(message)s",
        )

        self.logger = logging.getLogger()  # use root logger

    def debug(self, msg: str, stdout=True) -> None:
        """logs debug message"""
        self.logger.debug(msg)
        if stdout:
            print(f"debug - {msg}")

    def info(self, msg: str, stdout=True) -> None:
        """logs info message"""
        self.logger.info(msg)
        if stdout:
            print(f"info - {msg}")

    def error(self, msg: str, stdout=True) -> None:
        """logs error message"""
        self.logger.error(msg)
        if stdout:
            print(f"error - {msg}")

    def critical(self, msg: str, stdout=True) -> None:
        """logs critical message, exits program"""
        self.logger.critical(msg)
        if stdout:
            print(f"critical - {msg}")
            print("exiting")
        sys.exit()

    def warning(self, msg: str, stdout=True) -> None:
        """logs warning message"""
        self.logger.warning(msg)
        if stdout:
            print(f"warning - {msg}")
