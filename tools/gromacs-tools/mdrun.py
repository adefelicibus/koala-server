#! /usr/bin/env python
# -*- coding: utf-8 -*-

# check_structures_gromacs.py <PDB path> <GROMACS programs path>
# Example: python check_structures_gromacs.py /home/faccioli/Execute/1VII/ \
#         /home/faccioli/Programs/gmx-4.6.5/no_mpi/bin/

import sys
import os
from subprocess import Popen, PIPE
import shutil
from datetime import datetime

from koala.utils.path import PathRuns

log_file_structures_not_accepted_by_mdrun = 'structures_not_accepted_by_mdrun.log'


# Log file of structures NOT accepted by pdb2gmx
def structure_not_accepted_by_mdrun(tprfile, stderr):
    # create directory where is saved all structures that were not accepted by pdb2gmx

    # write information about error at log file
    f_log = open(log_file_structures_not_accepted_by_mdrun, "a")
    outline = "STARTING LOG OF " + tprfile + "\n"
    f_log.write(outline)
    outline = stderr + "\n"
    f_log.write(outline)
    outline = "FINISHED LOG OF " + tprfile + "\n\n\n"
    f_log.write(outline)
    f_log.close()

    # write information about error at Galaxy interface
    arq = open(log_file_structures_not_accepted_by_mdrun)
    while True:
        line = arq.readline()
        if not line:
            break  # EOF
        else:
            sys.stderr.write(line)
            continue


def mdrun(gmx_path, gmx_version, source_name):
    if (gmx_version == "5.0.2"):
        program = os.path.join(gmx_path, "gmx")
        process = Popen([
            program,
            'mdrun',
            '-s',
            source_name+'.tpr',
            '-v',
            '-deffnm',
            source_name],
            stdout=PIPE, stderr=PIPE)
    else:
        program = os.path.join(gmx_path, "mdrun")
        process = Popen([
            program,
            '-s',
            source_name+'.tpr',
            '-v',
            '-deffnm',
            source_name],
            stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    # Checking output of mdrun of tprfile
    if stderr.find('Fatal error') >= 0:
        structure_not_accepted_by_mdrun('tpr.tpr', stderr)
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
    shutil.copy(sys.argv[1], sys.argv[2]+".tpr")

    # define inputs
    source_name = sys.argv[2]

    gmx_path = path_runs.get_path_gromacs()
    gmx_version = path_runs.get_gromacs_version()

    # roda a funcao
    result = mdrun(
        gmx_path,
        gmx_version,
        source_name)

    # mdrun ok
    if (result != 0):

        # arquivos de saída
        gro = source_name+".gro"
        top = "top.top"
        edr = source_name+".edr"
        trr = source_name+".trr"
        log = source_name+".log"

        # cópia dos arquivos de saída para o dataset
        shutil.copy(gro, sys.argv[3])
        shutil.copy(top, sys.argv[4])
        shutil.copy(edr, sys.argv[5])
        shutil.copy(trr, sys.argv[6])
        shutil.copy(log, sys.argv[7])

        # remove arquivos do diretório temporário
        for raiz, diretorios, arquivos in os.walk(os.getcwd()):
            for arquivo in arquivos:
                os.remove(os.path.join(raiz, arquivo))

        # remove diretório temporário
        os.chdir(diretorio)
        os.rmdir(date)

main()
