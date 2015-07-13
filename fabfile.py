# -*- coding: utf-8 -*-

from fabric.api import *
import os

# Configurações para o cluster LCR

username = 'adefelicibus'
prod_server = '%s@lcrserver.icmc.usp.br' % username
media_server = '%s@lcrserver.icmc.usp.br' % username
project_path = '/home/%s/project/' % username
env_path = '/home/%s/env/bin/activate' % username

# Configurações para o Cloud USP

username = 'galaxy'
port = 22048
cloud_server = '%s@200.144.255.42 -P %s' % (username, port)
project_path = '/home/%s/galaxy-dist/tools/protpred' % username
env_path = '/home/%s/env/bin/activate' % username
galaxy_path = '/home/%s/galaxy/galaxy-dist/'

# Configurações para o servidor da FCFRP

username = 'galaxy'
FCFRP_server = '%s@143.107.203.166' % username
#media_server = '%s@50.116.39.155' % username
project_path = '/home/%s/%s/tools/protpred' % (username, username)
env_path = '/home/%s/env/bin/activate' % username
galaxy_path = '/home/%s/galaxy/galaxy-dist/'
	
# Configurações Locais

tool_path = 'galaxy-dist/tools/protpred'
static_path = 'galaxy-dist/static/'

#env.hosts = [LCR_server]
#env.hosts = [FCFRP_server]
env.hosts = [cloud_server]

# ----------------------------------------------------------------------------------------------------

def server():
    """inicia o servidor do Galaxy local"""
    log('Iniciando servidor do Galaxy')
    local('sh galaxy-dist/run.sh --reload')

def update_tool_local(tool_name):
	"""Atualiza tool no diretório do Galaxy"""
	log('Atualizando tool no diretorio do Galaxy')
	if not os.path.exists(tool_path):
		os.mkdir(tool_path)
		warn("Criando o diretório raiz das tools")
	if not os.path.exists(os.path.join(os.getcwd(), ''.join([tool_name, '.xml']))):
		abort("Tool não encontrada.")
	else:
		local('cp %s.py %s.xml %s' % (tool_name, tool_name, tool_path))

def update_tool_server(tool_name, server=''):
	"""Atualiza tool no diretório do Galaxy no servidor"""
	log('Atualizando tool no diretorio do Galaxy no servidor')
	if not os.path.exists(os.path.join(os.getcwd(), ''.join([tool_name, '.xml']))):
		abort("Tool não encontrada.")
	else:
		local('scp %s.py %s.xml %s:%s' % (tool_name, tool_name, cloud_server, project_path))

def update_all_tools_local():
	pass

def reinitialize_server(server=''):
	'''Reinitile the remote server'''
	log('Reinitilizing the remote server')
	with settings(warn_only=True):
		if run('screen -R -S "Galaxy" -p 0 -X exec sh %s/run.sh --reload' % galaxy_path).failed:
			log('There is no screen availabe. \nYou must create a new screen.\nAfter that, type CTRL + A + D to deatached it')
			if confirm("Do you want to create a new screen now? "):
				create_remote_screen()
				run('screen -R -S "Galaxy" -p 0 -X exec sh %s/run.sh --reload' % galaxy_path)
			else:
				abort("There is no screen available");

def create_remote_screen():
	'''Create a new screen'''
	log("Creating a new screen.")
	run('screen -R -S "Galaxy"')

def upload_public_key():
    """faz o upload da chave ssh para o servidor"""
    log('Adicionando chave publica no servidor')
    ssh_file = '~/.ssh/id_rsa.pub'
    target_path = '~/.ssh/uploaded_key.pub'
    put(ssh_file, target_path)
    run('echo `cat ~/.ssh/uploaded_key.pub` >> ~/.ssh/authorized_keys && rm -f ~/.ssh/uploaded_key.pub')

def remote_pull():
    """git pull remoto"""
    log('Atualizando aplicação no servidor')
    login()
    with cd(project_path):
        run('git pull origin master')

def login():
    local("ssh %s" % prod_server)

def log(message):
    print """
==============================================================
%s
==============================================================
    """ % message
