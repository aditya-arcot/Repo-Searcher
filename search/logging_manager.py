import os
import sys
import logging
import datetime

class LoggingManager:
    def __init__(self,
                 logs_folder:str = 'logs',
                 level:int = logging.DEBUG
                 ) -> None:
        now = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        self.filename = f'log_{now}.txt'
        self.__path = os.path.join(logs_folder, self.filename)

        if not os.path.exists(logs_folder):
            os.mkdir(logs_folder)

        logging.basicConfig(
            level=level,
            filename=self.__path,
            filemode='a',
            format='%(asctime)s - LOGGING.%(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger()

    def debug(self, msg, stdout=True):
        self.logger.debug(msg)
        if stdout:
            print(f'debug - {msg}')

    def info(self, msg, stdout=True):
        self.logger.info(msg)
        if stdout:
            print(f'info - {msg}')

    def error(self, msg, stdout=True):
        self.logger.error(msg)
        if stdout:
            print(f'error - {msg}')

    def critical(self, msg, stdout=True):
        self.logger.critical(msg)
        if stdout:
            print(f'critical - {msg}')
            print('exiting')
        sys.exit()

    def warning(self, msg, stdout=True):
        self.logger.warning(msg)
        if stdout:
            print(f'warning - {msg}')
