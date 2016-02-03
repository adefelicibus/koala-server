#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import random
import os
import stat
import shutil


def CreateExecutionDirectory(email=None):
        try:
            now = datetime.datetime.now()
            tupla = now.timetuple()
            rand = random.randint(0, 1000)

            try:   # dia        #mes        #ano            #hora       #min        #seg
                if email is None:
                    nome_diretorio = str(tupla[2]) + str(tupla[1]) + str(tupla[0]) \
                        + "_" + str(tupla[3]) + str(tupla[4]) + str(tupla[5]) + "_" + str(rand) + "/"
                else:
                    nome_diretorio = email + str(tupla[2]) + str(tupla[1]) + str(tupla[0]) \
                        + "_" + str(tupla[3]) + str(tupla[4]) + str(tupla[5]) + "_" + str(rand) + "/"
                os.mkdir(os.path.join(self.getPathExecute(), nome_diretorio))
                os.chmod(os.path.join(self.getPathExecute(), nome_diretorio), stat.S_IRWXU)
            except Exception, e:
                self.ShowErrorMessage("Error when CreateExecutionDirectory\n%s" % e)
                # raise Exception("Error while creating the execution directory!\n%s" % e)

            self.pathExecution = nome_diretorio
            return nome_diretorio

        except Exception, e:
            self.ShowErrorMessage("Error when CreateExecutionDirectory\n%s" % e)


def getPathExecution():  # the directory where the execution will run
        return self.pathExecution


def getPathExecute():  # the folder where all the execution folders run
    try:
        # return "/home/alexandre/execute/"
        return "/dados/%s/execute/" % self.getLoggedUser()
    except Exception, e:
        self.ShowErrorMessage("Error when getPathExecute\n%s" % e)


def getPathAlgorithms(framework):
        try:
            return "/home/%s/programs/%s/" % (self.getLoggedUser(), framework)
        except Exception, e:
            self.ShowErrorMessage("Error when getPathAlgorithms\n%s" % e)


def clearPathExecute(path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                return True
            else:
                self.ShowErrorMessage("It is not a path:\n%s" % path)
                return False
        except Exception, e:
            self.ShowErrorMessage("Error when clearPathExecute:\n%s" % e)
            return False


def getPathGromacs():
        self.pathGromacs = '/home/%s/programs/gmx-4.6.5/no_mpi/bin/' \
                                        % self.getLoggedUser()
        return self.pathGromacs
