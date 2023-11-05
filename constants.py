"""contains ConfigurationFile, BranchSearchResults, Constants, Messages classes"""


# pylint: disable=too-few-public-methods
class ConfigurationFile:
    """represents a config file"""

    def __init__(self, filename: str) -> None:
        self.__filename = filename

    # pylint: disable=missing-function-docstring
    def filename(self) -> str:
        return self.__filename

    # pylint: disable=missing-function-docstring
    def config_key(self) -> str:
        return self.__filename.split(".")[0]


# pylint: disable=too-few-public-methods
class BranchSearchResults:
    """represents results of branch search"""

    def __init__(self) -> None:
        self.matches = {}
        self.errors = []
        self.skipped_folders = []
        self.skipped_files = []
        self.folders = []
        self.files = []


# pylint: disable=missing-class-docstring
class Constants:
    # general
    TAB = "\t"
    NEWLINE = "\n"
    ENCODING = "utf-8"
    COMMENT_PREFIX = "#"
    WILDCARD = "*"
    # ENCODED_SPACE = "%20"
    RE_PATTERN = "(?<![a-z0-9_]){word}(?![a-z0-9_])"
    DEFAULT_TIME = -1

    # numbers
    SECONDS_IN_DAY = 86400
    TIMEOUT = 5
    RETRIES = 5
    SUCCESS_CODE = 200
    JSON_INDENT = 4
    MAX_PREVIEW_LENGTH = 5000

    # folders
    CONFIG_FOLDER = "config"
    REPOS_FOLDER = "repos"
    RESULTS_FOLDER = "results"

    # files
    LOG_FILE = "program.log"
    CONFIG_FILE = "config.txt"
    DETAILS_FILE = "details.txt"
    MATCHES_FILE = "matches.txt"
    FOUND_FILE = "found.txt"

    # ConfigFile objects
    TOKEN_FILE = ConfigurationFile("token.txt")
    REPO_DATA_FILE = ConfigurationFile("repo_data.json")
    WORDS_FILE = ConfigurationFile("words.txt")
    BRANCH_UPDATES_FILE = ConfigurationFile("branch_updates.json")
    EXCLUDE_FILES_FILE = ConfigurationFile("exclude_files.txt")
    EXCLUDE_FOLDERS_FILE = ConfigurationFile("exclude_folders.txt")
    INCLUDE_REPOS_FILE = ConfigurationFile("include_repos.txt")
    EXCLUDE_REPOS_FILE = ConfigurationFile("exclude_repos.txt")

    # search template
    NONE = "None"
    ALL = "All"
    DEFAULT = "Default"

    TEMPLATE_NONE = "no repos"
    TEMPLATE_DEFAULT = "all repos, default branch"
    TEMPLATE_ALL = "all repos, all branches"

    # config keys
    TEMPLATE_KEY = "template"
    OFFLINE_KEY = "offline"
    TARGET_REPOS_KEY = "target_repos"
    REPOS_KEY = "repos"

    # repo data keys
    LAST_UPDATE_KEY = "lastUpdate"
    VALUE_KEY = "value"
    DEFAULT_BRANCH_KEY = "defaultBranch"
    BRANCHES_KEY = "branches"
    NAME_KEY = "name"
    COUNT_KEY = "count"
    ID_KEY = "id"
    REMOTE_URL_KEY = "remoteUrl"

    # ADO - learn.microsoft.com/en-us/rest/api/azure/devops/git/?view=azure-devops-rest-7.0
    BASE_URL = "https://dev.azure.com/"
    __PROJECT = "bp-vsts/NAGPCCR/"
    __PREFIX = __PROJECT + "_apis/git/repositories"
    __POSTFIX = "api-version=7.0"
    REPOS_URL = BASE_URL + __PREFIX + "?" + __POSTFIX
    BRANCHES_URL = BASE_URL + __PREFIX + "/{id}/refs?filter=heads/&" + __POSTFIX
    BRANCH_PREFIX = "refs/heads/"


# pylint: disable=missing-class-docstring
class Messages:
    ## config manager
    UNHANDLED_TYPE = "unhandled config type - {type}"
    CONFIG_ITEM_NOT_FOUND = "config item doesn't exist (key-{key}, type-{type})"

    ## config handler
    # load template
    SELECT_REPO_TEMPLATE = "select a repo search template for initialization"
    SELECT_BRANCH_TEMPLATE = "select a branch search template for initialization"
    TEMPLATE = "search template - {template}"
    MODIFY_TEMPLATE = "include/exclude files will be used to modify this template"
    # get input
    ENTER_VALID_INTEGER = "enter a valid integer: "
    VALUE_ENTERED = "entered - {val}"
    INVALID_INTEGER = "invalid, please try again"
    KEYBOARD_INTERRUPT = "keyboard interrupt"
    # get connection status
    CONNECTION_FAILED = "connection failed"
    CONNECTION_STATUS = "offline - {offline}"
    # populate config
    TOKEN_FILE_SKIP = "skipping loading of token"
    LOCAL_REPO_DATA = "will attempt to use local repo data"
    # read file
    FILE_NOT_FOUND = "file not found - {path}"
    # load token
    TOKEN_REQUIRED = "token is required"
    # create repo data
    REPO_DATA_OK = "repo data exists and was updated within the last day"
    REPO_DATA_ISSUE = "repo data either doesn't exist or requires update"
    GETTING_REPO_DATA = "getting repo data"
    REPOS_MAX_RETRIES = "max retries requesting repo data"
    BAD_JSON = "badly formed json response"
    # make request
    REQUEST_FAILED = "request failed, trying again"
    # add branch info
    NO_DEFAULT = "{repo} has no default branch - most likely empty"
    GETTING_BRANCH_DATA = "getting branch data for {repo} ({pos}/{total})"
    BRANCH_MAX_RETRIES = "max retries requesting branch data, skipping"
    # write repo data
    PARSING_FAILED = "error parsing repo data"
    # load search words
    NO_WORDS = "no search words - program will be used to update local files"
    # load branch timestamps
    PARSING_FAILED = "parsing branch updates failed"
    # load repo data
    NO_REPO_DATA = "repo data file does not exist"
    # create target repos
    UNKNOWN_TEMPLATE = "unexpected template value - {template}"
    # add included repos
    BAD_REPO = "invalid repo - {repo}"
    BAD_BRANCH = "invalid branch - {branch} ({repo})"
    DEFAULT_BRANCH = "including default branch ({branch}) for {repo}"
    ALL_BRANCHES = "including all branches of {repo}"
    ONE_BRANCH = "including {branch} of {repo}"
    # remove excluded repos
    REPO_EXCLUDED = "repo {repo} is already not included"
    BRANCH_EXCLUDED = "branch {branch} of {repo} is already not included"
    EXCLUDING_ALL = "excluding all branches of {repo}"
    EXCLUDING_BRANCH = "excluding {branch} of {repo}"
    # create repos
    NO_URL = "url not found for {repo}"

    ## logging manager
    DEBUG_MSG = "debug - {msg}"
    INFO_MSG = "info - {msg}"
    ERR_MSG = "error - {msg}"
    CRIT_MSG = "critical - {msg}"
    EXITING = "exiting..."
    WARN_MSG = "warning - {msg}"

    ## repository
    STR = "{repo} - {url}, {branches}, {path}"
    PATH_EXISTS = "branch path exists"
    PATH_DOESNT_EXIST = "branch path does not exist"
    INTERVAL = 1
    RETRYING = f"trying again in {INTERVAL}s"
    GIT_MAX_RETRIES = "max retries for {mode}"
    GIT_SUCCESS = "{mode} success"
    GIT_FAILURE = "{mode} failed - {err}"
    PULL = "pull"
    CLONE = "clone"

    ## searcher
    SEARCHING = "starting search"
    SEARCHING_REPO = "repo {idx}/{total} - {name}"
    SEARCHING_BRANCH = "branch {idx}/{total} - {name}"
    UPDATE_NEEDED = "update required"
    UPDATE_FAILED = "update failed"
    UP_TO_DATE = "updated less than 1 day ago"
    NO_LOCAL = "branch files not locally available"
    NO_SEARCH = "no search words"
    BAD_PATH = "path does not exist"
    FILE = "file - {path}"
    LINE_TOO_LONG = "LINE TOO LONG - look at file"
    LINE = "line {idx} - {line}"
    MATCH = "match - {word} - {line}"
    PATH_TOO_LONG = "file not found - path too long? - {path}"
    DECODING_SUCCESS = "decoding success - {path}"
    DECODING_FAILED = "decoding failure - {path}"
