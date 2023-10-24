""" contains results, writer classes """

import os
from typing import Union, Optional, Tuple, List
from configuration_manager import ConfigurationManager
from constants import (
    Constants,
    ConfigEnum,
    SearchTemplateModeEnum,
    SearchExcelModelEnum,
)
from logging_manager import LoggingManager


class BranchSearchResults:
    def __init__(self) -> None:
        self.matches = {}
        self.errors = []
        self.skipped_folders = []
        self.skipped_files = []
        self.folders = []
        self.files = []


class ResultsWriter:
    """
    used to write results files
    """

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

    def __write_line(self, file, line="") -> None:
        with open(file, "a", encoding="utf-8") as f:
            f.write(line + Constants.NEWLINE)

    def __write_lines(self, file, lines, prefix="") -> None:
        with open(file, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(prefix + line + Constants.NEWLINE)

    def write_config(
        self, config: ConfigurationManager, search_repos_branches: dict
    ) -> None:
        """writes info from configuration sections"""

        # not included - pat, last update

        log_str = self.__config_str("Log file", [self.logger.filename])

        included_repos_str = self.__config_str(
            "Included repos / branches", config.get_dict(ConfigEnum.INCLUDED_REPOS.name)
        )
        excluded_repos_str = self.__config_str(
            "Excluded repos / branches", config.get_dict(ConfigEnum.EXCLUDED_REPOS.name)
        )

        search_template_mode = SearchTemplateModeEnum(
            config.get_int(ConfigEnum.SEARCH_TEMPLATE_MODE.name)
        ).name
        search_template_mode_str = self.__config_str(
            "Search template mode", search_template_mode
        )

        search_repos_branches_str = self.__config_str(
            "Search repos / branches", search_repos_branches
        )

        search_words_str = self.__config_str(
            "Search words", config.get_list(ConfigEnum.SEARCH_WORDS.name)
        )

        excel_search_mode = SearchExcelModelEnum(
            config.get_int(ConfigEnum.EXCEL_SEARCH_MODE.name)
        ).name
        excel_search_mode_str = self.__config_str(
            "Excel search mode", excel_search_mode
        )

        excluded_files_str = self.__config_str(
            "Excluded files", config.get_list(ConfigEnum.EXCLUDED_FILES.name)
        )
        excluded_folders_str = self.__config_str(
            "Excluded folders", config.get_list(ConfigEnum.EXCLUDED_FOLDERS.name)
        )

        lines = [
            "Config",
            log_str,
            included_repos_str,
            excluded_repos_str,
            search_template_mode_str,
            search_repos_branches_str,
            search_words_str,
            excel_search_mode_str,
            excluded_files_str,
            excluded_folders_str,
        ]

        self.__write_lines(self.__details_file, lines)
        self.__write_line(self.__details_file)

    def __config_str(self, heading: str, config_item=None) -> str:
        """returns formatted string of config section"""
        if config_item is None:
            return Constants.TAB + heading

        if isinstance(config_item, list):
            spacing = Constants.NEWLINE + (Constants.TAB * 2)
            if len(config_item) == 0:
                return Constants.TAB + heading

            return Constants.TAB + heading + spacing + (spacing).join(config_item)

        elif isinstance(config_item, dict):
            if len(config_item) == 0:
                return Constants.TAB + heading

            out = [Constants.TAB + heading]
            double_tab = Constants.TAB * 2
            for key, val in config_item.items():
                out.append(double_tab + key + f" - {list(val)}")
            return Constants.NEWLINE.join(out)

        elif isinstance(config_item, str):
            return (
                Constants.TAB
                + heading
                + Constants.NEWLINE
                + (Constants.TAB * 2)
                + config_item
            )

        return ""

    def write_repo_start(self, name: str) -> None:
        """writes repo start section"""
        lines = []
        if self.__repo_counter == 0:
            lines.append("Search")
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
        self.__write_line(
            self.__details_file,
        )

    def write_branch_results(
        self, repo: str, branch: str, results: BranchSearchResults
    ) -> None:
        """writes all search results sections"""

        n, lines = self.__format_matches_section(results.matches)
        if lines:
            self.__write_lines(
                self.__matches_file, [repo, f"{Constants.TAB}{branch} ({n})"] + lines
            )

            lines.insert(0, f"{Constants.TAB}Matches ({n})")
            self.__write_lines(self.__details_file, lines, Constants.TAB * 2)

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

    def __format_results_section(self, name: str, section: list) -> Optional[list[str]]:
        if len(section) == 0:
            return

        spacer = Constants.TAB * 3
        lines = [f"{spacer}{name} ({len(section)})"]

        spacer += Constants.TAB
        for i in section:
            lines.append(spacer + i)
        return lines

    def __format_matches_section(
        self, branch_matches: dict
    ) -> Tuple[int, Optional[List[str]]]:
        count = 0

        if len(branch_matches) == 0:
            return count, None

        spacer = Constants.TAB * 2
        lines = []

        for path in branch_matches:
            lines.append(spacer + path)
            for search_word in branch_matches[path].keys():
                self.__words.add(search_word)
                lines.append((spacer + Constants.TAB) + search_word)
                for match in branch_matches[path][search_word]:
                    lines.append((spacer + (Constants.TAB * 2)) + match)
                    count += 1

        return count, lines

    def write_found_words(self) -> None:
        """writes list of words found in search"""
        self.__write_lines(self.__words_file, list(self.__words))
