''' contains config class '''

import os
import re
from logging_manager import LoggingManager
from constants import ConfigEnum, Constants

class ConfigurationManager:
    ''' used to store and retrieve configuration info '''
    read_err_msg = '{filename} does not exist'

    def __init__(self, logger:LoggingManager, input_folder:str = 'input') -> None:
        self.logger = logger
        self.__input_folder = input_folder
        self.__str_info:  dict[str, str] = {}
        self.__list_info: dict[str, list] = {}
        self.__dict_info: dict[str, dict] = {}

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
        self.__list_info[config_enum.name] = names

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
        self.__dict_info[last_update_enum.name] = {}

        lines = self.__read_file(last_update_enum.value, in_input_folder=False)
        for line in lines:
            # expected format - {name}\t{date}
            elements = line.split('\t')
            try:
                name = elements[0]
                date = float(elements[1])
            except (IndexError, ValueError) as err:
                self.logger.error(repr(err), stdout=False)
                continue
            self.__dict_info[last_update_enum.name][name] = date

    def add_pat(self) -> None:
        ''' adds PAT for ADO authentication '''
        pat_enum = ConfigEnum.PAT
        lines = self.__read_file(pat_enum.value, critical=True)
        try:
            pat = lines[0]
        except IndexError: #empty line
            self.logger.critical('PAT not given')
            return
        self.__str_info[pat_enum.name] = pat

    def add_search_words(self) -> None:
        ''' adds search words '''
        search_words_enum = ConfigEnum.SEARCH_WORDS
        original = self.__read_file(search_words_enum.value)
        if len(original) == 0:
            self.logger.info('no search words, program will be used to update local repos')
        self.__list_info[search_words_enum.name] = [re.escape(word) for word in original]

    def add_excluded_files(self) -> None:
        ''' adds excluded files '''
        excluded_files_enum = ConfigEnum.EXCLUDED_FILES
        self.__list_info[excluded_files_enum.name] = self.__read_file(excluded_files_enum.value)

    def add_excluded_folders(self) -> None:
        ''' adds excluded folders'''
        excluded_folders_enum = ConfigEnum.EXCLUDED_FOLDERS
        self.__list_info[excluded_folders_enum.name] = self.__read_file(excluded_folders_enum.value)

    def get_str(self, label:str) -> str:
        ''' get config info of type string for label '''
        if label in self.__str_info:
            return self.__str_info[label]
        self.__get_error(label, 'str')
        return ''

    def get_dict(self, label:str) -> dict:
        ''' get config info of type dict for label '''
        if label in self.__dict_info:
            return self.__dict_info[label]
        self.__get_error(label, 'dict')
        return {}

    def get_list(self, label:str) -> list:
        ''' get config info of type list for label '''
        if label in self.__list_info:
            return self.__list_info[label]
        self.__get_error(label, 'list')
        return []

    def __get_error(self, label:str, _type:str) -> None:
        ''' report error finding config info '''
        self.logger.error(f'{label} not present in {_type} info')

    def __repr__(self) -> str:
        return self.__repr_helper(self.__str_info) + \
               self.__repr_helper(self.__dict_info) + \
               self.__repr_helper(self.__list_info)

    def __repr_helper(self, pairs:dict) -> str:
        out = ''
        for key, value in pairs.items():
            out += key + Constants.NEWLINE
            out += repr(value) + Constants.NEWLINE
            out += Constants.NEWLINE
        return out
