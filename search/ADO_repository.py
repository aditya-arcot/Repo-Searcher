import os
import time
import json
import requests
import git
from enum import Enum

from configuration_manager import ConfigurationManager
from constants import ConfigEnum, Constants
from logging_manager import LoggingManager

class GitCommandEnum(Enum):
    PULL, CLONE = range(2)

class ADORepository:
    branch_prefix = 'refs/heads/'
    git_branches_url = 'https://dev.azure.com/bp-vsts/NAGPCCR/_apis/git/repositories/' + \
                        '{id}/refs?filter=heads/&api-version=7.0'
    day_in_seconds = 86400
    max_git_attempts = 5

    def __init__(self,
                 logger:LoggingManager,
                 config:ConfigurationManager,
                 name:str,
                 url:str,
                 id:str,
                 path:str,
                 default_branch:str,
                 ) -> None:
        self.logger = logger
        self.config = config

        self.name = name
        self.url = url
        self.id = id
        self.path = path
        self.branches = self.__get_branches()

        if not self.is_empty():
            if self.branch_prefix not in default_branch:
                self.logger.warning(f'unexpected default branch format - {default_branch}')
            self.default_branch = default_branch.replace(self.branch_prefix, '')

    # https://learn.microsoft.com/en-us/rest/api/azure/devops/git/refs/list?view=azure-devops-rest-7.0
    def __get_branches(self):
        branches = []
        resp = requests.get(self.git_branches_url.format(id=self.id), \
                            auth=('user', self.config.get(ConfigEnum.PAT.name)),
                            timeout=10)
        if resp.status_code != 200:
            self.logger.critical(f'error requesting branches - {resp.status_code}')

        for i in json.loads(resp.text)['value']:
            branches.append(i['name'].replace(self.branch_prefix, ''))
        return branches

    def is_empty(self):
        return len(self.branches) == 0

    def update(self) -> bool:
        if self.is_empty():
            self.logger.info('no branches')
            return False

        if os.path.exists(self.path):
            self.logger.info('repo path already exists')

            last_update = self.config.get(ConfigEnum.LAST_UPDATE.name)

            if (self.name not in last_update) or \
                (time.time() - last_update[self.name] > self.day_in_seconds):
                return self.__update_helper(last_update, GitCommandEnum.PULL.name)

            self.logger.info('last update less than 1 day ago')
            return True

        self.logger.info('repo path does not exist')
        return self.__update_helper(last_update, GitCommandEnum.CLONE.name)

    def __update_helper(self, last_update, mode):
        attempts = 0

        while attempts < self.max_git_attempts:
            if self.__git_command_attempt(mode):
                last_update[self.name] = time.time()
                return True

            attempts += 1
            self.logger.info('trying again in 2s')
            time.sleep(2)

        self.logger.error(f'max retries for {mode}')
        return False

    def __git_command_attempt(self, mode):
        try:
            if mode == GitCommandEnum.PULL.name:
                git.Repo(self.path).git.pull()
            else:
                git.Repo.clone_from(self.url, self.path)
            self.logger.info(f'{mode} success')
            return True

        except git.GitCommandError as err:
            self.logger.error(f'{mode} failed - {err}')
            return False
