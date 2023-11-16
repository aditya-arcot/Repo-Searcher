"""contains ResultsWriter class"""

import os
from typing import Union
from constants import BranchSearchResults, Constants, Messages
from config import ConfigurationManager


class ResultsWriter:
    """used for writing results files (details, matches, words)"""

    def __init__(self, date: str) -> None:
        config_folder = Constants.RESULTS_FOLDER
        path = os.path.join(config_folder, date)
        if not os.path.exists(path):
            os.makedirs(path)

        self.__config_file = os.path.join(path, Constants.CONFIG_FILE)
        self.__details_file = os.path.join(path, Constants.DETAILS_FILE)
        self.__matches_file = os.path.join(path, Constants.MATCHES_FILE)
        self.__words_file = os.path.join(path, Constants.FOUND_FILE)

        self.__found_words = set()

    def write_repo_start(self, name: str) -> None:
        """writes repo start section"""
        self.__write_to_details_file(name)

    def write_branch_start(self, name: str) -> None:
        """writes branch start section"""
        line = Constants.TAB + name
        self.__write_to_details_file(line)

    def write_branch_skip(self, reason: str) -> None:
        """writes branch skip section"""
        line = Constants.TAB + f"skipped - {reason}"
        self.__write_to_details_file(line)

    def write_branch_results(
        self, repo: str, branch: str, results: BranchSearchResults
    ) -> None:
        """writes all branch search results sections"""

        lines, count = self.__format_matches(results.matches)
        if lines:
            self.__write_to_matches_file(repo)
            self.__write_to_matches_file(f"{Constants.TAB}{branch} ({count})")
            self.__write_to_matches_file(lines, Constants.TAB * 2)

            self.__write_to_details_file(
                f"{Constants.TAB * 2}{Messages.MATCHES} ({count})"
            )
            self.__write_to_details_file(lines, Constants.TAB * 3)

        sections = {
            Messages.ERRORS: results.errors,
            Messages.SKIPPED_FOLDERS: results.skipped_folders,
            Messages.SKIPPED_FILES: results.skipped_files,
            Messages.SEARCHED_FOLDERS: results.folders,
            Messages.SEARCHED_FILES: results.files,
        }

        for name, section in sections.items():
            lines = self.__format_results_section(name, section)
            if lines:
                self.__write_to_details_file(lines)

    def __format_matches(self, matches: dict) -> tuple:
        if len(matches) == 0:
            return [], -1

        count = 0
        lines = []
        for path in matches:
            lines.append(path)
            for word in matches[path].keys():
                self.__found_words.add(word)
                lines.append(Constants.TAB + word)
                for match in matches[path][word]:
                    lines.append(Constants.TAB * 2 + match)
                    count += 1

        if not count:
            return [], -1
        return lines, count

    def __format_results_section(self, name: str, section: list) -> list[str]:
        """formats branch search results section (other than matches) for output"""

        if len(section) == 0:
            return []

        spacer = Constants.TAB * 2
        lines = [f"{spacer}{name} ({len(section)})"]

        spacer += Constants.TAB
        for i in section:
            lines.append(spacer + i)
        return lines

    def write_config(self, config: ConfigurationManager) -> None:
        """writes config info"""
        self.__write_to_config_file(config.config_str())

    def write_found_words(self) -> None:
        """writes list of words found in search"""
        if self.__found_words:
            self.__write_to_words_file(list(self.__found_words))

    def __write_to_config_file(
        self, output: Union[str, list[str]], prefix: str = ""
    ) -> None:
        self.__write(self.__config_file, output, prefix)

    def __write_to_words_file(
        self, output: Union[str, list[str]], prefix: str = ""
    ) -> None:
        self.__write(self.__words_file, output, prefix)

    def __write_to_details_file(
        self, output: Union[str, list[str]], prefix: str = ""
    ) -> None:
        self.__write(self.__details_file, output, prefix)

    def __write_to_matches_file(
        self, output: Union[str, list[str]], prefix: str = ""
    ) -> None:
        self.__write(self.__matches_file, output, prefix)

    def __write(self, file: str, output: Union[str, list[str]], prefix: str) -> None:
        if isinstance(output, str):
            self.__write_line(file, output, prefix)
        else:
            self.__write_lines(file, output, prefix)

    def __write_line(self, filename, line, prefix) -> None:
        with open(filename, "a", encoding=Constants.ENCODING) as file:
            file.write(prefix + line + Constants.NEWLINE)

    def __write_lines(self, filename, lines, prefix) -> None:
        with open(filename, "a", encoding=Constants.ENCODING) as file:
            for line in lines:
                file.write(prefix + line + Constants.NEWLINE)
