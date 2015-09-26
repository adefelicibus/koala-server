#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import string
import shutil
import subprocess
import os
import stat
import smtplib
# import mimetypes
import re
import datetime
import zipfile
# import gzip
import fnmatch
from email.Utils import formatdate
from email import encoders
# from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass
import urllib2
from collections import OrderedDict,  Callable
import random


class DefaultOrderedDict(OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
           not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (
            self.default_factory, OrderedDict.__repr__(self))


class IcmcGalaxy(object):
    """docstring for IcmcGalaxy"""

    # parametersMEAMT = {
    #     'num_geracoes': '0',
    #     'tam_population': '450',
    #     'pop_vdw': '30',
    #     'pop_charge': '30',
    #     'pop_solv': '30',
    #     'pop_hbond': '30',
    #     'pop_nondom': '30',
    #     'pop_pond1': '30',
    #     'pop_pond2': '30',
    #     'pop_pond3': '30',
    #     'pop_pond4': '30',
    #     'pop_pond5': '30',
    #     'pop_pond6': '30',
    #     'pop_pond7': '30',
    #     'pop_pond8': '30',
    #     'pop_pond9': '30',
    #     'pop_pond10': '30',
    #     'unknown1': '0',
    #     'unknown2': '0',
    #     'vdw_w': '1',
    #     'charge_w': '0.5',
    #     'unknown3': '0',
    #     'unknown4': '0',
    #     'unknown5': '0',
    #     'unknown6': '0',
    #     'unknown7': '0',
    #     'solv_w': '0.5',
    #     'hbond_w': '0.5',
    #     'inputfasta': '1VII',
    #     'resultTxt': 'result_1vii.txt',
    #     'inputPop': 'pop_meamt.txt',
    #     'inputPDB': '1vii.pdb',
    #     'saida1': 'saida1.txt',
    #     'angles': 'angles.txt',
    #     'unknown8': '0',
    #     'meat': '1vii_meat.txt',
    # }

    general_parametersMEAMT = [
        ('num_geracoes', '0'),
        ('tam_population', '400'),
        ('pop_vdw', '25'),
        ('pop_charge', '25'),
        ('pop_solv', '25'),
        ('pop_hbond', '25'),
        ('pop_nondom', '25'),
        ('pop_pond1', '25'),
        ('pop_pond2', '25'),
        ('pop_pond3', '25'),
        ('pop_pond4', '25'),
        ('pop_pond5', '25'),
        ('pop_pond6', '25'),
        ('pop_pond7', '25'),
        ('pop_pond8', '25'),
        ('pop_pond9', '25'),
        ('pop_pond10', '25'),
        ('pop_pond11', '25'),
        ('unknown1', '0'),
        ('unknown2', '0'),
        ('vdw_w', '1'),
        ('charge_w', '0.5'),
        ('unknown3', '0'),
        ('unknown4', '0'),
        ('unknown5', '0'),
        ('unknown6', '0'),
        ('unknown7', '0'),
        ('solv_w', '0.5'),
        ('hbond_w', '0.5'),
        ('inputfasta', 'fasta.txt'),
        ('resultTxt', 'result_1vii.txt'),
        ('inputPop', 'pop_meamt.txt'),
        ('inputPDB', '1vii.pdb'),
        ('saida1', 'saida1.txt'),
        ('angles', 'angles.txt'),
        ('unknown8', '0'),
        ('meat', '1vii_meat.txt'),
    ]

    meamt_param = DefaultOrderedDict(list)
    for k, v in general_parametersMEAMT:
        meamt_param[k].append(v)

    general_parameters = {
        'gromacs_energy_min': 'ener_implicit',
        'NumberProcessor': '8',
        'NumberObjective': '1',
        'NumberGeration': '1',
        'SizePopulation': '1',
        'MonteCarloSteps': '50',
        'FrequencyMC': '5',
        'TemperatureMC': '370',
        'Fitness_Energy': 'Potential',
        'NativeProtein': '/home/faccioli/Execute/1VII_teste_1_1/1VII.pdb',
        'SequenceAminoAcidsPathFileName':
            '/home/faccioli/Execute/1VII_teste_1_1/1VII.fasta.txt',
        'NameExecutation': '1VII_teste_1',
        'Local_Execute': '/home/faccioli/Execute/1VII_teste_1_1/',
        'Database':
            '/home/faccioli/workspace/2pg_build_conformation/Database/',
        'rotamer_library': 'cad_tuffery',
        'top_file': 'top_protein.top',
        'IniPopFileName': 'pop_0.pdb',
        'Started_Generation': '-1',
        'z_matrix_fileName': 'z_matrix',
        'Path_Gromacs_Programs':
            '/home/faccioli/programs/gmx-4.6.5/no_mpi/bin/',
        'Computed_Energies_Gromacs_File':
            'file_energy_computed.ener.edr',
        'Energy_File_xvg': 'energy.xvg',
        'Computed_Areas_g_sas_File': 'file_g_sas_areas.xvg',
        'Computed_Energy_Value_File': 'energy_computed.xvg',
        'Computed_Radius_g_gyrate_File': 'file_g_gyrate_radius.xvg',
        'Computed_g_hbond_File': 'file_g_hbond.xvg',
        'How_Many_Rotation': '1',
        'min_angle_mutation_phi': '-10',
        'max_angle_mutation_phi': '10',
        'min_angle_mutation_psi': '-10',
        'max_angle_mutation_psi': '10',
        'min_angle_mutation_omega': '-10',
        'max_angle_mutation_omega': '10',
        'min_angle_mutation_side_chain': '-10',
        'max_angle_mutation_side_chain': '10',
        'apply_crossover': 'yes',
        'Individual_Mutation_Rate': '0.60',
        'mdp_file_min': 'energy_minimization_implicit.mdp',
        'mdp_file_name': 'compute_energy_implicit.mdp',
        'c_terminal_charge': 'none',
        'n_terminal_charge': 'none',
        'force_field': 'amber99sb-ildn',
        'objective_analisys': 'none',
        'objective_analisys_dimo_source':
            '/home/faccioli/workspace/dimo/DIMO2',
        'Program_Run_GreedyTreeGenerator2PG':
            '/2pg_cartesian/scripts/dimo/call_GreedyTreeGenerator2PG.sh',
        '1_point_cros_Rate': '0.80',
        'StepNumber': '100',
    }

    general_parameters_eda = [
                    ('[Config]', ''),
                    ('SaveOutput', 'yes'),
                    ('RandomSeed', '0'),
                    ('PrintDetails', 'no'),
                    ('RedirectToNull', 'no'),
                    ('RunMode', 'CreateRun'),
                    ('OptimMethod', 'eda'),
                    ('OutputFolder', 'out'),
                    ('Threshold', '0.0001'),
                    ('MaxEval', '1000000'),
                    ('Fitness', 'psp'),
                    ('SaveData', 'no'),
                    ('OverwriteData', 'no'),
                    ('PopFile', 'null'),
                    ('ExpsMode', 'no'),
                    ('SetsNumber', '4'),
                    ('[Optimization]', ''),
                    ('CellList', 'yes'),
                    ('CLOpenMP', 'no'),
                    ('SASAGPU', 'no'),
                    ('[FitnessPSP]', ''),
                    ('VanderWaals', '1.0'),
                    ('SASA', '0.0'),
                    ('Coulomb', '0.0'),
                    ('Solvatation', '0.0'),
                    ('HydrogenBond', '0.0'),
                    ('Torsion', '0.0'),
                    ('SequenceFile', 'fasta.txt'),
                    ('UseAngleDB', 'no'),
                    ('AminoAcidL', 'yes'),
                    ('SideChainMulti', 'no'),
                    ('SinglePDB', 'no'),
                    ('ChiDB', 'no'),
                    ]

    protpred_eda_param = DefaultOrderedDict(list)
    for k, v in general_parameters_eda:
        protpred_eda_param[k].append(v)

    l_rw_param = [
                ('[RandomWalk]', ''),
                ('PopSize', '500'),
                ]

    rw_param = DefaultOrderedDict(list)
    for k, v in l_rw_param:
        rw_param[k].append(v)

    l_mcm_param = [
                ('[MonteCarloMetropolis]', ''),
                ('PopSize', '5000'),
                ('Step', '0.02'),
                ('Boltzmann', '0.259'),
                ]

    mcm_param = DefaultOrderedDict(list)
    for k, v in l_mcm_param:
        mcm_param[k].append(v)

    l_ga_param = [
                ('[GeneticAlgorithm]', ''),
                ('PopSize', '3000'),
                ('OffSize', '3000'),
                ('CrossoverRate', '0.3'),
                ('MutationRate', '0.05'),
                ('MutationFactor', '0.1'),
                ('[SelectionConfig]', ''),
                ('SelSize', '5000'),
                ('SelMethod', 'tournament'),
                ('TouSize', '2'),
                ]

    ga_param = DefaultOrderedDict(list)
    for k, v in l_ga_param:
        ga_param[k].append(v)

    l_rboa_param = [
                    ('[rBOA]', ''),
                    ('PopSize', '5000'),
                    ('SelSize', '2500'),
                    ('MaxParents', '1'),
                    ('MixtureComponents', '2')
                    ]

    rboa_param = DefaultOrderedDict(list)
    for k, v in l_rboa_param:
        rboa_param[k].append(v)

    l_de_param = [
                ('[DE]', ''),
                ('PopSize', '3000'),
                ('OffSize', '3000'),
                ('CrossoverRate', '0.4'),
                ('FRate', '0.2'),
                ('[SelectionConfig]', ''),
                ('SelSize', '5000'),
                ('SelMethod', 'tournament'),
                ('TouSize', '2'),
                ]

    de_param = DefaultOrderedDict(list)
    for k, v in l_de_param:
        de_param[k].append(v)

    l_eda_param = [
                ('[EDA]', ''),
                ('PopSize', '500'),
                ('OffSize', '500'),
                ('SamplingMode', 'univariate'),
                ('Noise', '2'),
                ('Objective', 'mono'),
                ('Hierarchical', 'no'),
                ('[SelectionConfig]', ''),
                ('SelSize', '500'),
                ('SelMethod', 'tournament'),
                ('TouSize', '2'),
                ]

    eda_param = DefaultOrderedDict(list)
    for k, v in l_eda_param:
        eda_param[k].append(v)

    l_ceda_param = [
                ('[CEDA]', ''),
                ('MaxEval1', '500000'),
                ('MaxEval2', '500000'),
                ('Overlap', '0'),
                ('SamplingMode', 'univariate'),
                ('[SelectionConfig]', ''),
                ('SelSize', '5000'),
                ('SelMethod', 'tournament'),
                ('TouSize', '2'),
                ]

    ceda_param = DefaultOrderedDict(list)
    for k, v in l_ceda_param:
        ceda_param[k].append(v)

    l_fgm_param = [
                ('[FGM]', ''),
                ('MixtureComponents', '2'),
                ('Dimensionality', '2'),
                ('Threshold', '1.5'),
                ('Lambda', '0.9'),
                ('Partitions', '150'),
                ('FullMatrix', 'no'),
                ('GlobalSigma', 'no'),
                ('UseJointPDF', 'no'),
                ('[Hierarchical]', ''),
                ('ClusterMethod', 'euclidian'),
                ('AgglomerationM', 'complete'),
                ('CutTree', '2'),
                ('ClusteringType', 'dihedral'),
                ]

    fgm_param = DefaultOrderedDict(list)
    for k, v in l_fgm_param:
        fgm_param[k].append(v)

    pathExecution = ''
    command = ''
    program = ''
    framework = '2PG'  # 2PG(Default) or ProtPred-EDA or MEAMT
    pathGromacs = ''
    jobStart = ''
    jobEnd = ''

    def __init__(self):
        super(IcmcGalaxy, self).__init__()

    def getjobStart(self):
        return self.jobStart

    def setjobStart(self, jobStart):
        self.jobStart = jobStart

    def getjobEnd(self):
        return self.jobEnd

    def setjobEnd(self, jobEnd):
        self.jobEnd = jobEnd

    def calcTimeExecution(self, start, end):

        dif = end - start

        minutes = 0
        if (dif.seconds / 60) > 60:
            minutes = (dif.seconds / 60) - ((dif.seconds / 3600) * 60)
        else:
            minutes = dif.seconds / 60

        return [
            dif.seconds / 3600,
            minutes,
            dif.seconds - ((dif.seconds / 60) * 60)]

    def getPathGromacs(self):
        self.pathGromacs = '/home/%s/programs/gmx-4.6.5/no_mpi/bin/' \
                                        % self.getLoggedUser()
        return self.pathGromacs

    # def setPathGromacs(self, path):
    #   self.pathGromacs = pathGromacs

    def getParameters(self):
        return self.general_parameters

    def setFramework(self, framework):
        self.framework = framework

    def getFramework(self):
        return self.framework

    def setParameter(self, key, value):
        try:
            if(self.framework == '2PG'):
                if key in self.general_parameters:
                    self.general_parameters[key] = value
                else:
                    raise "There is no key %s in the parameters list. \
                                Please, use a valid key.\n" % key
            elif(self.framework == 'ProtPred-EDA'):
                if key in self.protpred_eda_param:
                    self.protpred_eda_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'rw'):
                    self.rw_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'mcm'):
                    self.mcm_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'eda'):
                    if key in self.eda_param:
                        self.eda_param[key] = value
                    elif self.\
                            getParameterValue("SamplingMode", "eda") == 'fgm':
                        if key in self.fgm_param:
                            self.fgm_param[key] = value
                        else:
                            raise "There is no key %s in the parameters list. \
                                    Please, use a valid key.\n" % key
                    else:
                        raise "There is no key %s in the parameters list. \
                                Please, use a valid key.\n" % key
                elif(self.getParameterValue("OptimMethod") == 'rboa'):
                    self.rboa_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'ga'):
                    self.ga_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'de'):
                    self.de_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'ceda'):
                    if key in self.ceda_param:
                        self.ceda_param[key] = value
                    elif self.\
                            getParameterValue("SamplingMode", "ceda") == 'fgm':
                        if key in self.fgm_param:
                            self.fgm_param[key] = value
                        else:
                            raise "There is no key %s in the parameters list [SamplingMode](%s)(%s). \
                                    Please, use a valid key.\n" % (
                                        key,
                                        self.getParameterValue("OptimMethod"),
                                        self.getParameterValue("SamplingMode"),
                                        )
                    else:
                        raise "There is no key %s in the parameters list[OptimMethod](%s)(%s). \
                                Please, use a valid key.\n" % (
                                    key,
                                    self.getParameterValue("OptimMethod"),
                                    self.getParameterValue("SamplingMode"),
                                    )
                else:
                    raise "There is no key %s in the parameters list. \
                            Please, use a valid key.\n" % key
            elif(self.framework == 'MEAMT'):
                if key in self.meamt_param:
                    self.meamt_param[key] = value
                else:
                    raise "There is no key %s in the parameters list. \
                                Please, use a valid key.\n" % key
            else:
                raise Exception("There is no defined framework.\n")
        except Exception, e:
            self.ShowErrorMessage("Error when setParameter\n%s" % e)
            # raise Exception("Error while setting parameter: \n%s" % e)

    def getParameterValue(self, key, optMethod=None):
        try:
            if(self.framework == '2PG'):
                if key in self.general_parameters:
                    return self.general_parameters[key]
            elif(self.framework == 'ProtPred-EDA'):
                if key in self.protpred_eda_param:
                    return self.protpred_eda_param[key]
                elif key in self.rw_param:
                    return self.rw_param[key]
                elif key in self.mcm_param:
                    return self.mcm_param[key]
                elif key in self.eda_param and optMethod == "eda":
                    return self.eda_param[key]
                elif key in self.fgm_param:
                    return self.fgm_param[key]
                elif key in self.ga_param:
                    return self.ga_param[key]
                elif key in self.rboa_param:
                    return self.rboa_param[key]
                elif key in self.de_param:
                    return self.de_param[key]
                elif key in self.ceda_param and optMethod == "ceda":
                    return self.ceda_param[key]
                else:
                    raise Exception(
                            "There is no key %s in the parameters list"
                            "Please, use a valid key.\n" % key)
            elif(self.framework == 'MEAMT'):
                if key in self.meamt_param:
                    return self.meamt_param[key]
            else:
                raise Exception("There is no defined framework.\n")
        except Exception, e:
            self.ShowErrorMessage("Error when getParameterValue\n%s" % e)
            # raise Exception("Error while getting parameter value: %s" % e)

    def getLoggedUser(self):
        try:
            return getpass.getuser()
        except Exception, e:
            self.ShowErrorMessage("Error when setCommand\n%s" % e)

    def getConfigurationFile(self, filename):
        # return '%s%s' % (self.getPathExecution(), filename)
        return '%s' % filename

    def setCommand(self, framework, algorithm):
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

    def getCommand(self):
        return self.command

    def getProgram(self):
        return self.program

    # fazer com que ele pegue o diretorio deste arquivo e una com o nome do programa
    def setProgram(self, executable):
        global program
        self.program = executable

    def getPathExecution(self):  # the directory where the execution will run
        return self.pathExecution

    def getPathExecute(self):  # the folder where all the execution folders run
        try:
            # return "/home/alexandre/execute/"
            return "/dados/%s/execute/" % self.getLoggedUser()
        except Exception, e:
            self.ShowErrorMessage("Error when getPathExecute\n%s" % e)

    def getPathAlgorithms(self, framework):
        try:
            return "/home/%s/programs/%s/" % (self.getLoggedUser(), framework)
        except Exception, e:
            self.ShowErrorMessage("Error when getPathAlgorithms\n%s" % e)

    def ValidateEmail(self, email):
        try:
            email = email.replace('__at__', '@')

            if not(re.match('(.+)@(.+)\.(.+)', email, re.IGNORECASE)):
                raise Exception("Invalid email address. Please, insert a valid email adress.")

            return email

        except Exception, e:
            self.ShowErrorMessage("Error when ValidateEmail\n%s" % e)

    def CreateExecutionDirectory(self, email=None):
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

    def CreateLocalPopFile(self, path, pop_file):
        try:
            if(self.framework == '2PG'):
                arq_pop = open(path + "pop_0.pdb", "wr")
                models = 0

                for line in file(pop_file, "r"):
                    arq_pop.write(line)
                    if line.startswith("MODEL"):
                        models += 1

                arq_pop.close()

                return models
            else:
                arq_pop = open(path + "pop_meamt.txt", "wr")
                ind = 0

                for line in file(pop_file, "r"):
                    arq_pop.write(line)
                    if line.startswith("##"):
                        ind += 1

                arq_pop.close()

                return ind

        except Exception, e:
            self.ShowErrorMessage("Error when CreateLocalPopFile\n%s" % e)
            # raise Exception("Error while creating the population file!\n%s" % e)

    def CreateLocalFastaFile(self, path, type_input, fasta_file, tool):
        try:
            arq_fasta = open(path + "fasta.txt", "wr")
            caption = ''
            sequence = ''

            if tool in ('2PG_Random_Tool', '2PG_NSGA2_Tool', '2PG_MC_Metropolis', '2PG_Mono_Tool'):
                if type_input == '0':
                    arq_fasta.write("none:A|PDBID|CHAIN|SEQUENCE"+'\n')
                    arq_fasta.write(fasta_file)
                    sequence = fasta_file
                    caption = 'none'
                elif type_input == '1':
                    for line in file(fasta_file, "r"):
                        if len(caption) == 0:
                            caption = line[1:5]
                        else:
                            sequence += line
                        arq_fasta.write(line)

            elif tool == '2PG_BuildConformation_Tool':
                if(self.getParameterValue('force_field') == 'amber99sb-ildn'):
                    linha = ''
                    if type_input == '0':
                        arq_fasta.write("none:A|PDBID|CHAIN|SEQUENCE"+'\n')
                        linha = fasta_file  # neste caso é só a sequência, mas a variável é a mesma
                    elif type_input == '1':
                        input_fasta = file(fasta_file, "r")
                        lines = input_fasta.readlines()
                        header = lines[0]
                        linha = lines[1]

                    if(self.getParameterValue('c_terminal_charge') == 'none' and
                            self.getParameterValue('n_terminal_charge') == 'none'):
                        arq_fasta.write(header)
                        arq_fasta.write(linha)
                    elif(self.getParameterValue('c_terminal_charge') == 'ACE' and
                            self.getParameterValue('n_terminal_charge') == 'none'):
                        arq_fasta.write('X')
                        arq_fasta.write(linha)
                    else:
                        if(self.getParameterValue('n_terminal_charge') == 'NME' and
                                self.getParameterValue('c_terminal_charge') == 'none'):
                            linha = string.replace(linha, '\n', 'X')
                            a = list(linha)
                            linha = ''.join(a)
                            arq_fasta.write(linha)
                            arq_fasta.write('\n')
                        else:
                            arq_fasta.write('X')
                            linha = string.replace(linha, '\n', 'X')
                            a = list(linha)
                            linha = ''.join(a)
                            arq_fasta.write(linha)
                            arq_fasta.write('\n')
                else:
                    for line in file(fasta_file, "r"):
                        arq_fasta.write(line)
            elif(tool == 'ProtPred_EDA'):
                if type_input == '0':
                    arq_fasta.write(fasta_file)
                    sequence = fasta_file
                    caption = 'none'
                elif type_input == '1':
                    for line in file(fasta_file, "r"):
                        if len(caption) == 0:
                            caption = line[1:5]
                        else:
                            arq_fasta.write(line.replace('\n', ''))
                            sequence += line
            elif(tool in ('MEAMT_BuildConformation_Tool', 'MEAMT_Tool')):
                residues = 0
                if type_input == '0':
                    residues = len(fasta_file.strip().replace("\n", ""))
                    arq_fasta.write(str(residues))
                    arq_fasta.write(fasta_file)
                    sequence = fasta_file
                    caption = 'none'
                elif type_input == '1':
                    for line in file(fasta_file, "r"):
                        if len(caption) == 0:
                            caption = line[1:5]
                        else:
                            line = line.strip().replace("\n", "")
                            sequence += line
                            residues += len(line)
                    arq_fasta.write(str(residues))
                    arq_fasta.write("\n")
                    arq_fasta.write(line)

            arq_fasta.close()

            return sequence

        except Exception, e:
            self.ShowErrorMessage("Error when CreateLocalFastaFile\n%s" % e)
            # raise Exception("Error while creating the local fasta file!\n%s" % e)

    def CreateLocalSeqFile(self, path, type_input, seq_file, tool):
        try:
            arq_fasta = open(path + "protein.seq", "wr")
            sequence = ''
            residues = 0

            if type_input == '0':  # verify
                residues = len(seq_file.strip().replace("\n", ""))
                arq_fasta.write(seq_file)
                sequence = seq_file
            elif type_input == '1':
                for line in file(seq_file, "r"):
                    residues += 1
                    sequence += line.split(" ")[0]  # three letter code
                    arq_fasta.write(line.strip().replace("\n", ""))
                    arq_fasta.write("\n")  # TODO: do not insert an empty line

            arq_fasta.close()

            return sequence, residues

        except Exception, e:
            self.ShowErrorMessage("Error when CreateLocalSeqFile\n%s" % e)

    def CreateConfigurationFile(self, path):
        try:
            if(self.framework == '2PG'):
                arq = file(path + 'configuration.conf', "wr")
                params = self.general_parameters.items()

                for par in params:
                    arq.write("%s = %s\n" % (par[0], par[1]))

                arq.close()

            elif(self.framework == 'ProtPred-EDA'):
                arq = file(path + 'input.ini', "wr")

                params = self.protpred_eda_param.items()
                param_extra = []

                for i, par in enumerate(params):
                    if((par[0].find("[")) != -1):
                        if(i == 0):
                            arq.write("%s\n" % par[0])
                        else:
                            arq.write("\n%s\n" % par[0])
                    elif(not isinstance(par[1], basestring)):
                        arq.write("%s = %s\n" % (par[0], par[1][0]))
                    else:
                        arq.write("%s = %s\n" % (par[0], par[1]))

                if(self.getParameterValue("OptimMethod") == 'rw'):
                    params = self.rw_param.items()
                elif(self.getParameterValue("OptimMethod") == 'mcm'):
                    params = self.mcm_param.items()
                elif(self.getParameterValue("OptimMethod") == 'eda'):
                    params = self.eda_param.items()
                    if(self.getParameterValue("SamplingMode", "eda") == 'fgm'):
                        param_extra = self.fgm_param.items()
                elif(self.getParameterValue("OptimMethod") == 'rboa'):
                    params = self.rboa_param.items()
                elif(self.getParameterValue("OptimMethod") == 'ga'):
                    params = self.ga_param.items()
                elif(self.getParameterValue("OptimMethod") == 'de'):
                    params = self.de_param.items()
                elif(self.getParameterValue("OptimMethod") == 'ceda'):
                    params = self.ceda_param.items()
                    if(self.getParameterValue("SamplingMode", "ceda") == 'fgm'):
                        param_extra = self.fgm_param.items()

                for i, par in enumerate(params):
                    if((par[0].find("[")) != -1):
                        if(i == 0):
                            arq.write("\n%s\n" % par[0])
                        else:
                            arq.write("\n%s\n" % par[0])
                    elif(not isinstance(par[1], basestring)):
                        arq.write("%s = %s\n" % (par[0], par[1][0]))
                    else:
                        arq.write("%s = %s\n" % (par[0], par[1]))

                if(len(param_extra) > 0):
                    for i, par in enumerate(param_extra):
                        if((par[0].find("[")) != -1):
                            if(i == 0):
                                arq.write("\n%s\n" % par[0])
                            else:
                                arq.write("\n%s\n" % par[0])
                        elif(not isinstance(par[1], basestring)):
                            arq.write("%s = %s\n" % (par[0], par[1][0]))
                        else:
                            arq.write("%s = %s\n" % (par[0], par[1]))

                    arq.close()

            elif(self.framework == 'MEAMT'):
                arq = file(path + 'parameters.txt', "wr")
                params = self.meamt_param.items()

                for i, par in enumerate(params):
                    if((par[0].find("[")) != -1):
                        if(i == 0):
                            arq.write("%s\n" % par[0])
                        else:
                            arq.write("\n%s\n" % par[0])
                    elif(not isinstance(par[1], basestring)):
                        arq.write("%s = %s\n" % (par[0], par[1][0]))
                    else:
                        arq.write("%s = %s\n" % (par[0], par[1]))

                arq.close()

        except Exception, e:
            self.ShowErrorMessage("Error when CreateConfigurationFile\n%s" % e)
            # raise Exception("Error while creating the configuration file!\n%s" % e)

    def getMessageEmail(self, tool_name):
        try:
            now = datetime.datetime.now()
            tupla = now.timetuple()
            data = str(tupla[2]) + '/' + str(tupla[1]) + '/' + str(tupla[0]) + ' ' + str(tupla[3]) + ':' + str(tupla[4]) + ':' + str(tupla[5])

            tool_name = tool_name.replace('_', ' ')

            messageEmail = '''Hi,

            Your simulation has been conclued at ''' + data + '''.

            You have to go to your History and download it.

            Best Regards.

            %s''' % tool_name

            return messageEmail

        except Exception, e:
            self.ShowErrorMessage("Error while getMessageEmail email!\n%s" % e)
            # raise Exception("Error while getMessageEmail email!\n%s" % e)

    def SendEmail(self, de, para, assunto, mensagem, arquivos, servidor):

        try:
            # Cria o objeto da mensagem
            msg = MIMEMultipart()
            # Define o cabeçalho
            msg['From'] = de
            msg['To'] = para
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = assunto

            # Atacha o texto da mensagem
            msg.attach(MIMEText(mensagem))

            # Atacha os arquivos
            for arquivo in arquivos:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(open(arquivo, 'rb').read())
                encoders.encode_base64(parte)
                parte.add_header(
                    'Content-Disposition', 'attachment; filename="%s"' % os.path.basename(arquivo)
                    )
                msg.attach(parte)

            # Conecta ao servidor SMTP
            smtp = smtplib.SMTP(servidor, 587)
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            # Faz login no servidor
            smtp.login('adefelicibus@gmail.com', 'mami1752@')
            try:
                # Envia o e-mail
                smtp.sendmail(de, para, msg.as_string())
            finally:
                # Desconecta do servidor
                smtp.close()
        except Exception, e:
            self.ShowErrorMessage("Error when SendEmail:\n%s" % e)
            # raise Exception("Error while sending email!\n%s" % e)

    def ShowErrorMessage(self, msg):
        error = sys.__stderr__
        error.write(msg)
        error.flush()
        sys.stderr = error
        sys.exit(1)
        # sys.stderr.write(msg)
        # sys.exit()

    def showMessage(self, msg):
        print msg

    def ShowWarningMessage(self, msg):
        info = sys.__stdout__
        info.write(msg)
        info.flush()
        sys.stdout = info

    def CopyNecessaryFiles(self, new_path):
        try:
            os.chdir(new_path)
            fileList = [os.path.normcase(f)
                        for f in os.listdir(self.getPathExecute())]
            fileList = [os.path.join(self.getPathExecute(), f)
                        for f in fileList]
            for arquivo in fileList:
                if not os.path.isdir(arquivo):
                    if(self.framework == 'MEAMT'):
                        shutil.copy(arquivo, new_path)
                    else:
                        if(os.path.splitext(arquivo.split('/')[-1])[1] != '.txt'):
                            shutil.copy(arquivo, new_path)
                else:
                    if not(re.search(r'\w+@\w+', arquivo)) and not(re.search(r'\d+_', arquivo)):
                        shutil.copytree(arquivo, os.path.join(new_path, arquivo.split('/')[-1]))
        except Exception, e:
            self.ShowErrorMessage("Error when CopyNecessaryFiles:\n%s" % e)
            # raise Exception("Error while copying the necessary files!\n%s" % e)

    def ExecuteProgram(
            self, program, config, path_execution, path_output,
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

    def getResultFiles(self, path, tool):
        try:
            resultFile = ''
            filesToHtml = []
            os.chdir(path)
            # if tool == '2PG_Random_Tool':
            #     resultFile = '%s%s' % (path, 'random_algorithm_solutions.pdb')
            if tool == '2PG_SortByFront_Tool':
                resultFile = '%s%s.zip' % (path, tool)
                z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
                listaArquivosFront = self.listDirectory(path, '*.front')
                for arq in listaArquivosFront:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosXvg = self.listDirectory(path, '*.xvg')
                for arq in listaArquivosXvg:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosPng = self.listDirectory(path, '*.png')
                for arq in listaArquivosPng:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosLog = self.listDirectory(path, '*.log')
                for arq in listaArquivosLog:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
            elif tool in (
                    'Dominance_Ranking', '2PG_SortMethodByFront_Tool',
                    'CalculateRMSD', 'CalculateTMScore', 'CalculateGDTTS'):
                resultFile = '%s%s.zip' % (path, tool)
                z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
                listaArquivosFront = self.listDirectory(path, '*.front')
                for arq in listaArquivosFront:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosXvg = self.listDirectory(path, '*.xvg')
                for arq in listaArquivosXvg:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosPdf = self.listDirectory(path, '*.pdf')
                for arq in listaArquivosPdf:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosPng = self.listDirectory(path, '*.png')
                for arq in listaArquivosPng:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosTxt = self.listDirectory(path, '*.txt')
                for arq in listaArquivosTxt:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosLog = self.listDirectory(path, '*.log')
                for arq in listaArquivosLog:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
            elif tool == '2PG_BuildConformation_Tool':
                resultFile = '%s%s' % (path, 'pop_0.pdb')
            elif tool in (
                    '2PG_NSGA2_Tool', '2PG_Mono_Tool',
                    '2PG_MC_Metropolis', '2PG_Random_Tool'):
                resultFile = '%s%s.zip' % (path, tool)
                z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
                listaArquivosPDB = self.listDirectory(path, '*.pdb')
                for arq in listaArquivosPDB:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosXvg = self.listDirectory(path, '*.xvg')
                for arq in listaArquivosXvg:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosFit = self.listDirectory(path, '*.fit')
                for arq in listaArquivosFit:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosPng = self.listDirectory(path, '*.png')
                for arq in listaArquivosPng:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                # listaArquivosPdb = self.listDirectory(path, 'PROT_IND_*.pdb')
                # for arq in listaArquivosPdb:
                #     z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                #     z.write(arq)
                #     z.close()
                #     filesToHtml.append(os.path.join(path, arq))
            # elif tool == '2PG_MC_Metropolis':
            #     os.chdir(path)
            #     resultFile = '%s%s' % (path, 'monte_carlo_solutions.pdb')
            # elif(tool == 'ProtPred_EDA'):
            #     resultFile = '%s%s' % (path, '/ProtPredEDA_out.zip')
            #     z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            #     self.copyFilesToExecuteFolder(path)
            #     listaArquivosPDB = self.listDirectory(path, '*.pdb')
            #     for arq in listaArquivosPDB:
            #         z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
            #         z.write(arq)
            #         z.close()
            # listadic = self.listDirectory(path)
            # self.zip_folder(listadic[0], resultFile)
            elif(tool == 'ProtPred_EDA'):
                resultFile = '%s%s.zip' % (path, tool)
                z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
                listaArquivosPDB = self.listDirectory(path, '*.pdb')
                for arq in listaArquivosPDB:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosPng = self.listDirectory(path, '*.png')
                for arq in listaArquivosPng:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
            elif tool == 'Download_From_Quark':
                resultFile = '%s%s' % (path, '/ResultQuark.zip')
                z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
                listaArquivosPDB = self.listDirectory(path, '*.pdb')
                for arq in listaArquivosPDB:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                listaArquivosTxt = self.listDirectory(path, '*.txt')
                for arq in listaArquivosTxt:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
            elif(tool == 'MEAMT_BuildConformation_Tool'):
                resultFile = '%s%s' % (path, 'pop_meamt.txt')
            elif(tool == 'MEAMT_Tool'):  # criar o html tbm, depois
                # resultFile = '%s%s' % (path, 'protein.pdb')
                resultFile = '%s%s.zip' % (path, tool)
                z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
                listaArquivosPDB = self.listDirectory(path, '*.pdb')
                for arq in listaArquivosPDB:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosPng = self.listDirectory(path, '*.png')
                for arq in listaArquivosPng:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
                listaArquivosTxt = self.listDirectory(path, 'subpop*.txt')
                for arq in listaArquivosTxt:
                    z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                    z.write(arq)
                    z.close()
                    filesToHtml.append(os.path.join(path, arq))
            return resultFile, filesToHtml
        except Exception, e:
            self.ShowErrorMessage("Error when getResultFiles:\n%s" % e)
            # raise Exception("Error while getting result files: \n%s" % e)

    def copyFilesToExecuteFolder(self, path):
        try:
            job_folder = os.path.join(path, 'out')
            contents = os.walk(job_folder)
            for root, folders, files in contents:
                for folder in folders:
                    pass
                for file_name in files:
                    name, ext = os.path.splitext(file_name)
                    if(ext == '.pdb'):
                        src = os.path.join(root, file_name)
                        dst = os.path.join(path, file_name)
                        shutil.copy(src, dst)
        except Exception, e:
            self.ShowErrorMessage("Error when copyFilesToExecuteFolder:\n%s" % e)

    def zip_folder(self, folder_path, output_path):
        """Zip the contents of an entire folder (with that folder included
        in the archive). Empty subfolders will be included in the archive
        as well.
        """
        parent_folder = os.path.dirname(folder_path)
        # Retrieve the paths of the folder contents.
        contents = os.walk(folder_path)
        try:
            zip_file = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
            for root, folders, files in contents:
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(parent_folder + '\\', '')
                    zip_file.write(absolute_path, relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path.replace(parent_folder + '\\', '')
                    zip_file.write(absolute_path, relative_path)
            zip_file.close()
        except Exception, e:
            self.ShowErrorMessage("Error when zipFolder:\n%s" % e)
            # raise Exception("Error while zipping folder: \n%s" % e)

    def listDirectory(self, directory, ereg=None):
        from natsort import natsorted
        try:
            # if self.framework == '2PG':
            fileList = [os.path.normcase(f)
                        for f in os.listdir(directory)]
            fileList = [os.path.normcase(f)
                        for f in fileList
                        if fnmatch.fnmatch(f, ereg)]
            # else:
            #     fileList = [os.path.normcase(f)
            #                 for f in os.listdir(directory)]
            #     fileList = [os.path.normcase(f)
            #                 for f in fileList
            #                 if os.path.isdir(f) and (re.search(r'out', f))]
            return natsorted(fileList)
        except Exception, e:
            self.ShowErrorMessage("Error when listDirectory:\n%s" % e)
            # raise Exception("Error while listing the directory.\n%s" % e)

    def sendOutputResults(self, path_output, file_output, file_result):
        try:
            dest = path_output + "/" + file_output
            copia = "cp " + file_result + " " + dest
            os.system(copia)
            # shutil.copy(arquivo, new_path)
        except Exception, e:
            self.ShowErrorMessage("Error when sendOutputResults:\n%s" % e)
            # raise Exception("Error while sending output files: \n%s" % e)

    def sendOutputFilesHtml(self, path, files):  # copia os arquivos listados em files para o path
        try:
            for f in files:
                shutil.copy(f, path)
        except Exception, e:
            self.ShowErrorMessage("Error when sendOutputFilesHtml:\n%s" % e)
            # raise Exception("Error: %s" % e)

    def format_fitness(self, fitness, tool=None):
        try:
            if(tool != 'Dominance_Ranking'):
                fe = string.split(fitness.rstrip(), ',')
                no_obj = len(fe)

                if fe[0] == 'None':
                    raise Exception("Please, use checkboxes to specify the objectives.\n")

                if int(no_obj) < 2:
                    raise Exception("Please, you must select more than 1 objective.\n")

                fit = ''
                for obj in fe:
                    fit += '%s, ' % obj
                fit = fit.strip(', ')

                return no_obj, fit
            else:
                comb = []  # fitness combination
                i = 0
                fe = fitness.split('#')
                for fit in range(len(fe)):
                    if len(fe[fit]) > 0:
                        fitn = fe[fit].strip().replace(str(i), '')
                        comb.append(fitn)
                        i = i + 1

                return comb
        except Exception, e:
            self.ShowErrorMessage("Error when FormatFitness:\n%s" % e)
            # raise Exception("Error: %s" % e)

# metodo para separar os modelos dentro de um PDB
    def parse_PDB(self, path, pdb_file, maxNumber=None, newName=None):
        try:
            pdb = file(pdb_file, 'r')
            path_f, name_f = os.path.split(pdb_file)
            name_f = name_f.split('.')[0]
            name_f = name_f.replace('_', '-')
            hearder = []
            new_pdbs = []
            for i, line in enumerate(open(pdb_file)):
                if len(new_pdbs) == maxNumber:
                    break
                if i < 3:  # mudar, um arquivo pdb pode ter mais de 3 linhas de header
                    hearder.append(line)
                if line.startswith("MODEL"):
                    l = line.split(" ")
                    if newName is None:
                        new_pdb = os.path.join(path, '%s-M%s.pdb' % (name_f, str(l[8].strip())))
                    else:
                        new_pdb = os.path.join(path, '%s-M%s.pdb' % (newName, str(l[8].strip())))

                    new_pdb_f = file(new_pdb, 'wr')

                    new_pdbs.append('%s-M%s.pdb' % (name_f, str(l[8].strip())))

                    if int(str(l[8].strip())) > 1:  # se o model for diferente de 1, coloca o header
                        for head in hearder:
                            new_pdb_f.write(head)

                    while not line.startswith("ENDMDL"):
                        line = pdb.readline()
                        new_pdb_f.write(line)

                    new_pdb_f.close()

            return new_pdbs

        except Exception, e:
            self.ShowErrorMessage("Error when parsePDB:\n%s" % e)
            # raise Exception("Error: %s" % e)

    def mergePDB(self, path, pdbs):
        try:
            if not pdbs:
                self.ShowErrorMessage("There is no PDB file to merge.")

            new_pdb = []
            header = []

            for idx, pdb_file in enumerate(pdbs):
                pdb = open(os.path.join(path, pdb_file), 'r')

                for line in pdb:
                    if idx == 0:  # primeiro arquivo, copia o cabeçalho
                        if not line.startswith("ATOM") and \
                            not line.startswith("MODEL") and \
                                not line.startswith("TER") and not line.startswith("ENDMDL"):
                            header.append(line)
                        elif not line.startswith("ATOM"):
                            continue
                        else:
                            new_pdb.append(line)
                    else:
                        if not line.startswith("ATOM"):
                            continue
                        else:
                            new_pdb.append(line)
                new_pdb.append("TER\n")
                new_pdb.append("ENDMDL\n")
                if (idx + 2) <= len(pdbs):
                    new_pdb.append("MODEL        %s\n" % (idx + 2))

            pdbf = os.path.join(path, 'MergedPDB.pdb')
            new_pdb_f = file(pdbf, 'wr')
            new_pdb_f.write(''.join(header))
            new_pdb_f.write(''.join('MODEL        1\n'))
            new_pdb_f.write(''.join(new_pdb))
            new_pdb_f.write('\n')
            new_pdb_f.close()

            return pdbf

        except Exception, e:
            self.ShowErrorMessage("Error when mergePDB:\n%s" % e)
            # raise Exception("Error: %s" % e)

    def sendMultipleOutputs(self, path, files, path_output, outputID):
        try:
            for pdb in files:
                # pdb_name = pdb.split(".")[0].split("_")[2]
                name, ext = os.path.splitext(pdb)
                ext = ext.replace('.', '')
                pdb_name = os.path.basename(pdb)
                new_name = "%s_%s_%s_%s_%s" % ('primary', outputID, pdb_name, 'visible', ext)
                f = os.path.join(path, pdb)
                dest = path_output + '/' + new_name
                copia = "cp " + f + " " + dest
                os.system(copia)
        except Exception, e:
            self.ShowErrorMessage("Error when sendMultipleOutputs:\n%s" % e)
            # raise Exception("Error sendMultipleOutputs: %s" % e)

    def openURL(self, url, path_output, file_name):
        """
        Download the file from `url` and save it locally under `file_name`
        """
        try:
            response = urllib2.urlopen(url)
            file_result = os.path.join(path_output, file_name)
            out_file = open(file_result, 'wb')
            out_file.write(response.read())
            out_file.close()
        except Exception, e:
            self.ShowErrorMessage("Error when openURL:\n%s" % e)

    def extractZipFile(self, zipFile, path):
        try:
            with zipfile.ZipFile(zipFile) as zip_file:
                for member in zip_file.namelist():
                    filename = os.path.basename(member)

                    # skip directories
                    if not filename:
                        continue

                    # copy file (taken from zipfile's extract)
                    source = zip_file.open(member)
                    target = file(os.path.join(path, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
        except Exception, e:
            self.ShowErrorMessage("Error when extractZipFile:\n%s" % e)
            # raise Exception("Error on extractZipFile: %s" % e)

    def extractGzFile(self, gzfile, path):
        try:
            shutil.copy(gzfile, path)

            subprocess.call(
                ["atool", '-q', '-X', path, os.path.join(path, os.path.basename(gzfile))])

            # TODO: Verificar se o arquivo tem folder e tratar

        except Exception, e:
            self.ShowErrorMessage("Error when extractGzFile:\n%s" % e)
            # raise Exception("Error on extractGzFile: %s" % e)

    def copyPDBsFromInput(
            self,
            path_execute,
            path_to,
            inputnames,
            inputPDBs):
        try:
            nomes_arquivos = []
            for n in inputnames.split(','):
                if len(n) > 0:
                    name, ext = os.path.splitext(n)
                    name = name.replace(' ', '-').replace('(', '').replace(')', '')
                    if ext.find('.pdb') < 0:
                        raise Exception('%s is not a PDB file' % name)
                    else:
                        if not ext.endswith('.pdb'):
                            extname = ext.replace(
                                '.pdb', '').strip().replace('(', '-').replace(')', '')
                            new_name = name + extname + '.pdb'
                            nomes_arquivos.append(new_name)

            arquivos = []
            arqs = inputPDBs.partition(',')
            arquivos.append(arqs[0])
            while(len(arqs[2]) > 0):
                arqs = arqs[2].partition(',')
                arquivos.append(arqs[0])

            for i, n in enumerate(nomes_arquivos):
                link_name = os.path.join(path_to, os.path.basename(n))
                if not os.path.exists(link_name):
                    os.symlink(arquivos[i], link_name)
                    os.system("cp %s %s" % (link_name, path_execute))
        except Exception, e:
            self.ShowErrorMessage("Error when copyPDBsFromInput:\n%s" % e)

    def clearPathExecute(self, path):
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

    def getFileSize(self, fpath, outpath):
        """
        format a nice file size string
        """
        try:
            size = ''
            fp = os.path.join(outpath, fpath)
            if os.path.isfile(fp):
                size = '0 B'
                n = float(os.path.getsize(fp))
                if n > 2**20:
                    size = '%1.1f MB' % (n/2**20)
                elif n > 2**10:
                    size = '%1.1f KB' % (n/2**10)
                elif n > 0:
                    size = '%d B' % (int(n))
            return size
        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error on getFileSize\n%s" % e)

    def compressFiles(self, files, path, toolname):
        # TODO: validar se files is a list
        try:
            os.chdir(path)
            resultFile = '%s%s.zip' % (path, toolname)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            for arq in files:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
            return True
        except Exception, e:
            self.ShowErrorMessage("Error when compressFiles:\n%s" % e)
