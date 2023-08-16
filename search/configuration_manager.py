''' contains config class '''

import os
import re
from typing import Union
from logging_manager import LoggingManager
from constants import ConfigEnum, Constants

class ConfigurationManager:
    ''' used to store and retrieve configuration info '''
    read_err_msg = '{filename} does not exist'

    def __init__(self, logger:LoggingManager, input_folder:str = 'input') -> None:
        self.logger = logger
        self.__input_folder = input_folder
        self.__info = {}

    def __read_file(self, filename, in_input_folder=True, critical=False) -> list:
        ''' checks if file exists and returns lines '''        
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

        lines = []
        with open(path, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                line = line.strip().lower()
                if (not line.startswith('#')) and (not line == ''):
                    lines.append(line)
        return lines

    def __add_repo_names(self, config_enum:ConfigEnum, critical=False) -> None:
        ''' adds either excluded or included repo names '''
        lines = self.__read_file(config_enum.value, critical)
        # replace spaces in repo names
        names = [name.replace(' ', Constants.ENCODED_SPACE) for name in lines]
        self.__info[config_enum.name] = names

    def add_included_repo_names(self) -> None:
        ''' adds included repo names '''
        # include mode must have input
        self.__add_repo_names(ConfigEnum.INCLUDED_REPOS, critical=True)

    def add_excluded_repo_names(self) -> None:
        ''' adds excluded repo names '''
        self.__add_repo_names(ConfigEnum.EXCLUDED_REPOS)

    def add_last_updated_info(self) -> None:
        ''' adds last updated info '''
        last_update_enum = ConfigEnum.LAST_UPDATE
        self.__info[last_update_enum.name] = {}

        lines = self.__read_file(last_update_enum.value, in_input_folder=False)
        for line in lines:
            # expected format - {name}\t{date}
            elements = line.split('\t')
            try:
                name = elements[0]
                date = float(elements[1])
            except (IndexError, ValueError) as err:
                self.logger.error(err, stdout=False)
                continue
            self.__info[last_update_enum.name][name] = date

    def add_pat(self) -> None:
        ''' adds PAT for ADO authentication '''
        pat_enum = ConfigEnum.PAT
        lines = self.__read_file(pat_enum.value, critical=True)
        try:
            pat = lines[0]
        except IndexError: #empty line
            self.logger.critical('PAT not given')
        self.__info[pat_enum.name] = pat

    def add_search_words(self) -> None:
        ''' adds search words '''
        search_words_enum = ConfigEnum.SEARCH_WORDS
        original = self.__read_file(search_words_enum.value)
        if len(original) == 0:
            self.logger.info('no search words, program will be used to update local repos')
        self.__info[search_words_enum.name] = [re.escape(word) for word in original]

    def add_excluded_files(self) -> None:
        ''' adds excluded files '''
        excluded_files_enum = ConfigEnum.EXCLUDED_FILES
        self.__info[excluded_files_enum.name] = self.__read_file(excluded_files_enum.value)

    def add_excluded_folders(self) -> None:
        ''' adds excluded folders'''
        excluded_folders_enum = ConfigEnum.EXCLUDED_FOLDERS
        self.__info[excluded_folders_enum.name] = self.__read_file(excluded_folders_enum.value)

    def get(self, label:str) -> Union[list, dict]:
        ''' get config info for specified label '''
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
