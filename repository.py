""" contains repository and git enumerations classes """

import os
import time
from enum import Enum
import git
from git.repo import Repo
from logging_manager import LoggingManager
from constants import Constants


class GitCommandEnum(Enum):
    """enumerations for git commands"""

    PULL, CLONE = range(2)


# pylint: disable=too-many-arguments, too-few-public-methods
class ADORepository:
    """Azure DevOps repository"""

    max_git_attempts = 5

    def __init__(
        self, logger: LoggingManager, name: str, branches: set[str], url: str, path: str
    ) -> None:
        self.logger = logger

        # populate repo properties
        self.name = name
        self.branches = branches
        self.url = url
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def update_branch(self, branch, last_update_dict: dict):
        """updates local branch files if necessary"""
        assert branch in self.branches

        if os.path.exists(os.path.join(self.path, branch)):
            self.logger.info("branch path exists")

            # info unavailable or >1 day since update
            if (
                self.name not in last_update_dict
                or branch not in last_update_dict[self.name]
                or time.time() - last_update_dict[self.name][branch]
                > Constants.DAY_IN_SECONDS
            ):
                self.logger.info("update required")
                return self.__update_helper(
                    branch, last_update_dict, GitCommandEnum.PULL.name
                )

            self.logger.info("updated less than 1 day ago")
            return True

        self.logger.info("branch path does not exist")
        return self.__update_helper(branch, last_update_dict, GitCommandEnum.CLONE.name)

    def __update_helper(self, branch: str, last_update: dict, mode: str) -> bool:
        """attempts to pull or clone a repo"""
        attempts = 0

        while attempts < self.max_git_attempts:
            if self.__attempt_update(branch, mode):
                # record update
                if self.name not in last_update:
                    last_update[self.name] = {}
                last_update[self.name][branch] = time.time()
                return True

            attempts += 1
            self.logger.info("trying again in 2s")
            time.sleep(2)

        self.logger.error(f"max retries for {mode}")
        return False

    def __attempt_update(self, branch, mode) -> bool:
        try:
            if mode == GitCommandEnum.PULL.name:
                repo = Repo(os.path.join(self.path, branch))
                repo.git.checkout(branch)
                # clear local changes / files
                repo.git.reset("--hard")
                repo.git.clean("-f", "-d", "-x")
                repo.remotes.origin.pull(branch)

            else:
                Repo.clone_from(
                    self.url, os.path.join(self.path, branch), branch=branch
                )

            self.logger.info(f"{mode} success")
            return True

        except git.GitCommandError as err:
            self.logger.error(f"{mode} failed - {err}")
            return False
