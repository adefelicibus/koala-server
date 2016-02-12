#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import shutil
from koala.utils import show_error_message
from koala.frameworks import framework, params

# TODO: review exception rules


def copy_pdbs_from_input(
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
        show_error_message("Error when copyPDBsFromInput:\n%s" % e)


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
        show_error_message("Error when FormatFitness:\n%s" % e)


def create_local_pop_file(path, pop_file, framework):
    try:
        if(framework == '2PG'):
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
        show_error_message("Error when CreateLocalPopFile\n%s" % e)


def create_local_fasta_file(path, type_input, fasta_file, tool):
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
            if(params.get_parameter_value('force_field') == 'amber99sb-ildn'):
                linha = ''
                if type_input == '0':
                    header = "none:A|PDBID|CHAIN|SEQUENCE"+'\n'
                    linha = fasta_file  # neste caso é só a sequência, mas a variável é a mesma
                elif type_input == '1':
                    input_fasta = file(fasta_file, "r")
                    lines = input_fasta.readlines()
                    header = lines[0]
                    linha = lines[1]

                if(params.get_parameter_value('c_terminal_charge') == 'none' and
                        params.get_parameter_value('n_terminal_charge') == 'none'):
                    arq_fasta.write(header)
                    arq_fasta.write(linha)
                elif(params.get_parameter_value('c_terminal_charge') == 'ACE' and
                        params.get_parameter_value('n_terminal_charge') == 'none'):
                    arq_fasta.write('X')
                    arq_fasta.write(linha)
                else:
                    if(params.get_parameter_value('n_terminal_charge') == 'NME' and
                            params.get_parameter_value('c_terminal_charge') == 'none'):
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
        show_error_message("Error when CreateLocalFastaFile\n%s" % e)


def create_local_seq_file(path, type_input, seq_file, tool):
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
        show_error_message("Error when CreateLocalSeqFile\n%s" % e)


def create_configuration_file(path):
    try:
        if(framework.get_framework() == '2PG'):
            arq = file(path + 'configuration.conf', "wr")
            parameters = params.protpred_param.items()

            for par in parameters:
                arq.write("%s = %s\n" % (par[0], par[1]))

            arq.close()

        elif(framework.get_framework() == 'ProtPred-EDA'):
            arq = file(path + 'input.ini', "wr")

            parameters = params.protpred_eda_param.items()
            param_extra = []

            for i, par in enumerate(parameters):
                if((par[0].find("[")) != -1):
                    if(i == 0):
                        arq.write("%s\n" % par[0])
                    else:
                        arq.write("\n%s\n" % par[0])
                elif(not isinstance(par[1], basestring)):
                    arq.write("%s = %s\n" % (par[0], par[1][0]))
                else:
                    arq.write("%s = %s\n" % (par[0], par[1]))

            if(params.get_parameter_value("OptimMethod") == 'rw'):
                parameters = params.rw_param.items()
            elif(params.get_parameter_value("OptimMethod") == 'mcm'):
                parameters = params.mcm_param.items()
            elif(params.get_parameter_value("OptimMethod") == 'eda'):
                parameters = params.eda_param.items()
                if(params.get_parameter_value("SamplingMode", "eda") == 'fgm'):
                    param_extra = params.fgm_param.items()
            elif(params.get_parameter_value("OptimMethod") == 'rboa'):
                parameters = params.rboa_param.items()
            elif(params.get_parameter_value("OptimMethod") == 'ga'):
                parameters = params.ga_param.items()
            elif(params.get_parameter_value("OptimMethod") == 'de'):
                parameters = params.de_param.items()
            elif(params.get_parameter_value("OptimMethod") == 'ceda'):
                parameters = params.ceda_param.items()
                if(params.get_parameter_value("SamplingMode", "ceda") == 'fgm'):
                    param_extra = params.fgm_param.items()

            for i, par in enumerate(parameters):
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

        elif(framework.get_framework() == 'MEAMT'):
            arq = file(path + 'parameters.txt', "wr")
            parameters = params.meamt_param.items()

            for i, par in enumerate(parameters):
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
        show_error_message("Error when CreateConfigurationFile\n%s" % e)


def copy_files_to_execute_folder(path, prefix_filename=None):
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
                    if(prefix_filename):
                        new_filename = prefix_filename + '-' + file_name
                        dst = os.path.join(path, new_filename)
                    else:
                        dst = os.path.join(path, file_name)
                    shutil.copy(src, dst)
    except Exception, e:
        show_error_message("Error when copyFilesToExecuteFolder:\n%s" % e)
