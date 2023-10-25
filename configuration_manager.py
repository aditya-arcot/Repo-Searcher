"""contains Config Manager class"""

import os
import re
import json
from logging_manager import LoggingManager
from constants import (
    Constants,
    ConfigEnum,
    SearchTemplateModeEnum,
)


class ConfigurationManager:
    """used to store and retrieve configuration info"""

    def __init__(self, logger: LoggingManager, input_folder: str = "input") -> None:
        self.logger = logger
        self.__input_folder = input_folder
        self.__str_info: dict[str, str] = {}
        self.__list_info: dict[str, list] = {}
        self.__dict_info: dict[str, dict] = {}
        self.__int_info: dict[str, int] = {}

    def __read_file(self, filename, lower=True, critical=False) -> list:
        """filters and strips lines from file"""
        path = os.path.join(self.__input_folder, filename)

        if not os.path.exists(path):
            error = f"{filename} does not exist"
            if critical:
                self.logger.critical(error)
            else:
                self.logger.warning(error)
                return []

        lines = []
        with open(path, "r", encoding="utf-8") as file:
            for line in file.readlines():
                line = line.strip()
                if lower:
                    line = line.lower()
                if (not line.startswith("#")) and (not line == ""):
                    lines.append(line)
        return lines

    def add_token(self) -> None:
        """Personal Access Token for ADO authentication"""
        pat_enum = ConfigEnum.PAT
        lines = self.__read_file(pat_enum.value, critical=True)

        try:
            pat = lines[0]
        except IndexError:  # empty line
            self.logger.critical("PAT is required for authentication")
            return

        self.__str_info[pat_enum.name] = pat

    def add_search_words(self) -> None:
        """repo search words"""
        search_words_enum = ConfigEnum.SEARCH_WORDS
        words = self.__read_file(search_words_enum.value)

        if len(words) == 0:
            self.logger.info(
                "no search words, program will be used to update local repos"
            )

        self.__list_info[search_words_enum.name] = [re.escape(word) for word in words]

    def add_excluded_files(self) -> None:
        """files excluded from search"""
        excluded_files_enum = ConfigEnum.EXCLUDED_FILES
        self.__list_info[excluded_files_enum.name] = self.__read_file(
            excluded_files_enum.value
        )

    def add_excluded_folders(self) -> None:
        """folders excluded from search"""
        excluded_folders_enum = ConfigEnum.EXCLUDED_FOLDERS
        self.__list_info[excluded_folders_enum.name] = self.__read_file(
            excluded_folders_enum.value
        )

    def add_last_updated_info(self) -> None:
        """last update timestamps for branches"""
        data = {}
        last_update_enum = ConfigEnum.LAST_UPDATE

        if os.path.exists(last_update_enum.value):
            with open(last_update_enum.value, "r", encoding="utf-8") as json_file:
                data = json_file.read()

            try:
                data = json.loads(data)
            except json.decoder.JSONDecodeError:
                self.logger.error("last update file is not formatted properly")
                data = {}

        self.__dict_info[last_update_enum.name] = data

    def __add_repos(self, config_enum: ConfigEnum) -> None:
        """repo and branch names"""
        repos = {}
        lines = self.__read_file(config_enum.value, lower=False)

        for line in lines:
            split = line.split()
            name = split[0]
            branches = set(split[1:])  # empty set if no branches specified

            if name not in repos:
                repos[name] = set()
            # preserve previously inputted branches
            repos[name] = repos[name] | branches

        self.__dict_info[config_enum.name] = repos

    def add_included_repos(self) -> None:
        """repos and branches included in search"""
        self.__add_repos(ConfigEnum.INCLUDED_REPOS)

    def add_excluded_repos(self) -> None:
        """repos and branches excluded from search"""
        self.__add_repos(ConfigEnum.EXCLUDED_REPOS)

    def __get_input(self, options: list) -> int:
        """gets user choice from options"""
        for pos, option in enumerate(options):
            print(f" - {pos} - {option}")

        while True:
            try:
                choice = int(input("enter a valid integer: "))
                if choice in range(len(options)):
                    return choice
            except KeyboardInterrupt:
                self.logger.critical("keyboard interrupt")
            except ValueError:
                print("invalid, please try again")

    def add_repo_search_template_mode(self) -> None:
        """sets repo/branch template for search"""
        print("Select a repository search template for initialization")
        print("Further configuration can be done using Include/Exclude files")
        repo_mode = self.__get_input(["None", "All"])

        if repo_mode == 1:
            print("Select a branch search template for initialization")
            print("Further configuration can be done using Include/Exclude files")
            branch_mode = self.__get_input(["Default", "All"])
            search_mode_enum_value = SearchTemplateModeEnum(branch_mode).value + 1
        else:
            # no need to ask for branch mode
            search_mode_enum_value = SearchTemplateModeEnum.NO_REPOS_NO_BRANCHES.value

        self.__int_info[ConfigEnum.SEARCH_TEMPLATE_MODE.name] = search_mode_enum_value
        self.logger.info(
            f"repo search template mode - {SearchTemplateModeEnum(search_mode_enum_value).name}"
        )

    def __get_error(self, label: str, _type: str) -> None:
        """reports error finding config info"""
        self.logger.error(f"{label} not present in {_type} info")

    def get_str(self, label: str) -> str:
        """returns config string with specified label"""
        if label in self.__str_info:
            return self.__str_info[label]
        self.__get_error(label, "str")
        return ""

    def get_dict(self, label: str) -> dict:
        """returns config dict with specified label"""
        if label in self.__dict_info:
            return self.__dict_info[label]
        self.__get_error(label, "dict")
        return {}

    def get_list(self, label: str) -> list:
        """returns config list with specified label"""
        if label in self.__list_info:
            return self.__list_info[label]
        self.__get_error(label, "list")
        return []

    def get_int(self, label: str) -> int:
        """returns config int with specified label"""
        if label in self.__int_info:
            return self.__int_info[label]
        self.__get_error(label, "int")
        return -1

    def __repr__(self) -> str:
        return (
            self.__repr_helper(self.__str_info)
            + self.__repr_helper(self.__dict_info)
            + self.__repr_helper(self.__list_info)
            + self.__repr_helper(self.__int_info)
        )

    def __repr_helper(self, pairs: dict) -> str:
        out = ""
        for key, value in pairs.items():
            out += key + Constants.NEWLINE
            out += repr(value) + Constants.NEWLINE
            out += Constants.NEWLINE
        return out
