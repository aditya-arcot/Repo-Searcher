''' contains input manager class'''

from constants import RepoSearchModeEnum
from logging_manager import LoggingManager

class InputManager():
    ''' gets, processes user input for options '''

    def __init__(self, logger:LoggingManager) -> None:
        self.logger = logger

    def __read_option(self, name, options:list, match_vals:list) -> bool:
        ''' reads user input and compares against match list '''
        print()
        print(name)
        for option in options:
            print(' - ' + option)
        return input('make selection: ').lower() in match_vals

    def get_repo_mode(self):
        ''' sets repo mode based on user input '''
        repo_mode = RepoSearchModeEnum.INCLUDE_MODE.value
        if self.__read_option('repo mode?', ['include - default', 'exclude'],
                              ['e', 'ex', 'exclude']):
            repo_mode = RepoSearchModeEnum.EXCLUDE_MODE.value
        self.logger.info(f'repo mode - {RepoSearchModeEnum(repo_mode).name}')
        print()
        return repo_mode

    def get_search_excel(self):
        ''' sets search Excel based on user input '''
        search_excel = True
        if self.__read_option('search Excel files?', ['yes - default', 'no'],
                              ['no', 'n']):
            search_excel = False
        self.logger.info(f'search Excel - {search_excel}')
        print()
        return search_excel
