"""contains ADORepository class"""

import os
import time
from typing import Union
import git
from git.repo import Repo
from logger import LoggingManager
from constants import Messages, Constants


# pylint: disable=too-many-arguments, too-few-public-methods
class ADORepository:
    """Azure DevOps repository"""

    def __init__(
        self,
        logger: LoggingManager,
        name: str,
        branches: set[str],
        path: str,
        url: Union[str, None] = None,
    ) -> None:
        self.logger = logger

        self.name = name
        self.branches = branches
        self.path = path
        self.url = url
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def __str__(self) -> str:
        return Messages.STR.format(
            repo=self.name, path=self.path, branches=self.branches
        )

    def __repr__(self) -> str:
        return self.__str__()

    def update_branch(self, branch) -> tuple[bool, float]:
        """updates local branch files if necessary"""
        assert branch in self.branches

        if os.path.exists(os.path.join(self.path, branch)):
            self.logger.info(Messages.PATH_EXISTS)
            mode = Messages.PULL
        else:
            self.logger.info(Messages.PATH_DOESNT_EXIST)
            mode = Messages.CLONE

        for _ in range(Constants.RETRIES):
            if self.__update_helper(branch, mode):
                return (True, time.time())

            self.logger.info(Messages.RETRYING)
            time.sleep(Messages.INTERVAL)

        self.logger.error(Messages.GIT_MAX_RETRIES.format(mode=mode))
        return (False, Constants.DEFAULT_TIME)

    def __update_helper(self, branch, mode) -> bool:
        try:
            if mode == Messages.PULL:
                repo = Repo(os.path.join(self.path, branch))
                repo.git.checkout(branch)
                # clear local changes / files
                repo.git.reset("--hard")
                repo.git.clean("-f", "-d", "-x")
                repo.remotes.origin.pull(branch)
            else:
                if self.url is None:
                    self.logger.error(Messages.URL_NOT_SPECIFIED)
                    return False
                Repo.clone_from(
                    self.url, os.path.join(self.path, branch), branch=branch
                )

            self.logger.info(Messages.GIT_SUCCESS.format(mode=mode))
            return True

        except git.GitCommandError as err:
            self.logger.error(Messages.GIT_FAILURE.format(mode=mode, err=err))
            return False
