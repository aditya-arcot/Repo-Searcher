from enum import Enum

class ConfigEnum(Enum):
    PAT = 'PAT.txt'
    SEARCH_WORDS = 'words.txt'
    INCLUDED_REPOS = 'included_repos.txt'
    EXCLUDED_REPOS = 'excluded_repos.txt'
    EXCLUDED_FILES = 'excluded_files.txt'
    EXCLUDED_FOLDERS = 'excluded_folders.txt'
    LAST_UPDATE = 'repos_last_update.txt'
    REPOS = 'repos_info.json'

class RepoModeEnum(Enum):
    INCLUDE_MODE, EXCLUDE_MODE = range(2)

class Constants:
    TAB = '\t'
    NEWLINE = '\n'
    ENCODED_SPACE = '%20'
