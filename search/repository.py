''' contains related repository classes '''

import os
import time
import json
from enum import Enum
import requests
import git
from git.repo import Repo
from configuration_manager import ConfigurationManager
from constants import ConfigEnum
from logging_manager import LoggingManager

class GitCommandEnum(Enum):
    ''' enumerations for git commands '''
    PULL, CLONE = range(2)

# pylint: disable=too-many-instance-attributes, too-many-arguments
class ADORepository:
    ''' Azure DevOps repository class '''
    branch_prefix = 'refs/heads/'
    git_branches_url = 'https://dev.azure.com/bp-vsts/NAGPCCR/_apis/git/repositories/' + \
                        '{id}/refs?filter=heads/&api-version=7.0'
    day_in_seconds = 86400
    max_git_attempts = 5

    def __init__(self, logger:LoggingManager, config:ConfigurationManager, name:str,
                 url:str, _id:str, path:str, default_branch:str) -> None:
        self.logger = logger
        self.config = config

        # populate repo properties
        self.name = name
        self.url = url
        self.repo_id = _id
        self.path = path
        self.branches = self.__get_branches()

        # resolve default branch - usually master
        if not self.is_empty():
            if self.branch_prefix not in default_branch:
                self.logger.warning(f'unexpected default branch format - {default_branch}')
            self.default_branch = default_branch.replace(self.branch_prefix, '')

    def __get_branches(self) -> list:
        '''
        gets list of branches from ADO API request 
        see learn.microsoft.com/en-us/rest/api/azure/devops/git/?view=azure-devops-rest-7.0
        '''
        branches = []

        # username is arbitrary - PAT authentication
        resp = requests.get(self.git_branches_url.format(id=self.repo_id), \
                            auth=('user', self.config.get_str(ConfigEnum.PAT.name)),
                            timeout=10)

        if resp.status_code != 200:
            self.logger.critical(f'error requesting branches - {resp.status_code}')

        for i in json.loads(resp.text)['value']:
            branches.append(i['name'].replace(self.branch_prefix, ''))

        return branches

    def is_empty(self) -> bool:
        ''' checks if repository contains branches '''
        return len(self.branches) == 0

    def update(self) -> bool:
        ''' updates local repository files to match remote if necessary '''
        if self.is_empty():
            self.logger.info('no branches')
            return False

        last_update:dict = self.config.get_dict(ConfigEnum.LAST_UPDATE.name)

        if os.path.exists(self.path):
            self.logger.info('repo path already exists')

            # last update info unavailable or > 1 day since update
            if (self.name not in last_update) or \
                (time.time() - last_update[self.name] > self.day_in_seconds):
                return self.__update_helper(last_update, GitCommandEnum.PULL.name)

            self.logger.info('last update less than 1 day ago')
            return True

        self.logger.info('repo path does not exist')
        return self.__update_helper(last_update, GitCommandEnum.CLONE.name)

    def __update_helper(self, last_update:dict, mode:str) -> bool:
        ''' makes several attempts to either pull or clone repo '''
        attempts = 0

        while attempts < self.max_git_attempts:
            if self.__attempt_update(mode):
                # record update
                last_update[self.name] = time.time()
                return True

            attempts += 1
            self.logger.info('trying again in 2s')
            time.sleep(2)

        self.logger.error(f'max retries for {mode}')
        return False

    def __attempt_update(self, mode) -> bool:
        ''' makes an attempt to either pull or clone repo '''
        try:
            if mode == GitCommandEnum.PULL.name:
                repo = Repo(self.path)
                repo.head.reset(working_tree=True)
                repo.git.clean('-f', '-d')
                repo.git.pull()
            else:
                Repo.clone_from(self.url, self.path)
            self.logger.info(f'{mode} success')
            return True

        except git.GitCommandError as err:
            self.logger.error(f'{mode} failed - {err}')
            return False
