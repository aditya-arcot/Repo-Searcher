"""contains RepositorySearcher class"""

import os
import re
import time
from typing import Optional
from config import ConfigurationManager
from constants import BranchSearchResults, Constants, Messages
from logger import LoggingManager
from writer import ResultsWriter
from repository import ADORepository


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class RepositorySearcher:
    """used to search for specified text in repos"""
    def __init__(
        self, logger: LoggingManager, writer: ResultsWriter, config: ConfigurationManager
    ) -> None:
        self.__logger = logger
        self.__writer = writer
        self.__offline = config.get_bool(Constants.OFFLINE_KEY)
        self.__branch_updates = config.get_dict(
            Constants.BRANCH_UPDATES_FILE.config_key()
        )
        self.__words: list[str] = config.get_list(Constants.WORDS_FILE.config_key())
        self.__exclude_folders = config.get_list(
            Constants.EXCLUDE_FOLDERS_FILE.config_key()
        )
        self.__exclude_files = config.get_list(
            Constants.EXCLUDE_FILES_FILE.config_key()
        )
        self.__repos: list[ADORepository] = config.get_list(Constants.REPOS_KEY)

    def search(self) -> None:
        """search target repos and branches"""
        self.__logger.info(Messages.SEARCHING)

        for idx, repo in enumerate(self.__repos):
            self.__logger.info(
                Messages.SEARCHING_REPO.format(
                    name=repo.name, idx=idx + 1, total=len(self.__repos)
                )
            )
            self.__search_repo(repo)

    def __search_repo(self, repo: ADORepository) -> None:
        self.__writer.write_repo_start(repo.name)

        for idx, branch in enumerate(repo.branches):
            self.__logger.info(
                Messages.SEARCHING_BRANCH.format(
                    name=branch, idx=idx + 1, total=len(repo.branches)
                )
            )

            try:
                update_time = self.__branch_updates[repo.name][branch]
            except KeyError:
                update_time = Constants.DEFAULT_TIME

            if not self.__offline:
                if time.time() - update_time > Constants.SECONDS_IN_DAY:
                    # update
                    self.__logger.info(Messages.UPDATE_NEEDED)
                    result, timestamp = repo.update_branch(branch)

                    if result:
                        # populate timestamp
                        if repo.name not in self.__branch_updates:
                            self.__branch_updates[repo.name] = {}
                        self.__branch_updates[repo.name][branch] = timestamp

                    else:
                        # skip search
                        self.__skip_branch(Messages.UPDATE_FAILED)
                        continue

                else:
                    # skip update
                    self.__logger.info(Messages.UP_TO_DATE)

            elif update_time == -1:
                self.__skip_branch(Messages.NO_LOCAL)
                continue

            if not self.__words:
                self.__skip_branch(Messages.NO_SEARCH)
                continue

            results = self.__search_branch(branch, repo)
            if results:
                self.__writer.write_branch_results(repo.name, branch, results)

    def __skip_branch(self, msg: str) -> None:
        self.__logger.error(msg)
        self.__writer.write_branch_skip(msg)

    def __search_branch(
        self, branch: str, repo: ADORepository
    ) -> Optional[BranchSearchResults]:
        self.__writer.write_branch_start(branch)

        path = os.path.join(repo.path, branch)
        if not os.path.exists(path):
            self.__logger.error(Messages.BAD_PATH)
            return None

        results = BranchSearchResults()
        for root, dirs, files in os.walk(path):
            skip_dirs = [dir for dir in dirs if dir.lower() in self.__exclude_folders]
            skip_files = [
                file
                for file in files
                if file.lower().endswith(tuple(self.__exclude_files))
            ]

            results.skipped_folders += [
                os.path.join(root, dir) + os.sep for dir in skip_dirs
            ]
            results.skipped_files += [os.path.join(root, file) for file in skip_files]

            # prune search tree
            dirs[:] = [dir for dir in dirs if dir not in skip_dirs]
            files[:] = [file for file in files if file not in skip_files]

            results.folders += [os.path.join(root, dir) for dir in dirs]

            for file in files:
                file_path = os.path.join(root, file)
                self.__logger.info(Messages.FILE.format(path=file_path))
                self.__search_file(file_path, results)

        return results

    def __search_file(self, file_path: str, results: BranchSearchResults) -> None:
        result, lines = self.__read_file(file_path)
        if not result:
            results.errors.append(file_path)
        if not lines:
            return

        for word in self.__words:
            pattern = Constants.RE_PATTERN.format(word=word)
            for idx, line in enumerate(lines):
                if re.search(pattern, line):
                    if len(line) > Constants.MAX_PREVIEW_LENGTH:
                        line = Messages.LINE_TOO_LONG
                    formatted_line = Messages.LINE.format(idx=idx + 1, line=line)
                    self.__logger.info(
                        Messages.MATCH.format(word=word, line=formatted_line)
                    )

                    if not file_path in results.matches:
                        results.matches[file_path] = {}
                    if not word in results.matches[file_path]:
                        results.matches[file_path][word] = []
                    results.matches[file_path][word].append(formatted_line)

    def __read_file(self, path: str) -> tuple[bool, list[str]]:
        lines = []
        try:
            with open(path, "r", encoding=Constants.ENCODING, errors="ignore") as file:
                lines = [line.lower().strip() for line in file.readlines()]
        except FileNotFoundError:
            self.__logger.error(Messages.PATH_TOO_LONG.format(path=path))
            return (False, lines)
        except (UnicodeDecodeError, UnicodeError):
            self.__logger.error(Messages.DECODING_FAILED.format(path=path))
            return (False, lines)
        return (True, lines)
