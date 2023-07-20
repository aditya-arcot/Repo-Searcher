import os

from configuration_manager import ConfigurationManager
from constants import Constants, ConfigEnum, RepoModeEnum
from logging_manager import LoggingManager

class RepoSearchResults:
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

    def __init__(self,
                 logger:LoggingManager,
                 output_folder:str = 'output'
                 ) -> None:
        self.logger = logger

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        self.__results_file = os.path.join(output_folder, 'results.txt')
        with open(self.__results_file, 'w', encoding='utf-8') as file:
            file.write('')

        self.__buffer = []
        self.__repo_counter = 0

    def __add_buffer_lines(self, lst:list) -> None:
        self.__buffer += lst

    def __add_buffer_line(self, line='') -> None:
        self.__buffer.append(line)

    def flush(self):
        with open(self.__results_file, 'a', encoding='utf-8') as file:
            for line in self.__buffer:
                file.write(line + Constants.NEWLINE)
        self.__buffer = []

    def write_config(self, repo_mode, config:ConfigurationManager):
        lines = [
            'Config',
            self.__format_config_section('Log file', [self.logger.filename]),
            self.__format_config_section('Search words', config.get(ConfigEnum.SEARCH_WORDS.name)),
            self.__format_config_section('Repo mode', [repo_mode]),
            self.__format_config_section('Included repos', \
                                            config.get(ConfigEnum.INCLUDED_REPOS.name)) \
                                            if repo_mode == RepoModeEnum.INCLUDE_MODE.name else \
                                                self.__format_config_section('Excluded repos', \
                                                config.get(ConfigEnum.EXCLUDED_REPOS.name)),
            self.__format_config_section('Excluded files', \
                                         config.get(ConfigEnum.EXCLUDED_FILES.name)),
            self.__format_config_section('Excluded folders', \
                                         config.get(ConfigEnum.EXCLUDED_FOLDERS.name))
        ]

        self.__add_buffer_lines(lines)
        self.__add_buffer_line()

    def __format_config_section(self, heading, lst:list):
        if lst is None:
            return Constants.TAB + heading
        spacing = Constants.NEWLINE + (Constants.TAB * 2)
        return Constants.TAB + heading + spacing + (spacing).join(lst)

    def write_repo_start(self, name):
        if self.__repo_counter == 0:
            self.__add_buffer_line('Repos')
        self.__add_buffer_line(Constants.TAB + name)
        self.__repo_counter += 1

    def write_repo_skip(self, reason):
        self.__add_buffer_line(Constants.TAB + Constants.TAB + f'skipped - {reason}')

    def write_repo_results(self, results:RepoSearchResults):
        self.__write_results_section('Matches', results.matches)
        self.__write_results_section('Errors', results.errors)
        self.__write_results_section('Skipped folders', results.skipped_folders)
        self.__write_results_section('Skipped files', results.skipped_files)
        self.__write_results_section('Searched folders', results.folders)
        self.__write_results_section('Searched files', results.files)

    def __write_results_section(self, section_name, results_section):
        if len(results_section) == 0:
            return

        spacer = Constants.TAB * 2

        if type(results_section) == list:
            self.__add_buffer_line(spacer + section_name + f'({len(results_section)})')

            spacer += Constants.TAB
            for i in results_section:
                self.__add_buffer_line(spacer + i)
        else:
            # matches dict
            lines = []
            lines.append(spacer + section_name)

            count = 0
            spacer += Constants.TAB
            for path in results_section.keys():
                lines.append(spacer + path)
                for search_word in results_section[path].keys():
                    lines.append((spacer + Constants.TAB) + search_word)
                    for match in results_section[path][search_word]:
                        lines.append((spacer + (Constants.TAB * 2)) + match)
                        count += 1

            lines[0] += f'({count})'
            self.__add_buffer_lines(lines)

    def write_repo_end(self):
        self.__add_buffer_line(Constants.NEWLINE)
        self.__add_buffer_line(Constants.NEWLINE)

    def write_found_words(self, words:set):
        self.__add_buffer_line('Found words')

        if len(words) == 0:
            return

        spacing = Constants.NEWLINE + Constants.TAB
        line = Constants.TAB + spacing.join(sorted(words))
        self.__add_buffer_line(line)
        self.__add_buffer_line()
