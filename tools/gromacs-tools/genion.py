#! /usr/bin/env python
# -*- coding: utf-8 -*-

# check_structures_gromacs.py <PDB path> <GROMACS programs path>
# Example: python check_structures_gromacs.py /home/faccioli/Execute/1VII/ \
#           /home/faccioli/Programs/gmx-4.6.5/no_mpi/bin/

import sys
import os
from subprocess import Popen, PIPE
import shutil
from datetime import datetime

from koala.utils.path import PathRuns

log_file_structures_not_accepted_by_genion = 'structures_not_accepted_by_genion.log'


# Log file of structures NOT accepted by pdb2gmx
def structure_not_accepted_by_genion(tprfile, stderr):
    # create directory where is saved all structures that were not accepted by pdb2gmx

    # write information about error at log file
    f_log = open(log_file_structures_not_accepted_by_genion, "a")
    outline = "STARTING LOG OF " + tprfile + "\n"
    f_log.write(outline)
    outline = stderr + "\n"
    f_log.write(outline)
    outline = "FINISHED LOG OF " + tprfile + "\n\n\n"
    f_log.write(outline)
    f_log.close()

    # write information about error at Galaxy interface
    arq = open(log_file_structures_not_accepted_by_genion)
    while True:
        line = arq.readline()
        if not line:
            break  # EOF
        else:
            sys.stderr.write(line)
            continue


def genion(gmx_path, gmx_version, concentration):
    if (gmx_version == "5.0.2"):
        program = os.path.join(gmx_path, "gmx")
        process = Popen([
            program,
            'genion',
            '-s',
            'tpr.tpr',
            '-o',
            'gro.gro',
            '-p',
            'top.top',
            '-pname',
            'NA',
            '-nname',
            'CL',
            '-pq',
            '1',
            '-nq',
            '-1',
            '-neutral',
            '-conc',
            concentration],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)

    else:
        program = os.path.join(gmx_path, "genion")
        process = Popen([
            program,
            '-s',
            'tpr.tpr',
            '-o',
            'gro.gro',
            '-p',
            'top.top',
            '-pname',
            'NA',
            '-nname',
            'CL',
            '-pq',
            '1',
            '-nq',
            '-1',
            '-neutral',
            '-conc',
            concentration],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate(input="SOL")

    # Checking output of genion of tprfile
    if stderr.find('Fatal error') >= 0:
        structure_not_accepted_by_genion('tpr.tpr', stderr)
        for raiz, diretorios, arquivos in os.walk(os.getcwd()):
            for arquivo in arquivos:
                if not arquivo.endswith(".log") and not arquivo.endswith(".tpr"):
                    os.remove(os.path.join(raiz, arquivo))
        return 0


def main():
    # Avoid GROMACS backup files
    os.environ["GMX_MAXBACKUP"] = "-1"

    path_runs = PathRuns()

    # define e acessa diretório padrão de execução
    diretorio = path_runs.get_path_execute()
    os.chdir(diretorio)

    # cria e acessa diretório temporário nomeado pela data completa atual sem espaços
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ', '_')
    os.makedirs(date)
    os.chdir(date)

    # copia parâmetro de entrada para a nova pasta temporária com o nome correto
    shutil.copy(sys.argv[1], "tpr.tpr")
    shutil.copy(sys.argv[2], "top.top")

    # define inputs
    concentration = sys.argv[3]

    gmx_path = path_runs.get_path_gromacs()
    gmx_version = path_runs.get_gromacs_version()

    # roda a funcao
    result = genion(
        gmx_path,
        gmx_version,
        concentration)

    # genion ok
    if (result != 0):

        # arquivos de saída
        gro = "gro.gro"
        top = "top.top"

        # cópia dos arquivos de saída para o dataset
        shutil.copy(gro, sys.argv[4])
        shutil.copy(top, sys.argv[5])

        # remove arquivos do diretório temporário
        for raiz, diretorios, arquivos in os.walk(os.getcwd()):
            for arquivo in arquivos:
                os.remove(os.path.join(raiz, arquivo))

        # remove diretório temporário
        os.chdir(diretorio)
        os.rmdir(date)

main()
