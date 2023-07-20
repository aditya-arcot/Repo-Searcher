''' contains results, writer classes '''

import os
from typing import Union
from configuration_manager import ConfigurationManager
from constants import Constants, ConfigEnum, RepoSearchModeEnum
from logging_manager import LoggingManager

class RepoSearchResults:
    ''' used for storing search results '''    
    def __init__(self) -> None:
        self.matches = {}
        self.errors = []
        self.skipped_folders = []
        self.skipped_files = []
        self.folders = []
        self.files = []

class ResultsWriter:
    '''
    used to write results file
    lines are stored in buffer until flush is called
    '''
    def __init__(self, logger:LoggingManager, output_folder = 'output') -> None:
        self.logger = logger

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        self.__results_file = os.path.join(output_folder, 'results.txt')
        # write blank line to overwrite existing file
        with open(self.__results_file, 'w', encoding='utf-8') as file:
            file.write('')

        self.__buffer = []
        self.__repo_counter = 0

    def __add_buffer_lines(self, lst=None) -> None:
        if lst is None:
            lst = ['']
        self.__buffer += lst

    def __add_buffer_line(self, line='') -> None:
        self.__buffer.append(line)

    def __flush(self) -> None:
        ''' flushes buffer to results file '''
        with open(self.__results_file, 'a', encoding='utf-8') as file:
            for line in self.__buffer:
                file.write(line + Constants.NEWLINE)
        # reset buffer
        self.__buffer = []

    def write_config(self, repo_mode:str, config:ConfigurationManager) -> None:
        ''' writes info from configuration sections'''
        log_str = self.__config_str('Log file', [self.logger.filename])
        search_words_str = self.__config_str('Search words', \
                                             config.get(ConfigEnum.SEARCH_WORDS.name))
        repo_mode_str = self.__config_str('Repo mode', [repo_mode])

        if repo_mode == RepoSearchModeEnum.INCLUDE_MODE.name:
            included_repos_str = self.__config_str('Included repos', \
                                                   config.get(ConfigEnum.INCLUDED_REPOS.name))
        else:
            included_repos_str = self.__config_str('Excluded repos', \
                                                   config.get(ConfigEnum.EXCLUDED_REPOS.name))

        excluded_files_str = self.__config_str('Excluded files', \
                                               config.get(ConfigEnum.EXCLUDED_FILES.name))
        excluded_folders_str = self.__config_str('Excluded folders', \
                                                 config.get(ConfigEnum.EXCLUDED_FOLDERS.name))

        lines = [
            'Config',
            log_str,
            search_words_str,
            repo_mode_str,
            included_repos_str,
            excluded_files_str,
            excluded_folders_str
        ]

        self.__add_buffer_lines(lines)
        self.__add_buffer_line()
        self.__flush()

    def __config_str(self, heading:str, lst:list) -> str:
        ''' returns formatted string of config section '''
        if lst is None:
            return Constants.TAB + heading
        spacing = Constants.NEWLINE + (Constants.TAB * 2)
        return Constants.TAB + heading + spacing + (spacing).join(lst)

    def write_repo_start(self, name:str) -> None:
        ''' writes repo start section '''
        if self.__repo_counter == 0:
            self.__add_buffer_line('Repos')
        self.__add_buffer_line(Constants.TAB + name)
        self.__repo_counter += 1
        self.__flush()

    def write_repo_skip(self, reason:str) -> None:
        ''' writes repo skip section '''
        self.__add_buffer_line(Constants.TAB + Constants.TAB + f'skipped - {reason}')
        self.__flush()

    def write_repo_results(self, results:RepoSearchResults) -> None:
        ''' writes all search results sections '''
        self.__write_results_section('Matches', results.matches)
        self.__write_results_section('Errors', results.errors)
        self.__write_results_section('Skipped folders', results.skipped_folders)
        self.__write_results_section('Skipped files', results.skipped_files)
        self.__write_results_section('Searched folders', results.folders)
        self.__write_results_section('Searched files', results.files)
        self.__flush()

    def __write_results_section(self, section_name:str, results_section:Union[dict, list]) -> None:
        ''' writes search results section '''
        # skip section
        if len(results_section) == 0:
            return

        # left indent
        spacer = Constants.TAB * 2

        # all except matches
        if isinstance(results_section, list):
            self.__add_buffer_line(spacer + section_name + f'({len(results_section)})')

            # add indent
            spacer += Constants.TAB
            for i in results_section:
                self.__add_buffer_line(spacer + i)

        # matches dict
        else:
            matches = results_section

            lines = []
            lines.append(spacer + section_name)

            count = 0
            spacer += Constants.TAB
            for path in matches.keys():
                lines.append(spacer + path)
                for search_word in matches[path].keys():
                    lines.append((spacer + Constants.TAB) + search_word)
                    for match in matches[path][search_word]:
                        lines.append((spacer + (Constants.TAB * 2)) + match)
                        count += 1 # increment for each match

            # add count to matches line
            lines[0] += f'({count})'
            self.__add_buffer_lines(lines)

    def write_repo_end(self) -> None:
        ''' writes space between repos '''
        self.__add_buffer_line(Constants.NEWLINE)
        self.__add_buffer_line(Constants.NEWLINE)
        self.__flush()

    def write_found_words(self, words:set) -> None:
        ''' writes list of words found in search'''
        self.__add_buffer_line('Found words')

        if len(words) == 0:
            return

        spacing = Constants.NEWLINE + Constants.TAB
        line = Constants.TAB + spacing.join(sorted(words))
        self.__add_buffer_line(line)
        self.__add_buffer_line()
        self.__flush()
