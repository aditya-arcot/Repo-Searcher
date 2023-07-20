''' contains logging manager class '''

import os
import sys
import logging
import datetime

class LoggingManager:
    ''' used for logging '''
    def __init__(self, logs_folder = 'logs', level = logging.DEBUG) -> None:
        cur_date = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        self.filename = f'log_{cur_date}.txt'
        self.__path = os.path.join(logs_folder, self.filename)

        if not os.path.exists(logs_folder):
            os.mkdir(logs_folder)

        # set up logging configuration
        logging.basicConfig(
            level=level,
            filename=self.__path,
            filemode='a', # append to log file
            format='%(asctime)s - LOGGING.%(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger() # use root logger

    def debug(self, msg:str, stdout=True) -> None:
        ''' logs debug message '''
        self.logger.debug(msg)
        if stdout:
            print(f'debug - {msg}')

    def info(self, msg:str, stdout=True) -> None:
        ''' logs info message '''
        self.logger.info(msg)
        if stdout:
            print(f'info - {msg}')

    def error(self, msg:str, stdout=True) -> None:
        ''' logs error message '''
        self.logger.error(msg)
        if stdout:
            print(f'error - {msg}')

    def critical(self, msg:str, stdout=True) -> None:
        ''' logs critical message, exits program '''
        self.logger.critical(msg)
        if stdout:
            print(f'critical - {msg}')
            print('exiting')
        sys.exit()

    def warning(self, msg:str, stdout=True) -> None:
        ''' logs warning message '''
        self.logger.warning(msg)
        if stdout:
            print(f'warning - {msg}')
