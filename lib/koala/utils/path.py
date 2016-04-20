#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import random
import os
import stat
import shutil
from koala.utils import show_error_message  # , get_logged_user

from koala.config import Configuration

# TODO: review exception rules
# TODO: fill some values from a new config file


class PathRuns(object):
    """docstring for PathRuns"""

    def __init__(self):
        super(PathRuns, self).__init__()

        self.config = Configuration()

        self.path_execute = self.config.get('path_execute', None)
        self.path_execution = ''

    def set_execution_directory(self, email=None):
        try:
            now = datetime.datetime.now()
            tupla = now.timetuple()
            rand = random.randint(0, 1000)

            try:
                if email is None:
                    nome_diretorio = str(tupla[2]) + str(tupla[1]) + str(tupla[0]) \
                        + "_" + str(tupla[3]) + str(tupla[4]) + str(tupla[5]) + "_" \
                        + str(rand) + "/"
                else:
                    nome_diretorio = email + str(tupla[2]) + str(tupla[1]) + str(tupla[0]) \
                        + "_" + str(tupla[3]) + str(tupla[4]) + str(tupla[5]) + "_" \
                        + str(rand) + "/"
                os.mkdir(os.path.join(self.get_path_execute(), nome_diretorio))
                os.chmod(os.path.join(self.get_path_execute(), nome_diretorio), stat.S_IRWXU)
            except Exception, e:
                show_error_message("Error when CreateExecutionDirectory\n%s" % e)

            self.path_execution = os.path.join(self.get_path_execute(), nome_diretorio)

        except Exception, e:
            show_error_message("Error when CreateExecutionDirectory\n%s" % e)

    def get_path_execution(self):
        return self.path_execution

    # def set_path_execute(self):
    #     try:
    #         self.path_execute = "/home/%s/execute/" % get_logged_user()
    #         # self.path_execute = "/dados/%s/execute/" % get_logged_user()
    #     except Exception, e:
    #         show_error_message("Error when getPathExecute\n%s" % e)

    def get_path_execute(self):
        return self.path_execute

    def get_path_algorithms(self, framework):
        try:
            # return "/home/%s/programs/%s/" % (get_logged_user(), framework)
            return self.config.get(framework.lower(), None)
        except Exception, e:
            show_error_message("Error when getPathAlgorithms\n%s" % e)

    def get_path_gromacs(self):
        # pathGromacs = '/home/%s/programs/gmx-4.6.5/no_mpi/bin/' \
        #                                 % get_logged_user()
        # return pathGromacs
        return self.config.get('path_gromacs', None)


def clear_path_execute(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            return True
        else:
            show_error_message("It is not a path:\n%s" % path)
            return False
    except Exception, e:
        show_error_message("Error when clearPathExecute:\n%s" % e)
