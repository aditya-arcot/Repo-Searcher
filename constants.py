"""contains various constants"""

# pylint: disable=too-few-public-methods

from enum import Enum


class ConfigEnum(Enum):
    """enumerations for config info"""

    PAT = "token.txt"
    REPOS = "repos_info.json"
    LAST_UPDATE = "repos_update_info.json"
    INCLUDED_REPOS = "included_repos.txt"
    EXCLUDED_REPOS = "excluded_repos.txt"
    EXCLUDED_FILES = "excluded_files.txt"
    EXCLUDED_FOLDERS = "excluded_folders.txt"
    SEARCH_WORDS = "words.txt"
    SEARCH_TEMPLATE_MODE, EXCEL_SEARCH_MODE = range(2)


class SearchTemplateModeEnum(Enum):
    """enumerations for search template mode"""

    NO_REPOS_NO_BRANCHES, ALL_REPOS_DEFAULT_BRANCH, ALL_REPOS_ALL_BRANCHES = range(3)


class SearchExcelModelEnum(Enum):
    """enumerations for search excel mode"""

    NO, YES = range(2)


class Constants:
    """general use constants"""

    TAB = "\t"
    NEWLINE = "\n"
    ENCODED_SPACE = "%20"
    DAY_IN_SECONDS = 86400
