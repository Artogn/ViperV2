# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

import os
import time

from viper.core.config import Config

class Project(object):
    def __init__(self):
        self.name = None
        self.path = None

        cfg = Config()
        if cfg.paths.root_path:
            self.root_path = cfg.paths.root_path
        else:
            self.root_path = os.getcwd()
            
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        
    def open(self, name):
        if name == 'default':
            path = self.root_path
        else:
            path = os.path.join(self.root_path, 'projects', name)
            if not os.path.exists(path):
                os.makedirs(path)

        self.name = name
        self.path = path

    def get_path(self):
        if self.path and os.path.exists(self.path):
            return self.path
        else:
            return self.root_path

    def list(self):
        projects_path = os.path.join(self.root_path, 'projects')
        if not os.path.exists(projects_path):
            return
        rows = []
        for project in os.listdir(projects_path):
            project_path = os.path.join(projects_path, project)
            rows.append({'name':project, 'created':time.ctime(os.path.getctime(project_path))})
        # Add Default
        rows.append({'name':'default', 'created':time.ctime(os.path.getctime(os.path.join(self.root_path, 'data')))})
        return rows

    def valid(self):
        if self.path and os.path.exists(self.path):
            return True

__project__ = Project()