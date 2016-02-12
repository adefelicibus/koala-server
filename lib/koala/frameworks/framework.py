#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from koala.utils import path
from koala.utils import show_error_message

# TODO: review exception rules
# TODO: build a new get_configuration_file method


class Framework(object):
    """docstring for Framework"""

    def __init__(self, framework='2PG'):
        super(Framework, self).__init__()

        self.framework = framework
        self.pathExecution = ''
        self.command = ''
        self.program = ''

    def set_framework(self, framework):
        self.framework = framework

    def get_framework(self):
        return self.framework

    def get_configuration_file(self, filename):
        return '%s' % filename

    def set_command(self, algorithm):
        try:
            if self.get_framework() == '2PG':
                self.command = '/usr/local/bin/%s' % (algorithm)
            elif self.get_framework() in ('MEAMT', 'i-paes'):
                self.command = '%s%s' % (path.getPathAlgorithms(self.get_framework()), algorithm)
            else:
                self.command = '%s%s' % (path.getPathExecute(), algorithm)
        except Exception, e:
            show_error_message("Error when set_command\n%s" % e)

    def get_command(self):
        return self.command

    def get_program(self):
        return self.program

    def set_program(self, executable):
        self.program = executable

    def __execute_program(
            self,
            program,
            config,
            path_output,
            tool,
            email,
            galaxydir="None",
            outputID="None"):
        try:
            stdout_file = open("%sstdout.txt" % path.getPathExecution(), "wr")
            retProcess = None
            retProcess = subprocess.Popen([
                'nohup',
                program,
                self.getCommand(),
                config,
                path.getPathExecution(),
                galaxydir,
                path_output,
                outputID,
                tool,
                self.get_framework(),
                email,
                '&'],
                stdout=stdout_file, stderr=subprocess.STDOUT, shell=False)

            if retProcess is not None:
                pass

        except Exception, e:
            show_error_message("Error when _execute_program:\n%s" % e)
