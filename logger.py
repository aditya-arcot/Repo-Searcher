"""contains LoggingManager class"""

import os
import sys
import logging
from constants import Constants, Messages


class LoggingManager:
    """used for logging and printing"""

    def __init__(
        self, date: str, folder=Constants.RESULTS_FOLDER, level=logging.DEBUG
    ) -> None:
        path = os.path.join(folder, date)
        if not os.path.exists(path):
            os.makedirs(path)

        logging.basicConfig(
            level=level,
            filename=os.path.join(path, Constants.LOG_FILE),
            filemode="a",
            format="%(asctime)s - LOGGING.%(levelname)s - %(message)s",
        )

        self.logger = logging.getLogger()

    def debug(self, msg: str, stdout=True) -> None:
        """logs debug message"""
        self.logger.debug(msg)
        if stdout:
            print(Messages.DEBUG_MSG.format(msg=msg))

    def info(self, msg: str, stdout=True) -> None:
        """logs info message"""
        self.logger.info(msg)
        if stdout:
            print(Messages.INFO_MSG.format(msg=msg))

    def error(self, msg: str, stdout=True) -> None:
        """logs error message"""
        self.logger.error(msg)
        if stdout:
            print(Messages.ERR_MSG.format(msg=msg))

    def critical(self, msg: str, stdout=True) -> None:
        """logs critical message, exits program"""
        self.logger.critical(msg)
        if stdout:
            print(Messages.CRIT_MSG.format(msg=msg))
            print(Messages.EXITING)
        sys.exit()

    def warning(self, msg: str, stdout=True) -> None:
        """logs warning message"""
        self.logger.warning(msg)
        if stdout:
            print(Messages.WARN_MSG.format(msg=msg))
