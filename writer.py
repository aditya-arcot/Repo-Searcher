"""contains ResultsWriter class"""

import os
from constants import BranchSearchResults, Constants
from config import ConfigurationManager


class ResultsWriter:
    """used for writing results files (details, matches, words)"""

    def __init__(self, date: str) -> None:
        config_folder = Constants.RESULTS_FOLDER
        path = os.path.join(config_folder, date)
        if not os.path.exists(path):
            os.makedirs(path)

        self.__details_file = os.path.join(path, Constants.DETAILS_FILE)
        self.__matches_file = os.path.join(path, Constants.MATCHES_FILE)
        self.__words_file = os.path.join(path, Constants.FOUND_FILE)

        self.__repo_counter = 0
        self.__words = set()

    def __write_line(self, filename, line="") -> None:
        with open(filename, "a", encoding=Constants.ENCODING) as file:
            file.write(line + Constants.NEWLINE)

    def __write_lines(self, filename, lines, prefix="") -> None:
        with open(filename, "a", encoding=Constants.ENCODING) as file:
            for line in lines:
                file.write(prefix + line + Constants.NEWLINE)

    def write_config(self, config: ConfigurationManager) -> None:
        """writes config info"""
        self.__write_lines(self.__details_file, config.config_str())
        self.__write_line(self.__details_file)

    def write_repo_start(self, name: str) -> None:
        """writes repo start section"""
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
