# -*- coding: utf-8 -*-

import os
from fabric.api import *
from fabric.contrib.files import upload_template, append, sed, exists, comment

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

# Configurações para o Cloud USP - Ribeirão

# IP Externo 200.144.255.35

# VM                 (22)     (80)
# docking01     2221    8084
# docking02     2227    8085
# docking03     2228    8086
# docking04     2229    8087
# docking05     2230    8088
# docking06     2231    8089
# docking07     2232    8090
# docking08     2233    8091
# docking09     2234    8092
# docking10     2235    8093
# docking11     2236    8094
# docking12     2224    8095

# IP SERVER
user = 'koala'
ip_server = "200.144.255.35"

#  LOCAL
# folder_local = '~/koala/'
galaxy_path = '~/galaxy/'
data_path = '/dados/koala/'

# GALAXY
galaxy_user = 'galaxyproject'
galaxy_project = 'galaxy'
galaxy_repository = 'git@github.com:%s/%s.git' % (galaxy_user, galaxy_project)

# PULSAR
pulsar_user = 'galaxyproject'
pulsar_project = 'pulsar'
pulsar_repository = 'git@github.com:%s/%s.git -b master' % (pulsar_user, pulsar_project)

# KOALA
koala_user = 'adefelicibus'
koala_project = 'koala-server'
koala_repository = 'git@github.com:%s/%s.git' % (koala_user, koala_project)

# koala server
username = 'koala'
port = 2221
port_http = 8084
koala_server = '%s@%s -p %s' % (username, ip_server, port)
env_path = '/home/%s/env/bin/activate' % username

# # pulsar server 1, docking03
# username = 'koala'
# port_http = 8086
# pulsar_server_1 = '%s@%s' % (username, ip_server)

# # pulsar server 2, docking04
# username = 'koala'
# port_http = 8087
# pulsar_server_2 = '%s@%s' % (username, ip_server)

# # pulsar server 3, docking05
# username = 'koala'
# port_http = 8088
# pulsar_server_3 = '%s@%s' % (username, ip_server)

# # pulsar server 4, docking06
# username = 'koala'
# port_http = 8089
# pulsar_server_4 = '%s@%s' % (username, ip_server)

# pulsar server 5, docking07
# username = 'koala'
# port_http = 8090
# pulsar_server_5 = '%s@%s' % (username, ip_server)

# # pulsar server 6, docking08
# username = 'koala'
# port_http = 8091
# pulsar_server_6 = '%s@%s' % (username, ip_server)

# # pulsar server 7, docking09
username = 'koala'
port_http = 8092
pulsar_server_7 = '%s@%s' % (username, ip_server)

# # pulsar server 8, docking10
# username = 'koala'
# port_http = 8093
# pulsar_server_8 = '%s@%s' % (username, ip_server)

# # pulsar server 9, docking11
# username = 'koala'
# port_http = 8094
# pulsar_server_9 = '%s@%s' % (username, ip_server)

# # pulsar server 10, docking12
# username = 'koala'
# port_http = 8095
# pulsar_server_10 = '%s@%s' % (username, ip_server)

# # pulsar server 11, docking2
# username = 'koala'
# port_http = 8085
# pulsar_server_11 = '%s@%s' % (username, ip_server)

# Configurações Locais
# tool_path = 'galaxy-dist/tools/protpred'
# static_path = 'galaxy-dist/static/'

# hosts
# env.hosts = ["myserver.net"]
# env.user = "koala"
env.key_filename = "/home/alexandre/.ssh/id_rsa"
# env.password = ""
env.port = 2234
env.hosts = [pulsar_server_7]
env.forward_agent = True

# -------------------------------
# SERVER
# -------------------------------

# ANTES DE QUALQUER COISA, CRIAR O USUARIO KOALA, COLOCAR COMO ROOT,
# LOGAR, CRIAR O SSH-KEYGEN, COPIAR
# SSH KEY DO COMPUTADOR LOCAL PARA O AUTHORIZED_KEYS NO SERVIDOR
# ssh-copy-id -i ~/.ssh/id_rsa.pub remote-host


def testserver():
    with cd('~/'):
        run('ls')


def reboot():
    """Reinicia o servidor"""
    sudo('reboot')


def locale_server():
    sudo('locale-gen --no-purge --lang pt_BR')


# update no servidor
def update_server():
    """Atualizando pacotes no servidor"""
    log('Atualizando pacotes')
    sudo('apt-get -y update')


# upgrade no servidor
def upgrade_server():
    """Updating programs"""
    log('Updating programs')
    sudo('apt-get -y upgrade')


def build_server():
    """Install all necessary packages"""
    log('Installing all necessary packages')
    sudo('apt-get -y install git')
    sudo('apt-get -y install python-dev')
    sudo('apt-get -y install python-pip')
    sudo('apt-get -y install zip')
    sudo('apt-get -y install python-virtualenv')
    sudo('apt-get -y install pymol')
    sudo('apt-get -y install postgresql postgresql-contrib')
    sudo('pip install virtualenvwrapper')
    sudo('apt-get -y install openmpi-bin openmpi-doc libopenmpi-dev')
    sudo('apt-get -y install automake')
    sudo('apt-get -y install nginx supervisor')
    sudo('apt-get -y install libcurl4-gnutls-dev')
    sudo('apt-get -y install libffi-dev')
    sudo('apt-get -y install python-numpy')
    # reboot()


def createDirectories_server(path=None):
    if(not exists('~/programs', use_sudo=True)):
        sudo('mkdir ~/programs')
    if(not exists('~/envs', use_sudo=True)):
        sudo('mkdir ~/envs')
    if(not exists('/dados/%s/execute' % user, use_sudo=True)):
        sudo('mkdir -p /dados/%s/execute' % user)

    sudo('chown %s:%s ~/envs' % (user, user))
    sudo('chown %s:%s ~/programs' % (user, user))
    sudo('chown -R %s:%s /dados/%s' % (user, user, user))


def installzlib_server():
    with cd('~/programs'):
        sudo('wget http://zlib.net/zlib-1.2.8.tar.gz')
        sudo('tar xzf zlib-1.2.8.tar.gz')
        with cd('zlib-1.2.8'):
            sudo('./configure')
            sudo('make')
            sudo('make install')
    with cd('~/programs'):
        sudo('rm zlib-1.2.8.tar.gz')
        # sudo('rm -r zlib-1.2.8')


def installFFTW_server():
    with cd('~/programs'):
        sudo('wget http://www.fftw.org/fftw-3.3.4.tar.gz')
        sudo('tar xzf fftw-3.3.4.tar.gz')
        with cd('fftw-3.3.4'):
            sudo('./configure --enable-float')
            sudo('make')
            sudo('make install')
    with cd('~/programs'):
        sudo('rm fftw-3.3.4.tar.gz')


def installGROMACS_server():
    with cd('~/programs'):
        sudo('wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-4.6.5.tar.gz')
        sudo('tar xzf gromacs-4.6.5.tar.gz')
        with cd('gromacs-4.6.5'):
            sudo('mkdir build')
            sudo('cd build/')
            sudo(
                'cmake /home/koala/programs/gromacs-4.6.5/ -DSHARED_LIBS_DEFAULT=OFF -DBUILD_SHARED_LIBS=OFF -DGMX_PREFER_STATIC_LIBS=YES '
                '-DGMX_BUILD_OWN_FFTW=OFF -DFFTW_LIBRARY=/usr/local/lib/libfftw3f.a '
                '-DFFTW_INCLUDE_DIR=/usr/local/include/ '
                '-DGMX_GSL=OFF -DGMX_DEFAULT_SUFFIX=ON -DGMX_GPU=OFF -DGMX_MPI=OFF -DGMX_DOUBLE=OFF '
                '-DGMX_INSTALL_PREFIX=/home/%s/programs/gmx-4.6.5/no_mpi/ '
                '-DCMAKE_INSTALL_PREFIX=/home/%s/programs/gmx-4.6.5/no_mpi/' % (user, user))
            sudo('make -j 8')
            sudo('make install')
    with cd('~/programs'):
        sudo('rm -r gromacs-4.6.5')
        sudo('rm gromacs-4.6.5.tar.gz')


# http://docs.fabfile.org/en/latest/api/contrib/files.html
def setVirtualenv_server():
    append(
        '~/.bashrc',
        ['export WORKON_HOME=~/envs',
            'source /usr/local/bin/virtualenvwrapper.sh'],
        use_sudo=True,
        )

    append(
        '~/.profile',
        ['export WORKON_HOME=~/envs',
            'source /usr/local/bin/virtualenvwrapper.sh'],
        use_sudo=True,
        )

    sudo('source ~/.bashrc')
    sudo('source ~/.profile')


def setPythonPath():
    append(
        '~/.bashrc',
        ['export PYTHONPATH=/usr/lib/python2.7/dist-packages:$PYTHONPATH',
            'export PYTHONPATH=/usr/lib/python2.7/dist-packages/pymol:$PYTHONPATH',
            'export PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH',
            'export PYTHONPATH=/usr/local/bin/pymol/modules:$PYTHONPATH',
            'export MPI_DIR=/lib/openmpi',
            'export PATH=/lib/openmpi/bin:$PATH',
            'export LD_LIBRARY_PATH=/lib/openmpi/lib:$LD_LIBRARY_PATH'],
        use_sudo=True,
        )
    sudo('source ~/.bashrc')


def installPyHighcharts_server():
    with cd('~/programs'):
        run('git clone git@github.com:%s/PyHighcharts.git' % koala_user)
        with cd('/usr/lib/python2.7/dist-packages'):
            sudo('ln -s /home/%s/programs/PyHighcharts/ PyHighcharts' % user)


def install2PGCartesian():
    path = '2pg_cartesian'
    with cd("~/programs"):
        run('git clone git@github.com:rodrigofaccioli/2pg_cartesian.git %s' % path)
        with cd('~/programs/%s' % path):
            run('mkdir build')
            with cd('build'):
                run('cmake ..')
                run('make')
                sudo('make install')


# def install2PGBuildConformation():
#     cd /usr/local/bin
#     sudo ln -s /home/koala/programs/2pg_build_conformation/src/protpred-Gromacs_pop_initial .


# def installMEAMT():
# cp ~/programs/meamt/aemt-mo-up2
# cp ~/programs/meamt/aemt-pop-up2
#     pass


# clone Koala
def cloneKoala_server():
    """ Criar novo projeto local """
    log('Criando novo projeto')

    run('git clone %s' % koala_repository)
    with cd('%s' % koala_project):
        run('mkvirtualenv %s' % koala_project)
        # run('pip install -r requirements.txt')  TODO: tem que inserir esse arquivo no projeto


def buildEnvKoala_server():  # tem que instalar na env do galaxy tbm
    sudo('workon %s' % koala_project)
    sudo('pip install -U distribute')
    sudo('pip install pycrypto')
    sudo('pip install natsort')
    sudo('pip install beautifulsoup4')
    sudo('pip install certifi')
    sudo('pip install pyopenssl ndg-httpsclient pyasn1')
    sudo('pip install pycurl')
    sudo('pip install fabric')


# clone Pulsar
def clonePulsar_server():
    """ Criar novo projeto local """
    log('Criando novo projeto')

    run('git clone %s' % pulsar_repository)
    with cd('%s' % pulsar_project):
        run('mkvirtualenv %s' % pulsar_project)
        sudo('pip install -r requirements.txt')


def buildEnvPulsar():
    run('workon %s' % pulsar_project)
    sudo('pip install -U distribute')
    sudo('pip install pycrypto')
    sudo('pip install natsort')
    sudo('pip install beautifulsoup4')
    sudo('pip install certifi')
    sudo('pip install pyopenssl ndg-httpsclient pyasn1')
    sudo('pip install pycurl')


def setKoalaLibLink_server():
    sudo(
        'ln -s /home/koala/koala-server/lib/koala/ /home/koala/envs/%s/lib/python2.7/site-packages/koala' % pulsar_project)


def setConfigNginx():
    write_file('%s/config/nginx_server.conf' % CURRENT_PATH, '/etc/nginx/nginx.conf', 'config')


def setSitePulsarNginx():
    # fabric.contrib.files.sed(filename, before, after, limit='', use_sudo=False, backup='.bak', flags='', shell=False)
    # sed('/etc/selinux/config',before='SELINUX=enforcing',after='SELINUX=permissive',use_sudo=True,backup='')
    write_file(
        '%s/config/site-koala' % CURRENT_PATH, '/etc/nginx/sites-available/site-koala', 'config')
    sed(
        '/etc/nginx/sites-available/site-koala',
        before='8000',
        after='%s' % port_http,
        use_sudo=True)
    sudo('ln -s /etc/nginx/sites-available/site-koala /etc/nginx/sites-enabled/site-koala')
    nginx_restart()


def setPulsarConfig():
    with cd('/home/%s/%s/' % (user, pulsar_project)):
        run('cp server.ini.sample server.ini')
    sed(
        '/home/koala/pulsar/server.ini',
        before='8913',
        # before='8000',
        after='%s' % port_http,
        use_sudo=True)
    comment(
        '/home/koala/pulsar/server.ini',
        regex='host = localhost',
        use_sudo=True)


def setPulsarApp():
    write_file('%s/config/app.yml' % CURRENT_PATH, '/home/koala/pulsar/', 'config')


def startPulsar():
    with cd('~/pulsar/'):
        run('paster serve server.ini --daemon')


def copyExecuteFiles():
    with cd('/dados/koala/'):
        run('cp -rR ~/%s/execute/ .' % koala_project)


def setLibOpenMPI():
    sudo('ln -s sudo ln -s /usr/lib/libmpi_cxx.so.0.0.1 /usr/lib/libmpi_cxx.so.1')
    sudo('ln -s /usr/lib/openmpi/lib/libmpi_cxx.so.0.0.1 /usr/lib/openmpi/lib/libmpi_cxx.so.1')
    sudo('ln -s /usr/lib/libmpi.so.0 /usr/lib/libmpi.so.1')
    sudo('ln -s /usr/lib/openmpi/lib/libmpi.so /usr/lib/openmpi/lib/libmpi.so.1')


def updateKoala():
    # atualizar o koala em todos os server
    pass


def newServerPulsar():
    """Configurar e instalar todos pacotes necessários para servidor"""
    log('Configurar e instalar todos pacotes necessários para servidor')

    locale_server()

    update_server()

    upgrade_server()

    build_server()

    createDirectories_server()

    installzlib_server()

    installFFTW_server()

    installGROMACS_server()

    setVirtualenv_server()

    setPythonPath()

    installPyHighcharts_server()

    install2PGCartesian()

    cloneKoala_server()

    # buildEnvKoala_server()

    clonePulsar_server()

    buildEnvPulsar()

    setKoalaLibLink_server()

    setConfigNginx()

    setSitePulsarNginx()

    setPulsarConfig()

    setPulsarApp()

    startPulsar()

    copyExecuteFiles()

    log('Reiniciando a máquina')
    reboot()

# -------------------------------
# GLOBAL METHODS
# -------------------------------


def nginx_restart():
    """Restart nginx no servidor"""
    log('restart nginx')
    sudo('/etc/init.d/nginx restart')


def write_file(filename, destination, path_template):

    upload_template(
            filename=filename,
            destination=destination,
            # template_dir=os.path.join(CURRENT_PATH, 'inc'),
            template_dir=os.path.join(CURRENT_PATH, path_template),
            context=env,
            # use_jinja=True,
            use_sudo=True,
            backup=True
        )


def upload_public_key():
    """Faz o upload da chave ssh para o servidor"""
    log('Adicionando chave publica no servidor')
    ssh_file = '~/.ssh/id_rsa.pub'
    target_path = '~/.ssh/uploaded_key.pub'
    put(ssh_file, target_path)
    run('echo `cat ~/.ssh/uploaded_key.pub` >> ~/.ssh/authorized_keys && rm -f ~/.ssh/uploaded_key.pub')


def login():
    local("ssh %s" % pulsar_server_1)


def log(message):
    print """
==============================================================
%s
==============================================================
    """ % message


# lixo
# # ----------------------------------------------------------------------------------------------------

# def server():
#     """inicia o servidor do Galaxy local"""
#     log('Iniciando servidor do Galaxy')
#     local('sh galaxy-dist/run.sh --reload')

# def update_tool_local(tool_name):
#     """Atualiza tool no diretório do Galaxy"""
#     log('Atualizando tool no diretorio do Galaxy')
#     if not os.path.exists(tool_path):
#         os.mkdir(tool_path)
#         warn("Criando o diretório raiz das tools")
#     if not os.path.exists(os.path.join(os.getcwd(), ''.join([tool_name, '.xml']))):
#         abort("Tool não encontrada.")
#     else:
#         local('cp %s.py %s.xml %s' % (tool_name, tool_name, tool_path))

# def update_tool_server(tool_name, server=''):
#     """Atualiza tool no diretório do Galaxy no servidor"""
#     log('Atualizando tool no diretorio do Galaxy no servidor')
#     if not os.path.exists(os.path.join(os.getcwd(), ''.join([tool_name, '.xml']))):
#         abort("Tool não encontrada.")
#     else:
#         local('scp %s.py %s.xml %s:%s' % (tool_name, tool_name, cloud_server, project_path))

# def update_all_tools_local():
#     pass

# def reinitialize_server(server=''):
#     '''Reinitile the remote server'''
#     log('Reinitilizing the remote server')
#     with settings(warn_only=True):
#         if run('screen -R -S "Galaxy" -p 0 -X exec sh %s/run.sh --reload' % galaxy_path).failed:
#             log('There is no screen availabe. \nYou must create a new screen.\nAfter that, type CTRL + A + D to deatached it')
#             if confirm("Do you want to create a new screen now? "):
#                 create_remote_screen()
#                 run('screen -R -S "Galaxy" -p 0 -X exec sh %s/run.sh --reload' % galaxy_path)
#             else:
#                 abort("There is no screen available");

# def create_remote_screen():
#     '''Create a new screen'''
#     log("Creating a new screen.")
#     run('screen -R -S "Galaxy"')

# def upload_public_key():
#     """faz o upload da chave ssh para o servidor"""
#     log('Adicionando chave publica no servidor')
#     ssh_file = '~/.ssh/id_rsa.pub'
#     target_path = '~/.ssh/uploaded_key.pub'
#     put(ssh_file, target_path)
#     run('echo `cat ~/.ssh/uploaded_key.pub` >> ~/.ssh/authorized_keys && rm -f ~/.ssh/uploaded_key.pub')

# def remote_pull():
#     """git pull remoto"""
#     log('Atualizando aplicação no servidor')
#     login()
#     with cd(project_path):
#         run('git pull origin master')