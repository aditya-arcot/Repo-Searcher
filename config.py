"""contains ConfigurationManager, ConfigurationHandler classes"""

import os
import re
import time
import sys
import json
from typing import Optional, Union
import toml
import requests
from logger import LoggingManager
from constants import Messages, Constants, ConfigurationFile
from repository import ADORepository


class ConfigurationManager:
    """used to store and retrieve configuration info"""

    def __init__(self, logger: LoggingManager) -> None:
        self.__logger: LoggingManager = logger
        self.__config: dict[type, dict] = {}

    def set_config(self, key: str, val: Union[str, bool, list, dict]):
        """set key, value pair"""
        if not isinstance(val, (str, bool, list, dict)):
            self.__logger.critical(
                Messages.UNHANDLED_TYPE.format(type=type(key).__name__)
            )
        self.__set_config_helper(type(val), key, val)

    def __set_config_helper(
        self, _type: type, key: str, val: Union[str, bool, list, dict]
    ) -> None:
        if _type not in self.__config:
            self.__config[_type] = {}
        self.__config[_type][key] = val

    def __get_helper(self, key: str, _type: type) -> tuple:
        if key in self.__config[_type]:
            return True, self.__config[_type][key]
        self.__logger.error(
            Messages.CONFIG_ITEM_NOT_FOUND.format(key=key, type=_type.__name__)
        )
        return False, -1

    def get_str(self, key: str, default: str = "") -> str:
        """get string with specified key"""
        found, val = self.__get_helper(key, str)
        if found:
            return val
        return default

    def get_bool(self, key: str, default=False) -> bool:
        """get boolean with specified key"""
        found, val = self.__get_helper(key, bool)
        if found:
            return val
        return default

    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """get list with specified key"""
        found, val = self.__get_helper(key, list)
        if found:
            return val
        return [] if default is None else default

    def get_dict(self, key: str, default: Optional[dict] = None) -> dict:
        """get dict with specified key"""
        found, val = self.__get_helper(key, dict)
        if found:
            return val
        return {} if default is None else default

    def config_str(self) -> str:
        """creates string of config info"""
        out = []
        for _type, config in self.__config.items():
            out.append(_type.__name__)
            for key, val in config.items():
                out.append(Constants.TAB + key)
                out.append((Constants.TAB * 2) + str(val))
        return Constants.NEWLINE.join(out)


# pylint: disable=too-few-public-methods
class ConfigurationHandler:
    """used to add config to manager"""

    def __init__(
        self, config_manager: ConfigurationManager, logger: LoggingManager
    ) -> None:
        self.__config_manager = config_manager
        self.__logger = logger
        self.__config_folder = Constants.CONFIG_FOLDER

    def populate_config(self) -> None:
        """populate config manager with files, user input, and other logic"""
        self.__load_template()
        self.__load_search_pattern()
        offline = self.__get_connection_status()
        if offline:
            self.__logger.info(Messages.ADO_CONFIG_SKIP)
            self.__logger.info(Messages.LOCAL_REPO_DATA)
        else:
            self.__load_ado_config()
            self.__create_repo_data()
        self.__load_search_words()
        self.__load_branch_timestamps()
        self.__load_excluded_files()
        self.__load_excluded_folders()
        self.__load_included_repos()
        self.__load_excluded_repos()
        self.__load_repo_data()
        self.__create_target_repos()
        self.__create_repos(offline)

    def write_branch_updates(self) -> None:
        """write branch updates to json file"""
        branch_updates_file = Constants.BRANCH_UPDATES_FILE
        branch_updates = self.__config_manager.get_dict(
            branch_updates_file.config_key()
        )
        with open(
            os.path.join(Constants.CONFIG_FOLDER, branch_updates_file.filename()),
            "w",
            encoding=Constants.ENCODING,
        ) as file:
            json.dump(branch_updates, file, indent=Constants.JSON_INDENT)

    def __load_template(
        self,
    ) -> None:
        """repo/branch template for search"""
        self.__logger.info(Messages.SELECT_REPO_TEMPLATE)
        repo_mode = self.__get_choice_index([Messages.NONE, Messages.ALL])
        if repo_mode == 0:
            template = Messages.TEMPLATE_NONE
        else:
            self.__logger.info(Messages.SELECT_BRANCH_TEMPLATE)
            branch_mode = self.__get_choice_index([Messages.DEFAULT, Messages.ALL])
            if branch_mode == 0:
                template = Messages.TEMPLATE_DEFAULT
            else:
                template = Messages.TEMPLATE_ALL

        self.__config_manager.set_config(Constants.TEMPLATE_KEY, template)
        self.__logger.info(Messages.TEMPLATE.format(template=template))
        self.__logger.info(Messages.MODIFY_TEMPLATE)

    def __load_search_pattern(self) -> None:
        """regex search pattern"""
        self.__logger.info(Messages.SELECT_REGEX_PATTERN)
        options = [
            Constants.NO_PATTERN,
            Constants.DB_TABLE_PATTERN,
            Messages.CUSTOM_PATTERN,
        ]
        choice = self.__get_choice_index(options)
        match choice:
            case 0:
                pattern = Constants.NO_PATTERN.pattern
            case 1:
                pattern = Constants.DB_TABLE_PATTERN.pattern
            case _:
                pattern = self.__get_custom_regex_pattern()
        self.__config_manager.set_config(Constants.PATTERN_KEY, pattern)
        self.__logger.info(Messages.PATTERN.format(pattern=pattern))

    def __get_choice_index(self, options: list) -> int:
        """gets user choice index from options"""
        for ind, option in enumerate(options):
            self.__logger.info(f"{ind} - {option}")

        while True:
            try:
                _input = input(Messages.ENTER_VALID_INTEGER)
                self.__logger.info(Messages.VALUE_ENTERED.format(val=_input))
                _input = int(_input)
                if _input in range(len(options)):
                    return _input
            except KeyboardInterrupt:
                self.__logger.critical(Messages.KEYBOARD_INTERRUPT)
            except ValueError:
                self.__logger.info(Messages.INVALID_INTEGER)

    def __get_custom_regex_pattern(self):
        """gets custom regex pattern from user input"""
        self.__logger.info(Messages.ENTER_REGEX_PATTERN)
        while True:
            try:
                pattern = input(Messages.ENTER_VALID_PATTERN)
                self.__logger.info(Messages.VALUE_ENTERED.format(val=pattern))
                if not "{word}" in pattern:
                    continue
                re.compile(pattern)
                return pattern
            except KeyboardInterrupt:
                self.__logger.critical(Messages.KEYBOARD_INTERRUPT)
            except re.error:
                continue

    def __get_connection_status(self) -> bool:
        """status of connection request to ADO"""
        try:
            response = requests.get(Constants.BASE_URL, timeout=Constants.TIMEOUT)
            offline = response.status_code != 200
        except requests.ConnectionError:
            offline = True

        if offline:
            self.__logger.info(Messages.CONNECTION_FAILED)
        self.__config_manager.set_config(Constants.OFFLINE_KEY, offline)
        self.__logger.info(Messages.CONNECTION_STATUS.format(offline=offline))
        return offline

    def __read_file(self, filename: str, lowercase=False) -> list[str]:
        """filters and strips lines from file"""
        path = os.path.join(self.__config_folder, filename)
        if not os.path.exists(path):
            error = Messages.FILE_NOT_FOUND.format(path=path)
            self.__logger.warning(error)
            return []

        lines = []
        with open(path, "r", encoding=Constants.ENCODING) as file:
            for line in file.readlines():
                line = line.strip()
                if line.startswith(Constants.CONFIG_COMMENT_PREFIX) or line == "":
                    continue
                if lowercase:
                    line = line.lower()
                lines.append(line)
        return lines

    def __load_ado_config(self) -> None:
        """PAT, org, and project for ADO"""
        ado_config_file = Constants.ADO_CONFIG_FILE
        lines = self.__read_file(ado_config_file)
        if not lines:
            self.__logger.critical(Messages.ADO_CONFIG_REQUIRED)

        try:
            config = toml.loads(Constants.NEWLINE.join(lines))
        except toml.decoder.TomlDecodeError:
            self.__logger.critical(Messages.BAD_TOML)
            sys.exit()

        token_key = Constants.TOKEN_KEY
        org_key = Constants.ORG_KEY
        project_key = Constants.PROJECT_KEY

        if any(s not in config for s in (token_key, org_key, project_key)):
            self.__logger.critical(Messages.MISSING_INFO)
            sys.exit()

        self.__config_manager.set_config(token_key, config[token_key])
        self.__config_manager.set_config(org_key, config[org_key])
        self.__config_manager.set_config(project_key, config[project_key])

    def __read_repo_data(self, filename) -> dict:
        lines = self.__read_file(filename)
        if not lines:
            return {}

        data = json.loads("".join(lines))
        if Constants.LAST_UPDATE_KEY not in data:
            return {}
        if time.time() - data[Constants.LAST_UPDATE_KEY] > Constants.SECONDS_IN_DAY:
            return {}

        return data

    def __write_repo_data(self, data: dict, filename) -> None:
        try:
            with open(
                os.path.join(self.__config_folder, filename),
                "w",
                encoding=Constants.ENCODING,
            ) as json_file:
                json.dump(data, json_file, indent=Constants.JSON_INDENT)
        except requests.exceptions.JSONDecodeError:
            self.__logger.critical(Messages.PARSING_FAILED)

    def __create_repo_data(self) -> None:
        """create json with repository and branch info from ADO"""
        json_filename = Constants.REPO_DATA_FILE.filename()
        data = self.__read_repo_data(json_filename)
        if data:
            self.__logger.info(Messages.REPO_DATA_OK)
            return
        self.__logger.info(Messages.REPO_DATA_ISSUE)
        self.__logger.info(Messages.GETTING_REPO_DATA)

        org = self.__config_manager.get_str(Constants.ORG_KEY)
        project = self.__config_manager.get_str(Constants.PROJECT_KEY)
        auth = (
            "user",
            self.__config_manager.get_str(Constants.TOKEN_KEY),
        )
        resp = self.__make_request(
            Constants.REPOS_URL.format(org=org, project=project),
            auth,
            Messages.REPOS_MAX_RETRIES,
        )
        assert resp is not None
        data = resp.json()
        if Constants.VALUE_KEY not in data:
            self.__logger.critical(Messages.BAD_JSON)

        self.__add_branch_info(data, auth, org, project)

        data[Constants.LAST_UPDATE_KEY] = time.time()
        self.__write_repo_data(data, json_filename)

    def __make_request(
        self, url, auth, error_msg
    ) -> Optional[requests.models.Response]:
        attempts = 0
        resp = None

        while attempts < Constants.RETRIES:
            try:
                resp = requests.get(url, auth=auth, timeout=Constants.TIMEOUT)
                if resp.status_code == Constants.SUCCESS_CODE:
                    return resp
                attempts += 1
                self.__logger.error(Messages.REQUEST_FAILED)

            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
            ) as e:
                attempts += 1
                self.__logger.error(f"{Messages.REQUEST_FAILED} - {e}")

        self.__logger.critical(error_msg)
        return resp

    def __add_branch_info(
        self, data: dict, auth: tuple, org: str, project: str
    ) -> None:
        for pos, repo in enumerate(data[Constants.VALUE_KEY]):
            if Constants.DEFAULT_BRANCH_KEY not in repo:
                self.__logger.error(
                    Messages.NO_DEFAULT.format(repo=repo[Constants.NAME_KEY])
                )
                data[Constants.VALUE_KEY][pos][Constants.BRANCHES_KEY] = []
                continue

            repo[Constants.DEFAULT_BRANCH_KEY] = repo[
                Constants.DEFAULT_BRANCH_KEY
            ].replace(Constants.BRANCH_PREFIX, "", 1)

            self.__logger.info(
                Messages.GETTING_BRANCH_DATA.format(
                    repo=repo[Constants.NAME_KEY],
                    pos=pos + 1,
                    total=data[Constants.COUNT_KEY],
                )
            )

            url = Constants.BRANCHES_URL.format(
                org=org, project=project, id=repo[Constants.ID_KEY]
            )
            resp = self.__make_request(url, auth, Messages.BRANCH_MAX_RETRIES)
            if not resp:
                sys.exit()

            branches_data = resp.json()
            branches = [
                branch[Constants.NAME_KEY].replace(Constants.BRANCH_PREFIX, "", 1)
                for branch in branches_data[Constants.VALUE_KEY]
            ]
            assert repo[Constants.DEFAULT_BRANCH_KEY] in branches
            data[Constants.VALUE_KEY][pos][Constants.BRANCHES_KEY] = branches

    def __load_search_words(self) -> None:
        """words to be used in repo search"""
        words_file = Constants.WORDS_FILE
        words = self.__read_file(words_file.filename(), lowercase=True)
        if not words:
            self.__logger.info(Messages.NO_WORDS)
        self.__config_manager.set_config(words_file.config_key(), words)

    def __load_branch_timestamps(self) -> None:
        """last updated timestamps for branches"""
        branch_updates_file = Constants.BRANCH_UPDATES_FILE
        lines = self.__read_file(branch_updates_file.filename())
        data = {}
        if lines:
            try:
                data = json.loads("".join(lines))
            except json.decoder.JSONDecodeError:
                self.__logger.error(Messages.PARSING_FAILED.format())
        self.__config_manager.set_config(branch_updates_file.config_key(), data)

    def __load_excluded_files(self) -> None:
        """files excluded from search"""
        exclude_files_file = Constants.EXCLUDE_FILES_FILE
        files = self.__read_file(exclude_files_file.filename(), lowercase=True)
        self.__config_manager.set_config(exclude_files_file.config_key(), files)

    def __load_excluded_folders(self) -> None:
        """folders excluded from search"""
        exclude_folders_file = Constants.EXCLUDE_FOLDERS_FILE
        files = self.__read_file(exclude_folders_file.filename(), lowercase=True)
        self.__config_manager.set_config(exclude_folders_file.config_key(), files)

    def __load_repos(self, repos_file: ConfigurationFile) -> None:
        lines = self.__read_file(repos_file.filename())
        repos = {}

        for line in lines:
            split = line.split()
            repo = split[0]
            # empty set if no branches specified
            branches = set(split[1:])

            if repo not in repos:
                repos[repo] = set()
            # preserve previously inputted branches
            repos[repo] = repos[repo] | branches

        self.__config_manager.set_config(repos_file.config_key(), repos)

    def __load_included_repos(self) -> None:
        """repos and branches explicitly included in search"""
        self.__load_repos(Constants.INCLUDE_REPOS_FILE)

    def __load_excluded_repos(self) -> None:
        """repos and branches explicitly excluded from search"""
        self.__load_repos(Constants.EXCLUDE_REPOS_FILE)

    def __load_repo_data(self) -> None:
        """repo data from json file"""
        json_file = Constants.REPO_DATA_FILE
        lines = self.__read_file(json_file.filename())
        if not lines:
            self.__logger.critical(Messages.NO_REPO_DATA)
        data = json.loads("".join(lines))
        self.__config_manager.set_config(json_file.config_key(), data)

    def __create_target_repos(self) -> None:
        """target repos and branches from template and include/exclude files"""
        repo_data = self.__config_manager.get_dict(
            Constants.REPO_DATA_FILE.config_key()
        )
        repo_dict = {
            repo[Constants.NAME_KEY]: {
                Constants.DEFAULT_BRANCH_KEY: (
                    repo[Constants.DEFAULT_BRANCH_KEY]
                    if Constants.DEFAULT_BRANCH_KEY in repo
                    else ""
                ),
                Constants.BRANCHES_KEY: repo[Constants.BRANCHES_KEY],
            }
            for repo in repo_data[Constants.VALUE_KEY]
        }

        target_repos = {}
        template = self.__config_manager.get_str(Constants.TEMPLATE_KEY)
        match template:
            case Messages.TEMPLATE_NONE:
                pass
            case Messages.TEMPLATE_DEFAULT:
                target_repos = {
                    name: {details[Constants.DEFAULT_BRANCH_KEY]}
                    for name, details in repo_dict.items()
                    if len(details[Constants.BRANCHES_KEY]) != 0
                }
            case Messages.TEMPLATE_ALL:
                target_repos = {
                    name: set(details[Constants.BRANCHES_KEY])
                    for name, details in repo_dict.items()
                }
            case _:
                self.__logger.critical(
                    Messages.UNKNOWN_TEMPLATE.format(template=template)
                )

        self.__add_included_repos(target_repos, repo_dict)
        self.__remove_excluded_repos(target_repos)

        self.__config_manager.set_config(Constants.TARGET_REPOS_KEY, target_repos)

    def __add_included_repos(
        self, target_repos: dict[str, set], repo_dict: dict[str, dict]
    ) -> None:
        included = self.__config_manager.get_dict(
            Constants.INCLUDE_REPOS_FILE.config_key()
        )

        for name, branches in included.items():
            if name not in repo_dict:
                self.__logger.error(Messages.BAD_REPO.format(repo=name))
                continue

            if name not in target_repos:
                target_repos[name] = set()

            default_branch = repo_dict[name][Constants.DEFAULT_BRANCH_KEY]
            all_branches = repo_dict[name][Constants.BRANCHES_KEY]

            if len(branches) == 0 and default_branch:
                target_repos[name].add(default_branch)
                self.__logger.info(
                    Messages.DEFAULT_BRANCH.format(branch=default_branch, repo=name)
                )
            elif Constants.WILDCARD in branches:
                target_repos[name].update(all_branches)
                self.__logger.info(Messages.ALL_BRANCHES.format(repo=name))
            else:
                for branch in branches:
                    if branch in all_branches:
                        target_repos[name].add(branch)
                        self.__logger.info(
                            Messages.ONE_BRANCH.format(branch=branch, repo=name)
                        )
                    else:
                        self.__logger.error(
                            Messages.BAD_BRANCH.format(branch=branch, repo=name)
                        )

    def __remove_excluded_repos(self, target_repos: dict[str, set]) -> None:
        excluded = self.__config_manager.get_dict(
            Constants.EXCLUDE_REPOS_FILE.config_key()
        )

        for name, branches in excluded.items():
            if name not in target_repos:
                self.__logger.info(Messages.REPO_EXCLUDED.format(repo=name))
                continue

            if len(branches) == 0 or Constants.WILDCARD in branches:
                target_repos.pop(name)
                self.__logger.info(Messages.EXCLUDING_ALL.format(repo=name))
            else:
                for branch in branches:
                    if branch in target_repos[name]:
                        target_repos[name].remove(branch)
                        self.__logger.info(
                            Messages.EXCLUDING_BRANCH.format(branch=branch, repo=name)
                        )
                    else:
                        self.__logger.info(
                            Messages.BRANCH_EXCLUDED.format(branch=branch, repo=name)
                        )

    def __create_repos(self, offline: bool) -> None:
        """create and store repo objects for target repos"""
        target_repos: dict[str, set] = self.__config_manager.get_dict(
            Constants.TARGET_REPOS_KEY
        )

        repos: list[ADORepository] = []
        for repo, branches in target_repos.items():
            if offline:
                repos.append(
                    ADORepository(
                        self.__logger,
                        repo,
                        branches,
                        os.path.join(Constants.REPOS_FOLDER, repo),
                    )
                )
                continue

            org = self.__config_manager.get_str(Constants.ORG_KEY)
            project = self.__config_manager.get_str(Constants.PROJECT_KEY)
            token = self.__config_manager.get_str(Constants.TOKEN_KEY)

            url = Constants.REPO_URL.format(
                token=token, org=org, project=project, name=repo
            )

            repos.append(
                ADORepository(
                    self.__logger,
                    repo,
                    branches,
                    os.path.join(Constants.REPOS_FOLDER, repo),
                    url,
                )
            )

        self.__config_manager.set_config(Constants.REPOS_KEY, repos)
