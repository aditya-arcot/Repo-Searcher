""" contains results writer and search results classes """

import os
from configuration_manager import ConfigurationManager
from constants import (
    Constants,
    ConfigEnum,
    SearchTemplateModeEnum,
)
from logging_manager import LoggingManager


# pylint: disable=too-few-public-methods
class BranchSearchResults:
    """holds results from repo branch search"""

    def __init__(self) -> None:
        self.matches = {}
        self.errors = []
        self.skipped_folders = []
        self.skipped_files = []
        self.folders = []
        self.files = []


class ResultsWriter:
    """used for writing results files (details, matches, words)"""

    def __init__(self, logger: LoggingManager, date: str, folder="results") -> None:
        self.logger = logger

        path = os.path.join(folder, date)
        if not os.path.exists(path):
            os.makedirs(path)

        self.__details_file = os.path.join(path, "details.txt")
        self.__matches_file = os.path.join(path, "matches.txt")
        self.__words_file = os.path.join(path, "words.txt")

        self.__repo_counter = 0
        self.__words = set()

    def __write_line(self, filename, line="") -> None:
        with open(filename, "a", encoding="utf-8") as file:
            file.write(line + Constants.NEWLINE)

    def __write_lines(self, filename, lines, prefix="") -> None:
        with open(filename, "a", encoding="utf-8") as file:
            for line in lines:
                file.write(prefix + line + Constants.NEWLINE)

    def __write_config_section(self, heading: str, config_item=None) -> None:
        lines = [Constants.TAB + heading]

        if isinstance(config_item, str):
            lines.append(Constants.TAB * 2 + config_item)

        elif isinstance(config_item, list):
            for item in config_item:
                lines.append(Constants.TAB * 2 + item)

        elif isinstance(config_item, dict):
            for key, val in config_item.items():
                lines.append(Constants.TAB * 2 + f"{key} - {list(val)}")

        self.__write_lines(self.__details_file, lines)

    def write_config(
        self, config: ConfigurationManager, search_repos_branches: dict
    ) -> None:
        """writes info from configuration sections except PAT, last branch updates"""

        self.__write_line(self.__details_file, "Config")

        self.__write_config_section("Log file", self.logger.filename)

        words = config.get_list(ConfigEnum.SEARCH_WORDS.name)
        self.__write_config_section("Search words", words)

        excluded_files = config.get_list(ConfigEnum.EXCLUDED_FILES.name)
        self.__write_config_section("Excluded files", excluded_files)
        excluded_folders = config.get_list(ConfigEnum.EXCLUDED_FOLDERS.name)
        self.__write_config_section("Excluded folders", excluded_folders)

        search_template_mode = SearchTemplateModeEnum(
            config.get_int(ConfigEnum.SEARCH_TEMPLATE_MODE.name)
        ).name
        self.__write_config_section("Search template mode", search_template_mode)

        included_repos_branches = config.get_dict(ConfigEnum.INCLUDED_REPOS.name)
        self.__write_config_section(
            "Included repos / branches", included_repos_branches
        )
        excluded_repos_branches = config.get_dict(ConfigEnum.EXCLUDED_REPOS.name)
        self.__write_config_section(
            "Excluded repos / branches", excluded_repos_branches
        )

        self.__write_config_section(
            "Final search repos / branches", search_repos_branches
        )

        self.__write_line(self.__details_file)

    def write_repo_start(self, name: str) -> None:
        """writes repo start section"""
        # include heading for first repo
        lines = ["Search"] if not self.__repo_counter else []
        lines.append(Constants.TAB + name)
        self.__repo_counter += 1
        self.__write_lines(self.__details_file, lines)

    def write_branch_start(self, name: str) -> None:
        """writes branch start section"""
        line = Constants.TAB * 2 + name
        self.__write_line(self.__details_file, line)

    def write_branch_skip(self, reason: str) -> None:
        """writes branch skip section"""
        line = Constants.TAB * 2 + f"skipped - {reason}"
        self.__write_line(self.__details_file, line)

    def write_branch_results(
        self, repo: str, branch: str, results: BranchSearchResults
    ) -> None:
        """writes all branch search results sections"""

        if len(results.matches) > 0:
            lines = []
            count = 0

            for path in results.matches:
                lines.append(path)
                for search_word in results.matches[path].keys():
                    self.__words.add(search_word)
                    lines.append(Constants.TAB + search_word)
                    for match in results.matches[path][search_word]:
                        lines.append(Constants.TAB * 2 + match)
                        count += 1

            if count:
                self.__write_line(self.__matches_file, repo)
                self.__write_line(
                    self.__matches_file, f"{Constants.TAB}{branch} ({count})"
                )
                self.__write_lines(self.__matches_file, lines, Constants.TAB * 2)

                self.__write_line(
                    self.__details_file, f"{Constants.TAB * 3}Matches ({count})"
                )
                self.__write_lines(self.__details_file, lines, Constants.TAB * 4)

        sections = {
            "Errors": results.errors,
            "Skipped folders": results.skipped_folders,
            "Skipped files": results.skipped_files,
            "Searched folders": results.folders,
            "Searched files": results.files,
        }

        for name, section in sections.items():
            lines = self.__format_results_section(name, section)
            if lines:
                self.__write_lines(self.__details_file, lines)

    def __format_results_section(self, name: str, section: list) -> list[str]:
        """formats branch search results section (other than matches) for output"""

        if len(section) == 0:
            return []

        spacer = Constants.TAB * 3
        lines = [f"{spacer}{name} ({len(section)})"]

        spacer += Constants.TAB
        for i in section:
            lines.append(spacer + i)
        return lines

    def write_found_words(self) -> None:
        """writes list of words found in search"""
        self.__write_lines(self.__words_file, list(self.__words))
