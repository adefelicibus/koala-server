# -*- coding: utf-8 -*-

import data
import logging
from galaxy.datatypes.sniff import *
import commands
import os

log = logging.getLogger(__name__)

class GRO(data.Text):
    file_ext = 'gro'

    def sniff(self, filename):
        arq = open(filename)
        while True:
            line = arq.readline()
            if not line:
                break  # EOF
            else:
                #if str(line).find(' ') != 0:
                #    continue
                #else:                
                string_tratada = str(line)[0:len(line)-1].strip()
                if string_tratada.isdigit():
                    return True
                else:
                    continue
        return False

class TOP(data.Text):
    file_ext = 'top'

    def sniff(self, filename):
        arq = open(filename)
        text = "File 'top.top' was generated"
        while True:
            line = arq.readline()
            if not line:
                break  # EOF
            else:
                #if str(line).find(';') != 0:
                #    continue
                #else:                
                string_tratada = str(line)[0:len(line)-1].strip()                
                if string_tratada.find(text) != -1:
                   return True
                else:
                   continue
        return False

class ITP(data.Text):
    file_ext = 'itp'

    def sniff(self, filename):
        arq = open(filename)
        text = "[ position_restraints ]"
        while True:
            line = arq.readline()
            if not line:
                break  # EOF
            else:
                #if str(line).find(';') != 0:
                #    continue
                #else:                
                string_tratada = str(line)[0:len(line)-1].strip()                
                if string_tratada.find(text) != -1:
                    return True
                else:
                    continue
        return False

class MDP(data.Text):
    file_ext = 'mdp'

    def sniff(self, filename):
        arq = open(filename)
        test1 = False
        test2 = False
        text1 = "constraints"
        text2 = "integrator"
        while True:
            line = arq.readline()
            if not line:
                break  # EOF
            else:
                #if str(line).find(';') != 0:
                #    continue
                #else:                
                string_tratada = str(line)[0:len(line)-1].strip()
                if string_tratada.find(text1) != -1:
                    test1 = True           
                if string_tratada.find(text2) != -1:
                    test2 = True
                if (test1) and (test2):
                    return True                
                else:
                    continue
        return False

class TPR(data.Text):
    file_ext = 'tpr'

    def sniff(self, filename):
        fileName, fileExtension = os.path.splitext(filename)
        if fileExtension == ".tpr":
            return True                           
        return False

class EDR(data.Text):
    file_ext = 'edr'

    def sniff(self, filename):
        fileName, fileExtension = os.path.splitext(filename)
        if fileExtension == ".edr":
            return True                           
        return False

class TRR(data.Text):
    file_ext = 'trr'

    def sniff(self, filename):
        fileName, fileExtension = os.path.splitext(filename)
        if fileExtension == ".trr":
            return True                           
        return False

class LOG(data.Text):
    file_ext = 'log'

    def sniff(filename):
        fileName, fileExtension = os.path.splitext(filename)
        if fileExtension == ".log":
            arq = open(filename)
            test1 = False
            test2 = False
            text1 = "Log"
            text2 = "GROMACS"
            while True:
                line = arq.readline()
                if not line:
                    break  # EOF
                else:
                    #if str(line).find(';') != 0:
                    #    continue
                    #else:                
                    string_tratada = str(line)[0:len(line)-1].strip()
                    if string_tratada.find(text1) != -1:
                        test1 = True           
                    if string_tratada.find(text2) != -1:
                        test2 = True
                    if (test1) and (test2):
                        return True                
                    else:
                        continue
        return False