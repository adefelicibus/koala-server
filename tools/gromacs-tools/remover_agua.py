#! /usr/bin/env python
# -*- coding: utf-8 -*-

# check_structures_gromacs.py <PDB path> <GROMACS programs path>
# Example: python check_structures_gromacs.py /home/faccioli/Execute/1VII/ \
#          /home/faccioli/Programs/gmx-4.6.5/no_mpi/bin/

import sys
import os
from subprocess import Popen, PIPE
import shutil
from datetime import datetime

from koala.utils.path import PathRuns

log_file_structures_not_accepted_by_remover_agua = 'structures_not_accepted_by_remover_agua.log'


# Log file of structures NOT accepted by pdb2gmx
def structure_not_accepted_by_remover_agua(grofile, stderr):
    # create directory where is saved all structures that were not accepted by pdb2gmx

    # write information about error at log file
    f_log = open(log_file_structures_not_accepted_by_remover_agua, "a")
    outline = "STARTING LOG OF " + grofile + "\n"
    f_log.write(outline)
    outline = stderr + "\n"
    f_log.write(outline)
    outline = "FINISHED LOG OF " + grofile + "\n\n\n"
    f_log.write(outline)
    f_log.close()

    # write information about error at Galaxy interface
    arq = open(log_file_structures_not_accepted_by_remover_agua)
    while True:
        line = arq.readline()
        if not line:
            break  # EOF
        else:
            sys.stderr.write(line)
            continue


def remover_agua(gmx_path, gmx_version, source_distance):
    if (gmx_version == "5.0.2"):
        program = os.path.join(gmx_path, "gmx")
        process = Popen([
            program,
            'select',
            '-f',
            'water.gro',
            '-s',
            'water.tpr',
            '-on',
            'remover.ndx',
            '-select',
            'not same residue as resname SOL and within ' + source_distance + ' of group Protein'],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        process2 = Popen([
            program,
            'trjconv',
            '-f',
            'water.gro',
            '-s',
            'water.tpr',
            '-n',
            'remover.ndx',
            '-o',
            'water_ok.gro'],
            stdout=PIPE, stderr=PIPE)
        stdout2, stderr2 = process2.communicate()
    else:
        program = os.path.join(gmx_path, "g_select")
        process = Popen([
            program,
            '-f',
            'water.gro',
            '-s',
            'water.tpr',
            '-on',
            'remover.ndx',
            '-select',
            'not same residue as resname SOL and within ' + source_distance + ' of group Protein'],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        program2 = os.path.join(gmx_path, "trjconv")
        process2 = Popen([
            program2,
            '-f',
            'water.gro',
            '-s',
            'water.tpr',
            '-n',
            'remover.ndx',
            '-o',
            'water_ok.gro'],
            stdout=PIPE, stderr=PIPE)
        stdout2, stderr2 = process2.communicate()

    # Até aqui as águas foram retiradas com sucesso no .gro,
    # mas é preciso atualizar a quantidade de águas da topologia. O bloco em bash abaixo faz isso:
    # top_temporary é top.top sem a última linha, que tem a quantidade de águas
    # os.system('head -n-1 top.top > top_temporary')
    arq_top = open("top.top", "rw")
    linhas = arq_top.readlines()
    arq_top.close()
    arq_top_temp = open("top_temporary.top", "w+")
    for line in linhas[:-1]:
        arq_top_temp.write(line)
    # conta o número de águas em water_ok.gro
    # os.system('total_aguas=$(grep SOL water_ok.gro | grep OW | wc -l | awk "{print $1}")')
    arq = open("water_ok.gro")
    cont = 0
    while True:
        line = arq.readline()
        if not line:
            break  # EOF
        else:
            if line.find("SOL") != -1 and line.find("OW") != -1:
                cont += 1
            else:
                continue
    arq.close()
    # Adiciona a última linha corrigida ao top_temporary
    # os.system('echo "SOL              ""$total_aguas" >> top_temporary')
    arq_top_temp.write("SOL              " + str(cont))
    arq_top_temp.close()
    # Troca top_temporary por top.top, que agora tem o número de águas atualizado
    # os.system('mv top_temporary top.top')
    shutil.copy("top_temporary.top", "top.top")

    # Checking output of remover_agua of grofile
    if stderr.find('Fatal error') >= 0:
        structure_not_accepted_by_remover_agua('water.gro', stderr)
        for raiz, diretorios, arquivos in os.walk(os.getcwd()):
            for arquivo in arquivos:
                if not arquivo.endswith(".log") and not arquivo.endswith(".gro"):
                    os.remove(os.path.join(raiz, arquivo))
        return 0
    if stderr2.find('Fatal error') >= 0:
        structure_not_accepted_by_remover_agua('water.gro', stderr2)
        for raiz, diretorios, arquivos in os.walk(os.getcwd()):
            for arquivo in arquivos:
                if not arquivo.endswith(".log") and not arquivo.endswith(".gro"):
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
    shutil.copy(sys.argv[1], "water.gro")
    shutil.copy(sys.argv[2], "water.tpr")
    shutil.copy(sys.argv[3], "top.top")

    # define inputs
    source_distance = sys.argv[4]

    gmx_path = path_runs.get_path_gromacs()
    gmx_version = path_runs.get_gromacs_version()

    # roda a funcao
    result = remover_agua(gmx_path, gmx_version, source_distance)

    # remover_agua ok
    if (result != 0):

        # arquivos de saída
        gro = "water_ok.gro"
        top = "top.top"

        # cópia dos arquivos de saída para o dataset
        shutil.copy(gro, sys.argv[5])
        shutil.copy(top, sys.argv[6])

        # remove arquivos do diretório temporário
        for raiz, diretorios, arquivos in os.walk(os.getcwd()):
            for arquivo in arquivos:
                os.remove(os.path.join(raiz, arquivo))

        # remove diretório temporário
        os.chdir(diretorio)
        os.rmdir(date)

main()
