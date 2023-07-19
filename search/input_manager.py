from constants import RepoModeEnum
from logging_manager import LoggingManager

class InputManager():
    def __init__(self, logger:LoggingManager) -> None:
        self.logger = logger

    def __read_option(self, name, options:list, match_vals:list, match_result, no_match_result):
        print()
        print(name)
        for option in options:
            print(' - ' + option)
        if input('make selection: ').lower() in match_vals:
            return match_result
        return no_match_result

    def get_repo_mode(self):
        repo_mode = self.__read_option('repo mode?',
                            ['include - default', 'exclude'],
                            ['e', 'ex', 'exclude'],
                            RepoModeEnum.EXCLUDE_MODE.value,
                            RepoModeEnum.INCLUDE_MODE.value)
        self.logger.info(f'repo mode - {RepoModeEnum(repo_mode).name}')
        print()
        return repo_mode

    def get_search_excel(self):
        search_excel = self.__read_option('search Excel files?',
                                ['yes - default', 'no'],
                                ['no', 'n'],
                                False, True)
        self.logger.info(f'search Excel - {search_excel}')
        print()
        return search_excel
