import os

from configuration_manager import ConfigurationManager
from constants import Constants, ConfigEnum, RepoModeEnum
from logging_manager import LoggingManager

class RepoSearchResults:
    def __init__(self) -> None:
        self.errors = []
        self.skipped = []
        self.subfolders = []
        self.files = []
        self.matches = {}

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
        self.flush()

    def __format_config_section(self, heading, lst:list):
        if lst is None:
            return Constants.TAB + heading
        spacing = Constants.NEWLINE + Constants.TAB + Constants.TAB
        return Constants.TAB + heading + spacing + (spacing).join(lst)

    def write_repo_start(self, name):
        if self.__repo_counter == 0:
            self.__add_buffer_line('Repos')
        self.__add_buffer_line(Constants.TAB + name)
        self.__repo_counter += 1

    def write_repo_skip(self, reason):
        self.__add_buffer_line(Constants.TAB + Constants.TAB + f'skipped - {reason}')

    def write_repo_details(self, results:RepoSearchResults):
        ## TODO
        pass
        '''
        if len(matches) > 0:
            count = 0

            write_full_results_line('\tmatches:')
            for path in matches.keys():
                write_full_results_line(f'\t\t{path}')
                for search_word in matches[path].keys():
                    write_full_results_line(f'\t\t\t{search_word}')
                    for match in matches[path][search_word]:
                        write_full_results_line(f'\t\t\t\t{match}')
                        count += 1

            write_summary_results_line(f'\tmatches: {count}')

        if len(skipped) > 0:
            write_full_results_line('\tskipped:')
            for skip in skipped:
                write_full_results_line(f'\t\t{skip}')

            write_summary_results_line(f'\tskipped: {len(skipped)}')

        if len(errors) > 0:
            write_full_results_line('\terrors:')
            for error in errors:
                write_full_results_line(f'\t\t{error}')

            write_summary_results_line(f'\terrors: {len(errors)}')

        if len(searched_subfolders) > 0:
            write_full_results_line('\tsubfolders searched:')
            for folder in searched_subfolders:
                write_full_results_line(f'\t\t{folder}')

            write_summary_results_line(f'\tsubfolders searched: {len(searched_subfolders)}')

        if len(searched_files) > 0:
            write_full_results_line('\tfiles searched:')
            for file in searched_files:
                write_full_results_line(f'\t\t{file}')

            write_summary_results_line(f'\tfiles searched: {len(searched_files)}')

        '''

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
