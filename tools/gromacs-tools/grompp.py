#! /usr/bin/env python
# -*- coding: utf-8 -*-

# check_structures_gromacs.py <PDB path> <GROMACS programs path>
# Example: python check_structures_gromacs.py /home/faccioli/Execute/1VII/ /home/faccioli/Programs/gmx-4.6.5/no_mpi/bin/

import sys
import os
from subprocess import Popen, PIPE, STDOUT
import shutil
from datetime import datetime
import getpass

# obtem usuario logado no linux
user = getpass.getuser()

def get_gromacs_version():
	if os.path.exists("/home/"+user+"/programs/gmx-5.0.2/"):
		gromacs_version = "5.0.2"
	else:
		gromacs_version = "4.6.5"
	return gromacs_version

#Log file of structures NOT accepted by pdb2gmx
log_file_structures_not_accepted_by_grompp='structures_not_accepted_by_grompp.log'
def structure_not_accepted_by_grompp(grofile, stderr):
	#create directory where is saved all structures that were not accepted by pdb2gmx
	# directory = os.path.join(os.getcwd(),'no_accepted_by_pdb2gmx')
	# if not os.path.exists(directory):
	#	os.makedirs(directory)
	# moves structure that was not accepted by pdb2gmx
	# shutil.move(grofile, directory)

	#write information about error at log file
	f_log = open(log_file_structures_not_accepted_by_grompp,"a")
	outline = "STARTING LOG OF " + grofile + "\n"
	f_log.write(outline)
	outline = stderr + "\n"
	f_log.write(outline)
	outline = "FINISHED LOG OF " + grofile + "\n\n\n"	
	f_log.write(outline)	
	f_log.close()

	#write information about error at Galaxy interface
	arq = open(log_file_structures_not_accepted_by_grompp)
	while True:
		line = arq.readline()
		if not line:
			break  # EOF
		else:
			sys.stderr.write(line)
        	continue

def grompp():
	if (get_gromacs_version() == "5.0.2"):
		gmx_path = "/home/"+user+"/programs/gmx-5.0.2/no_mpi/bin/"
		program = os.path.join(gmx_path, "gmx")
		process = Popen([program, 'grompp', '-f', 'mdp.mdp', '-c', 'gro.gro', '-p', 'top.top', '-o', 'tpr.tpr'], stdout=PIPE, stderr=PIPE)
	else:
		gmx_path = "/home/"+user+"/programs/gmx-4.6.5/no_mpi/bin/"
		program = os.path.join(gmx_path, "grompp")
		process = Popen([program, '-f', 'mdp.mdp', '-c', 'gro.gro', '-p', 'top.top', '-o', 'tpr.tpr'], stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	#Checking output of grompp of grofile
	if stderr.find('Fatal error') >= 0:		
		structure_not_accepted_by_grompp('gro.gro', stderr)
		for raiz, diretorios, arquivos in os.walk(os.getcwd()):
			for arquivo in arquivos:
				if not arquivo.endswith(".log") and not arquivo.endswith(".gro"):
					os.remove(os.path.join(raiz,arquivo))
		return 0

def main():
	#Avoid GROMACS backup files
	os.environ["GMX_MAXBACKUP"]="-1"

	# define e acessa diretório padrão de execução
	diretorio = "/home/"+user+"/execute/"
	os.chdir(diretorio)

	# cria e acessa diretório temporário nomeado pela data completa atual sem espaços
	date = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ', '_')
	os.makedirs(date)
	os.chdir(date)

	# copia parâmetro de entrada para a nova pasta temporária com o nome correto
	shutil.copy(sys.argv[1], "mdp.mdp")
	shutil.copy(sys.argv[2], "gro.gro")
	shutil.copy(sys.argv[3], "top.top")

	# roda a funcao
	result = grompp()

	# grompp ok
	if (result != 0):

		# arquivos de saída
		tpr = "tpr.tpr"

		# cópia dos arquivos de saída para o dataset
		shutil.copy(tpr, sys.argv[4])

		# remove arquivos do diretório temporário
		for raiz, diretorios, arquivos in os.walk(os.getcwd()):
			for arquivo in arquivos:
				os.remove(os.path.join(raiz,arquivo))

		# remove diretório temporário
		os.chdir(diretorio)
		os.rmdir(date)

main()