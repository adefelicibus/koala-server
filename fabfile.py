# -*- coding: utf-8 -*-

import os
from fabric.api import *
from fabric.contrib.files import upload_template, append, sed, exists, comment
import getpass

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

LOGGED_USER = getpass.getuser()

# USER THAT WILL EXECUTE THE KOALA SERVER
user = 'koala'

# Settings to Postgres Database
bd = 'koaladb'
user_db = 'koala'
passwd_db = 'koala'

# IP SERVER
ip_server = "0.0.0.0"

#  LOCAL PATH
folder_local = '/home/%s/koala/' % user
galaxy_path = '/home/%s/koala/galaxy/' % user
data_path = '/home/%s/koala/dados/' % user

#  SERVER PATH
folder_local = '/home/%s/koala/' % user
galaxy_path = '/home/%s/koala/galaxy/' % user
data_path = '/home/%s/koala/dados/' % user

# GALAXY
galaxy_user = 'galaxyproject'
galaxy_project = 'galaxy'
galaxy_repository = 'https://github.com/%s/%s.git -b master' % (galaxy_user, galaxy_project)

# PULSAR
pulsar_user = 'galaxyproject'
pulsar_project = 'pulsar'
pulsar_repository = 'https://github.com/%s/%s.git -b master' % (pulsar_user, pulsar_project)

# KOALA
koala_user = 'adefelicibus'
koala_project = 'koala-server'
koala_repository = 'https://github.com/%s/%s.git -b master' % (koala_user, koala_project)

# koala server
username = 'koala'
port = 2221
port_http = 8080
koala_server = '%s@%s -p %s' % (username, ip_server, port)
env_path = '/home/%s/env/bin/activate' % username

# # pulsar server 7, docking09
username = 'koala'
port_http = 8092
pulsar_server_7 = '%s@%s' % (username, ip_server)

# hosts
# env.hosts = ["myserver.net"]
# env.user = "koala"
env.key_filename = "/home/%s/.ssh/id_rsa" % LOGGED_USER
# env.password = ""
env.port = 2234
env.hosts = [pulsar_server_7]
env.forward_agent = True

# -------------------------------
# SERVER
# -------------------------------

# ANTES DE QUALQUER COISA, CRIAR O USUARIO $user, COLOCAR COMO ROOT,
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
                'cmake /home/koala/programs/gromacs-4.6.5/ -DSHARED_LIBS_DEFAULT=OFF '
                '-DBUILD_SHARED_LIBS=OFF -DGMX_PREFER_STATIC_LIBS=YES '
                '-DGMX_BUILD_OWN_FFTW=OFF -DFFTW_LIBRARY=/usr/local/lib/libfftw3f.a '
                '-DFFTW_INCLUDE_DIR=/usr/local/include/ '
                '-DGMX_GSL=OFF -DGMX_DEFAULT_SUFFIX=ON -DGMX_GPU=OFF '
                '-DGMX_MPI=OFF -DGMX_DOUBLE=OFF '
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
        run('git cloen https://github.com/adefelicibus/PyHighcharts.git')
        with cd('/usr/lib/python2.7/dist-packages'):
            sudo('ln -s /home/%s/programs/PyHighcharts/ PyHighcharts' % user)


def install2PGCartesian():
    path = '2pg_cartesian'
    with cd("~/programs"):
        run('git clone https://github.com/rodrigofaccioli/2pg_cartesian.git %s' % path)
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
        run('pip install -r requirements.txt')


def buildEnvKoala_server():
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
        'ln -s /home/koala/koala-server/lib/koala/ \
        /home/koala/envs/%s/lib/python2.7/site-packages/koala' % pulsar_project)


def setConfigNginx():
    write_file('%s/config/nginx_server.conf' % CURRENT_PATH, '/etc/nginx/nginx.conf', 'config')


def setSitePulsarNginx():
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


def installScripts():
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
    run('echo `cat ~/.ssh/uploaded_key.pub` >> \
        ~/.ssh/authorized_keys && rm -f ~/.ssh/uploaded_key.pub')


def login():
    local("ssh %s" % pulsar_server_1)


def log(message):
    print """
==============================================================
%s
==============================================================
    """ % message

# -------------------------------
# LOCAL
# -------------------------------


def localLocale():
    log('Setting locale local')
    local('sudo locale-gen --no-purge --lang pt_BR')


def createLocalUser(user_senha=None):
    log('Create a new user local')
    """Create a new user local"""

    if not user_senha:
        user_senha = raw_input('Digite a senha do usuário "%s": ' % user)

    log('Criando usuário {0}'.format(user))
    local(
        'sudo useradd -m -p '
        'pass=$(perl -e \'print crypt($ARGV[0], "password")\' \'{0}\') {1}'.format(
            user_senha, user))
    print '\nSenha usuário: {0}'.format(user_senha)
    local('sudo gpasswd -a %s sudo' % user)
    print '\n============================================================='


def updateLocal():
    """Updating packages local"""
    log('Updating packages local')
    local('sudo apt-get -y update')


def upgradeLocal():
    """Updating programs"""
    log('Updating programs')
    local('sudo apt-get -y upgrade')


def buildLocal():
    """Install all necessary packages"""
    log('Installing all necessary packages')
    local('sudo apt-get -y install wget')
    local('sudo apt-get -y install git')
    local('sudo apt-get -y install python-dev')
    local('sudo apt-get -y install python-pip')
    local('sudo apt-get -y install zip')
    local('sudo apt-get -y install python-virtualenv')
    local('sudo apt-get -y install pymol')
    local('sudo apt-get -y install postgresql postgresql-contrib')
    local('sudo apt-get -y install openmpi-bin openmpi-doc libopenmpi-dev')
    local('sudo apt-get -y install automake')
    local('sudo apt-get -y install nginx supervisor')
    local('sudo apt-get -y install libcurl4-gnutls-dev')
    local('sudo apt-get -y install libffi-dev')
    local('sudo apt-get -y install python-numpy')
    local('sudo apt-get -y install gsl-bin libgsl0-dev')
    local('sudo apt-get -y install libpng-dev')
    local('sudo apt-get -y install libfreetype6-dev')
    local('sudo apt-get -y install libblas-dev liblapack-dev libatlas-base-dev gfortran')


def createDirectoriesLocal():
    log('Creating directories local')
    if(not os.path.exists('%sprograms' % folder_local)):
        local('sudo mkdir -p %sprograms' % folder_local)
    if(not os.path.exists('%sexecute' % data_path)):
        local('sudo mkdir -p %sexecute' % data_path)


def installZlibLocal():
    log('Installing zlib library local')
    with lcd('%sprograms' % folder_local):
        local('sudo wget http://zlib.net/zlib-1.2.8.tar.gz')
        local('sudo tar xzf zlib-1.2.8.tar.gz')
        with lcd('zlib-1.2.8'):
            local('sudo ./configure')
            local('sudo make')
            local('sudo make install')
    with lcd('%sprograms' % folder_local):
        local('sudo rm zlib-1.2.8.tar.gz')
        local('sudo rm -r zlib-1.2.8')


def installFFTWlocal():
    log('Installing FFTW library local')
    with lcd('%sprograms' % folder_local):
        local('sudo wget http://www.fftw.org/fftw-3.3.4.tar.gz')
        local('sudo tar xzf fftw-3.3.4.tar.gz')
        with lcd('fftw-3.3.4'):
            local('sudo ./configure --enable-float')
            local('sudo make')
            local('sudo make install')
    with lcd('%sprograms' % folder_local):
        local('sudo rm fftw-3.3.4.tar.gz')
        local('sudo rm -r fftw-3.3.4')


def installGROMACSlocal():
    log('Installing GROMACS package local')
    with lcd('%sprograms' % folder_local):
        local('sudo wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-4.6.5.tar.gz')
        local('sudo tar xzf gromacs-4.6.5.tar.gz')
        local('sudo chown %s:%s gromacs-4.6.5' % (LOGGED_USER, LOGGED_USER))
        with lcd('gromacs-4.6.5'):
            local('sudo mkdir build')
            with lcd('build'):
                local(
                    'sudo cmake .. -DSHARED_LIBS_DEFAULT=OFF '
                    '-DBUILD_SHARED_LIBS=OFF -DGMX_PREFER_STATIC_LIBS=YES '
                    '-DGMX_BUILD_OWN_FFTW=OFF -DFFTW_LIBRARY=/usr/local/lib/libfftw3f.a '
                    '-DFFTW_INCLUDE_DIR=/usr/local/include/ '
                    '-DGMX_GSL=OFF -DGMX_DEFAULT_SUFFIX=ON -DGMX_GPU=OFF '
                    '-DGMX_MPI=OFF -DGMX_DOUBLE=OFF '
                    '-DGMX_INSTALL_PREFIX=%sprograms/gmx-4.6.5/ '
                    '-DCMAKE_INSTALL_PREFIX=%sprograms/gmx-4.6.5/' % (
                        folder_local, folder_local))
                local('sudo make -j 8')
                local('sudo make install')
    with lcd('%sprograms' % folder_local):
        local('sudo rm -r gromacs-4.6.5')
        local('sudo rm gromacs-4.6.5.tar.gz')


def setExportLocal():
    log('Creating some exports variables local')
    if not os.path.exists("/home/%s/.bashrc" % user):
        local('sudo touch /home/%s/.bashrc' % user)
    local(
        'echo "export MPI_DIR=/lib/openmpi\n'
        'export LD_LIBRARY_PATH=/lib/openmpi/lib:$LD_LIBRARY_PATH" | \
        sudo tee --append /home/%s/.bashrc'
        % user)

    local("/bin/bash -l -c 'source ~/.bashrc'")


def installPyHighchartsLocal():
    log('Installing PyHighcharts local')
    with lcd('%sprograms' % folder_local):
        local('sudo mkdir PyHighcharts')
        local('sudo chown %s:%s PyHighcharts' % (LOGGED_USER, LOGGED_USER))
        local('git clone https://github.com/adefelicibus/PyHighcharts.git')
        with lcd('/usr/lib/python2.7/dist-packages'):
            local('sudo ln -s %sprograms/PyHighcharts/ PyHighcharts' % folder_local)


def install2PGCartesianLocal():
    log('Installing 2PG predictor local')
    path = '2pg_cartesian'
    with lcd("%sprograms" % folder_local):
        local('sudo mkdir %s' % path)
        local('sudo chown %s:%s %s' % (LOGGED_USER, LOGGED_USER, path))
        local('git clone https://github.com/rodrigofaccioli/2pg_cartesian.git %s' % path)
        with lcd(path):
            local('sudo mkdir build')
            with lcd('build'):
                local('sudo cmake ..')
                local('sudo make')
                local('sudo make install')
    # TODO: test if 2pg_cartesian folder is really necessary
    with lcd('%sprograms' % folder_local):
        local('sudo rm -r %s' % path)


def install2PGBuildConformationLocal():
    log('Installing 2PG build conformation local')
    path = '2pg_build_conformation'
    with lcd("%sprograms" % folder_local):
        local('sudo mkdir %s' % path)
        local('sudo chown %s:%s %s' % (LOGGED_USER, LOGGED_USER, path))
        local('git clone https://github.com/rodrigofaccioli/2pg_build_conformation.git %s' % path)
        with lcd('%s/src' % path):
            local('sudo make')
    with lcd("/usr/local/bin"):
        local('sudo ln -s %sprograms/%s/src/protpred-Gromacs_pop_initial .' % (folder_local, path))


def installMEAMTLocal():
    log('Creating directories local')
    with lcd("%sprograms" % folder_local):
        local('sudo cp %s/dependencies/meamt.zip .' % CURRENT_PATH)
        local('sudo unzip meamt.zip')
        local('sudo chown %s:%s meamt' % (LOGGED_USER, LOGGED_USER))
        with lcd('meamt'):
            local('sudo cp aemt-mo-up2 %sexecute/' % data_path)
            local('sudo cp aemt-pop-up2 %sexecute/' % data_path)
    with lcd("%sprograms" % folder_local):
        local('sudo rm -r meamt')
        local('sudo rm meamt.zip')


def installProtPredEDALocal():
    log('Installing ProtPredEda predictor local')
    with lcd("%sprograms" % folder_local):
        local('sudo cp %s/dependencies/protpred %sexecute' % (CURRENT_PATH, data_path))


def cloneGalaxyLocal():
    log('Installing Galaxy local')
    with lcd('%sprograms' % folder_local):
        local('sudo mkdir %s' % galaxy_project)
        local('sudo chown %s:%s %s' % (LOGGED_USER, LOGGED_USER, galaxy_project))
        local('git clone %s %s' % (galaxy_repository, galaxy_project))


def installJsmolLocal():
    log('Installing Jsmol local')
    with lcd("%sprograms" % folder_local):
        local('sudo cp %s/dependencies/jsmol.zip .' % CURRENT_PATH)
        local('sudo unzip jsmol.zip')
        local('sudo mkdir -p %sprograms/%s/static/js' % (
            folder_local, galaxy_project))
        local('sudo ln -s %sprograms/jsmol/* %sprograms/%s/static/js/' % (
            folder_local, folder_local, galaxy_project))


def buildEnvGalaxyLocal():
    log('Build env packages local')
    with lcd("%sprograms/%s" % (folder_local, galaxy_project)):
        local('sudo virtualenv .venv')
        local(". %sprograms/%s/.venv/bin/activate" % (
            folder_local, galaxy_project))
        with lcd(".venv"):
            local('sudo bin/pip install -U distribute')
            local('sudo bin/pip install pycrypto')
            local('sudo bin/pip install natsort')
            local('sudo bin/pip install beautifulsoup4')
            local('sudo bin/pip install certifi')
            local('sudo bin/pip install pyopenssl ndg-httpsclient pyasn1')
            local('sudo bin/pip install pycurl')
            local('sudo bin/pip install fabric')
            local('sudo bin/pip install Biopython')


def setKoalaLibLinksLocal():
    log('Creating links to Koala files local')
    local(
        'sudo ln -s %s/lib/koala/ %sprograms/%s/.venv/lib/python2.7/site-packages/koala' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/config/datatypes_conf.xml %sprograms/%s/config/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    # local(
    #     'sudo ln -s %s/config/galaxy.ini %sprograms/%s/config/' % (
    #         CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/config/integrated_tool_panel.xml %sprograms/%s/config/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/config/tool_conf.xml %sprograms/%s/config/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/datatypes/confFiles.py %sprograms/%s/lib/galaxy/datatypes/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/datatypes/gromacs_datatype.py %sprograms/%s/lib/galaxy/datatypes/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/datatypes/molFiles.py %sprograms/%s/lib/galaxy/datatypes/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/tools/analysis/ %sprograms/%s/tools/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/tools/gromacs-tools/ %sprograms/%s/tools/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/tools/meamt/ %sprograms/%s/tools/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/tools/pdb-tools/ %sprograms/%s/tools/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/tools/protpred-2pg/ %sprograms/%s/tools/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/tools/protpred-eda/ %sprograms/%s/tools/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/static/Bio-200.png %sprograms/%s/static/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/static/LOGO-ICMC-RGB-300.png %sprograms/%s/static/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/static/koala.css %sprograms/%s/static/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/static/logo-koala.png %sprograms/%s/static/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/static/usp-logo-300px.png %sprograms/%s/static/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/static/welcome.html %sprograms/%s/static/' % (
            CURRENT_PATH, folder_local, galaxy_project))


def copyExecuteFilesLocal():
    log('Coping necessary files local')
    local('sudo cp -rR %s/execute/ %s' % (CURRENT_PATH, data_path))


def setLibOpenMPILocal():
    log('Creating MPI lib links local')
    if not os.path.exists('/usr/lib/libmpi_cxx.so.1'):
        local('sudo ln -s /usr/lib/libmpi_cxx.so.0.0.1 /usr/lib/libmpi_cxx.so.1')
    if not os.path.exists('/usr/lib/openmpi/lib/libmpi_cxx.so.1'):
        local(
            'sudo ln -s /usr/lib/openmpi/lib/libmpi_cxx.so.0.0.1 \
            /usr/lib/openmpi/lib/libmpi_cxx.so.1')
    if not os.path.exists('/usr/lib/libmpi.so.1'):
        local('sudo ln -s /usr/lib/libmpi.so.0 /usr/lib/libmpi.so.1')
    if not os.path.exists('/usr/lib/openmpi/lib/libmpi.so.1'):
        local('sudo ln -s /usr/lib/openmpi/lib/libmpi.so /usr/lib/openmpi/lib/libmpi.so.1')


def installScriptsLocal():
    log('Installing Koala scripts to Galaxy local')
    local(
        'sudo ln -s %s/scripts/check_structures_gromacs.py %sprograms/%s/scripts/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/scripts/min.sh %sprograms/%s/scripts/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/scripts/prepare_structures.py %sprograms/%s/scripts/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/scripts/rename_atoms.py %sprograms/%s/scripts/' % (
            CURRENT_PATH, folder_local, galaxy_project))
    local(
        'sudo ln -s %s/scripts/residue_renumber_all_pdbs.py %sprograms/%s/scripts/' % (
            CURRENT_PATH, folder_local, galaxy_project))


def createDBKoalaLocal():
    log('Creating a DB to Koala local')
    local('sudo service postgresql restart')
    local(
        "echo 'CREATE USER %s SUPERUSER INHERIT CREATEDB CREATEROLE;' |"
        " sudo -u postgres psql" % user_db)
    local(
        'echo "ALTER USER %s PASSWORD \'koala\';" |'
        ' sudo -u postgres psql' % user_db)
    local(
        "echo 'CREATE DATABASE %s --OWNER %s;' |"
        " sudo -u postgres psql" % (bd, user_db))


def configureKoalaServer():
    # TODO: configure koala.ini according to directory and others here
    pass


def configurePymol():
    log('Configuring Galaxy to use Pymol local')
    with lcd('%sprograms/%s' % (folder_local, galaxy_project)):
        if os.path.exists('/usr/lib/python2.7/dist-packages/pymol'):
            local('sudo ln -s /usr/lib/python2.7/dist-packages/pymol \
                .venv/lib/python2.7/site-packages/')
        if os.path.exists('/usr/lib/python2.7/dist-packages/chempy'):
                local('sudo ln -s /usr/lib/python2.7/dist-packages/chempy \
                    .venv/lib/python2.7/site-packages/')


def setOwnFiles():
    log('Setting owner files local')
    local('sudo chown -R %s:%s %s' % (user, user, folder_local))


def newKoalaLocal(new_user=None):
    """Create a new Koala Server local"""
    log('Creating a new Koala Server local')

    localLocale()
    if new_user:
        createLocalUser()
    updateLocal()
    upgradeLocal()
    buildLocal()
    createDirectoriesLocal()
    installZlibLocal()
    installFFTWlocal()
    installGROMACSlocal()
    setExportLocal()
    installPyHighchartsLocal()
    install2PGCartesianLocal()
    install2PGBuildConformationLocal()
    installMEAMTLocal()
    installProtPredEDALocal()
    cloneGalaxyLocal()
    installJsmolLocal()
    buildEnvGalaxyLocal()
    setKoalaLibLinksLocal()
    copyExecuteFilesLocal()
    setLibOpenMPILocal()
    installScriptsLocal()
    createDBKoalaLocal()
    configurePymol()
    setOwnFiles()

    log('Your koala server has been installed.\n \
    Log with %s and run Galaxy server\n \
    sh %sprograms/%s/run.sh' % (
        user, folder_local, galaxy_project))
