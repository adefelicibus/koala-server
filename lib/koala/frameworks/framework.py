#!/usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess
# create a class to framework


def setFramework(framework):
        self.framework = framework


def getFramework():
    return self.framework


def getConfigurationFile(filename):
        # return '%s%s' % (self.getPathExecution(), filename)
        return '%s' % filename


def setCommand(framework, algorithm):
    try:
        global command
        if(self.framework == '2PG'):
            # self.command = '%ssrc/%s' % (
            self.command = '/usr/local/bin/%s' % (algorithm)
        # elif(self.framework == 'MEAMT'):
        #     self.command = '%s%s' % (self.getPathAlgorithms(framework), algorithm)
        elif(self.framework == 'i-paes'):
            self.command = '%s%s' % (self.getPathAlgorithms(framework), algorithm)
        else:
            self.command = '%s%s' % (self.getPathExecute(), algorithm)
    except Exception, e:
        self.ShowErrorMessage("Error when setCommand\n%s" % e)


def getCommand():
    return self.command


def getProgram():
    return self.program


# fazer com que ele pegue o diretorio deste arquivo e una com o nome do programa
def setProgram(executable):
    global program
    self.program = executable


def executeProgram(
            program, config, path_execution, path_output,
            tool, email, framework='2PG', galaxydir="None", outputID="None"):
        try:
            stdout_file = open("%sstdout.txt" % self.getPathExecution(), "wr")
            retProcess = None
            retProcess = subprocess.Popen([
                'nohup',
                program,
                self.getCommand(),
                config,
                path_execution,
                galaxydir,
                path_output,
                outputID,
                tool,
                framework,
                email,
                '&'],
                stdout=stdout_file, stderr=subprocess.STDOUT, shell=False)

            if retProcess is not None:
                pass

        except Exception, e:
            self.ShowErrorMessage("Error when ExecuteProgram:\n%s" % e)