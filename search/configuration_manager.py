import os
import re
import sys

from logging_manager import LoggingManager
from constants import ConfigEnum, Constants

class ConfigurationManager:
    read_err_msg = '{filename} does not exist'

    def __init__(self,
                logger:LoggingManager,
                input_folder:str = 'input',
                ) -> None:
        self.logger = logger
        self.__input_folder = input_folder
        self.__info = {}

    def __read_file(self, filename, in_input_folder=True, critical=False):
        if in_input_folder:
            path = os.path.join(self.__input_folder, filename)
        else:
            path = filename
        if not os.path.exists(path):
            if critical:
                self.logger.critical(self.read_err_msg.format(filename=filename))
            else:
                self.logger.warning(self.read_err_msg.format(filename=filename))
                return []

        out = []
        with open(path, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                line = line.strip().lower()
                if (not line.startswith('#')) and (not line == ''):
                    out.append(line)
        return out

    def __add_repo_names(self, config_enum:ConfigEnum, critical=False):
        lines = self.__read_file(config_enum.value, critical)
        names = [name.replace(' ', Constants.ENCODED_SPACE) for name in lines]
        self.__info[config_enum.name] = names

    def add_included_repo_names(self, config_enum:ConfigEnum):
        # included mode must have input
        self.__add_repo_names(config_enum, critical=True)

    def add_excluded_repo_names(self, config_enum:ConfigEnum):
        self.__add_repo_names(config_enum)

    def add_last_updated_info(self, config_enum:ConfigEnum):
        self.__info[config_enum.name] = {}
        lines = self.__read_file(config_enum.value, in_input_folder=False)
        for line in lines:
            elements = line.split('\t')

            try:
                name = elements[0]
                date = float(elements[1])
            except (IndexError, ValueError) as err:
                self.logger.error(err, stdout=False)

            self.__info[config_enum.name][name] = date

    def add_PAT(self, config_enum:ConfigEnum):
        lines = self.__read_file(config_enum.value, critical=True)
        try:
            PAT = lines[0]
        except IndexError:
            self.logger.critical('PAT not given')
        self.__info[config_enum.name] = PAT

    def add_search_words(self, config_enum:ConfigEnum):
        original = self.__read_file(config_enum.value, critical=True)
        #print([re.escape(word) for word in original])
        self.__info[config_enum.name] = [re.escape(word) for word in original]

    def add_excluded_files(self, config_enum:ConfigEnum):
        self.__info[config_enum.name] = self.__read_file(config_enum.value)

    def add_excluded_folders(self, config_enum:ConfigEnum):
        self.__info[config_enum.name] = self.__read_file(config_enum.value)

    def get(self, label):
        if label in self.__info:
            return self.__info[label]
        self.logger.error(f'{label} info not present')
        return None

    def __repr__(self) -> str:
        out = ''
        for key, value in self.__info.items():
            out += key + Constants.NEWLINE
            out += value.__repr__() + Constants.NEWLINE
            out += Constants.NEWLINE
        return out
