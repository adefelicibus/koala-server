# -*- coding: utf-8 -*-

import os
from fabric.api import *
from fabric.contrib.files import upload_template, append

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------
# ALTERAR CONFIGURAÇÕES BASEADAS NO SEUS SERVIDOR E MAQUINA LOCAL
# ----------------------------------------------------------------

# SERVIDOR
user = 'koala'
host = '200.144.255.35'
# chave = '/home/adefelicibus/.ssh/id_rsa'  # caminho da chave nome_arquivo (id_rsa)

#  LOCAL
folder_local = '~/koala/'

# GALAXY
galaxy_user = 'galaxyproject'
galaxy_project = 'galaxy'
galaxy_repository = 'git@github.com:%s/%s.git' % (galaxy_user, galaxy_project)

# PULSAR
pulsar_user = 'galaxyproject'
pulsar_project = 'pulsar'
pulsar_repository = 'git@github.com:%s/%s.git' % (pulsar_user, pulsar_project)

# KOALA
koala_user = 'adefelicibus'
koala_project = 'koala-server'
koala_repository = 'git@github.com:%s/%s.git' % (koala_user, koala_project)

# diretório do sites-enable do nginx
env.nginx_sites_enable_path = '/etc/nginx/sites-enabled'

# --------------------------------------------------------


env.hosts = [prod_server]

# --------------------------------------------------------
# LOCAL
# --------------------------------------------------------


def locale():
    local('sudo locale-gen --no-purge --lang pt_BR')


def adduser(user_senha):
    """Criar um usuário no servidor"""

    if not user_senha:
        user_senha = raw_input('Digite a senha do usuário: ')

    log('Criando usuário {0}'.format(user))
    local('sudo useradd -m -p pass=$(perl -e \'print crypt($ARGV[0], "password")\' \'{0}\') {1}'.format(
            user_senha, user))
    print '\nSenha usuário: {0}'.format(user_senha)
    local('sudo gpasswd -a %s sudo' % user)
    print '\n============================================================='


def login():
    """Acessa o servidor"""
    if chave:
        local("ssh %s -i %s" % (prod_server, env.key_filename))
    else:
        local("ssh %s" % prod_server)


# update no local
def update_local():
    """Updating packages"""
    log('Updating packages')
    local('sudo apt-get -y update')


# upgrade no local
def upgrade_local():
    """Updating programs"""
    log('Updating programs')
    local('sudo apt-get upgrade')


def build_local():
    """Install all necessary packages"""
    log('Installing all necessary packages')
    local('sudo apt-get -y install git')
    local('sudo apt-get -y install python-dev')
    local('sudo apt-get -y install python-pip')
    local('sudo apt-get -y install zip')
    local('sudo apt-get -y install python-virtualenv')
    local('sudo apt-get -y install pymol')
    local('sudo apt-get -y install postgresql postgresql-contrib')
    local('sudo pip install virtualenvwrapper')
    local('sudo apt-get -y install openmpi-bin openmpi-doc libopenmpi-dev')
    local('sudo apt-get -y install automake')
    local('sudo apt-get -y install nginx supervisor')
    # local('sudo apt-get -y install mercurial')
    local('sudo apt-get -y install libcurl4-gnutls-dev')
    local('sudo apt-get -y install libffi-dev')
    local('sudo apt-get -y install python-numpy')

    # local('sudo apt-get -y install libpcre3-dev')
    # local('sudo apt-get -y install openssl')
    # local('sudo apt-get -y install fort77')
    # local('sudo apt-get -y install cmake')
    # local('sudo apt-get -y install libc6-dev libssl-dev libexpat1-dev libgl1-mesa-dev libqt4-dev')
    # local('sudo apt-get -y install libglew-dev freeglut3-dev libpng-dev')
    # local('sudo apt-get -y install libfreetype6-dev')
    # local('sudo apt-get -y install terminator')
    # local('sudo apt-get -y install gsl-bin libgsl0-dev')
    # local('sudo pip install numpy')


def createDirectories():
    local('mkdir programs')
    local('mkdir envs')


def installzlib():
    local('cd ~/programs')
    local('wget http://zlib.net/zlib-1.2.8.tar.gz')
    local('tar xzf zlib-1.2.8.tar.gz')
    local('cd zlib-1.2.8')
    local('./configure')
    local('make')
    local('sudo make install')
    local('cd ..')
    local('rm zlib-1.2.8.tar.gz')
    local('sudo rm -r zlib-1.2.8')


def installFFTW():
    local('cd ~/programs')
    local('wget http://www.fftw.org/fftw-3.3.4.tar.gz')
    local('tar xzf fftw-3.3.4.tar.gz')
    local('cd fftw-3.3.4')
    local('./configure --enable-float')
    local('make')
    local('sudo make install')
    local('cd ..')
    local('rm fftw-3.3.4.tar.gz')


# somente para servidor koala
def setPostgres(user_senha):
    local('sudo -u postgres psql')
    local('CREATE USER %s SUPERUSER INHERIT CREATEDB CREATEROLE;' % user)
    local("ALTER USER %s PASSWORD ''%s'';" % (user, user_senha))
    local('CREATE DATABASE %sdb OWNER %s;' % (user, user))
    local('\q')
    local('sudo /etc/init.d/postgresql restart')


def installGROMACS():
    local('cd ~/programs')
    local('wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-4.6.5.tar.gz')
    local('tar xzf gromacs-4.6.5.tar.gz')
    local('cd gromacs-4.6.5')
    local('mkdir build')
    local('cd build/')
    local(
        'cmake .. -DSHARED_LIBS_DEFAULT=OFF -DBUILD_SHARED_LIBS=OFF -DGMX_PREFER_STATIC_LIBS=YES'
        '-DGMX_BUILD_OWN_FFTW=OFF -DFFTW_LIBRARY=/usr/local/lib/libfftw3f.a'
        '-DFFTW_INCLUDE_DIR=/usr/local/include/'
        '-DGMX_GSL=OFF -DGMX_DEFAULT_SUFFIX=ON -DGMX_GPU=OFF -DGMX_MPI=OFF -DGMX_DOUBLE=OFF'
        '-DGMX_INSTALL_PREFIX=/home/%s/programs/gmx-4.6.5/no_mpi/'
        '-DCMAKE_INSTALL_PREFIX=/home/%s/programs/gmx-4.6.5/no_mpi/' % (user, user))
    local('make -j 8')
    local('sudo make install')
    local('cd ../../')
    local('sudo rm -r gromacs-4.6.5')
    local('sudo rm gromacs-4.6.5.tar.gz')


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


# tem que criar uma ssh-key e colocar no git do usuario pra fazer o clone
def installPyHighcharts():
    local('cd ~/programs')
    local('git clone git@github.com:%s/PyHighcharts.git' % koala_user)
    local('cd /usr/lib/python2.7/dist-packages')
    local('sudo ln -s /home/%s/programs/PyHighcharts/ PyHighcharts' % user)


# clone Galaxy, somente servidor koala
def cloneGalaxy():
    """ Criar novo projeto local """
    log('Criando novo projeto')

    local('echo "clonando projeto %s"' % galaxy_project)
    local('git clone %s %s%s' % (galaxy_repository, folder_local, galaxy_project))
    local('cd %s%s' % (folder_local, galaxy_project))
    local('mkvirtualenv %s' % galaxyproject)
    local('setvirtualenvproject')
    local('pip install -r requirements.txt')


# clone Koala
def cloneKoala():
    """ Criar novo projeto local """
    log('Criando novo projeto')

    local('echo "clonando projeto %s"' % koala_project)
    local('git clone %s %s%s' % (koala_repository, folder_local, koala_project))
    local('cd %s%s' % (folder_local, koala_project))
    local('mkvirtualenv %s' % koala_project)
    local('setvirtualenvproject')
    local('pip install -r requirements.txt')


def buildEnvKoala():  # tem que instalar na env do galaxy tbm
    local('workon %s' % koala_project)
    local('pip install -U distribute')
    local('pip install pycrypto')
    local('pip install natsort')
    local('pip install beautifulsoup4')
    local('pip install certifi')
    local('pip install pyopenssl ndg-httpsclient pyasn1')
    local('pip install pycurl')
    local('pip install fabric')


# a maioria dos links vai ser somente para o servidor koala, nao pulsar
def createLinks():
    local('rm /home/koala/galaxy/config/galaxy.ini')
    local('ln -s /home/koala/koala-server/config/galaxy.ini /home/koala/galaxy/config/galaxy.ini')
    local('ln -s /home/koala/koala-server/config/datatypes_conf.xml /home/koala/galaxy/config/datatypes_conf.xml')
    local('ln -s /home/koala/koala-server/config/job_conf.xml /home/koala/galaxy/config/job_conf.xml')
    local('ln -s /home/koala/koala-server/config/reports_wsgi.ini /home/koala/galaxy/config/reports_wsgi.ini')
    local('ln -s /home/koala/koala-server/config/tool_conf.xml /home/koala/galaxy/config/tool_conf.xml')
    local('rm /home/koala/galaxy/config/integrated_tool_panel.xml')
    local('ln -s /home/koala/koala-server/config/integrated_tool_panel.xml /home/koala/galaxy/config/integrated_tool_panel.xml')

    local('ln -s /home/koala/koala-server/datatypes/confFiles.py /home/koala/galaxy/lib/galaxy/datatypes/confFiles.py')
    local('ln -s /home/koala/koala-server/datatypes/gromacs_datatype.py /home/koala/galaxy/lib/galaxy/datatypes/gromacs_datatype.py')
    local('ln -s /home/koala/koala-server/datatypes/molFiles.py /home/koala/galaxy/lib/galaxy/datatypes/molFiles.py')

    local('ln -s /home/koala/koala-server/static/Bio-200.png /home/koala/galaxy/static/Bio-200.png')
    local('ln -s /home/koala/koala-server/static/koala.css /home/koala/galaxy/static/koala.css')
    local('ln -s /home/koala/koala-server/static/LOGO-ICMC-RGB-300.png /home/koala/galaxy/static/LOGO-ICMC-RGB-300.png')
    local('ln -s /home/koala/koala-server/static/usp-logo-300px.png /home/koala/galaxy/static/usp-logo-300px.png')
    local('rm /home/koala/galaxy/static/welcome.html')
    local('ln -s /home/koala/koala-server/static/welcome.html /home/koala/galaxy/static/welcome.html')

    local('ln -s /home/koala/koala-server/tools/analysis/ /home/koala/galaxy/tools/analysis')
    local('ln -s /home/koala/koala-server/tools/gromacs-tools/ /home/koala/galaxy/tools/gromacs-tools')
    local('ln -s /home/koala/koala-server/tools/meamt/ /home/koala/galaxy/tools/meamt')
    local('ln -s /home/koala/koala-server/tools/pdb-tools/ /home/koala/galaxy/tools/pdb-tools')
    local('ln -s /home/koala/koala-server/tools/protpred-2pg/ /home/koala/galaxy/tools/protpred-2pg')
    local('ln -s /home/koala/koala-server/tools/protpred-eda/ /home/koala/galaxy/tools/protpred-eda')
    local('ln -s /home/koala/koala-server/tools/quark/ /home/koala/galaxy/tools/quark')
    local('ln -s /home/koala/koala-server/tools/robetta/ /home/koala/galaxy/tools/robetta')

    local('ln -s /home/koala/koala-server/scripts/check_structures_gromacs.py /home/koala/galaxy/scripts/check_structures_gromacs.py')
    local('ln -s /home/koala/koala-server/scripts/rename_atoms.py /home/koala/galaxy/scripts/rename_atoms.py')


def changePythonPath():
    local('PYTHONPATH="${PYTHONPATH}:/usr/lib/python2.7/dist-packages/"')
    local('PYTHONPATH="${PYTHONPATH}:/usr/lib/python2.7/dist-packages/pymol/"')
    local('PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python2.7/dist-packages/"')
    local('PYTHONPATH="${PYTHONPATH}:/usr/local/bin/pymol/modules/"')
    local('export PYTHONPATH')


# configura uma maquina local ubuntu
def setupLocal():
    """Configura uma maquina local Ubuntu para trabalhar python/django"""
    log('Configura uma computador Ubuntu para trabalhar python/django')

    # update
    update_local()
    upgrade_local()

    # packages
    build_local()

    # update
    update_local()
    upgrade_local()

    cloneGalaxy()

    # cloneKoala()

# --------------------------------------------------------
# SERVIDOR
# --------------------------------------------------------


def locale_server():
    sudo('locale-gen --no-purge --lang pt_BR')


def adduser_server(user_senha):
    """Criar um usuário no servidor"""

    if not user_senha:
        user_senha = raw_input('Digite a senha do usuário: ')

    log('Criando usuário {0}'.format(user))
    sudo('useradd -m -p pass=$(perl -e \'print crypt($ARGV[0], "password")\' \'{0}\') {1}'.format(
            user_senha, user))
    print '\nSenha usuário: {0}'.format(user_senha)
    sudo('gpasswd -a %s sudo' % user)
    print '\n============================================================='


# update no servidor
def update_server():
    """Atualizando pacotes no servidor"""
    log('Atualizando pacotes')
    sudo('apt-get -y update')


# upgrade no local
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


def createDirectories_server():
    sudo('mkdir ~/programs')
    sudo('mkdir ~/envs')


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
    sudo('cd ~/programs')
    sudo('wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-4.6.5.tar.gz')
    sudo('tar xzf gromacs-4.6.5.tar.gz')
    sudo('cd gromacs-4.6.5')
    sudo('mkdir build')
    sudo('cd build/')
    sudo(
        'cmake .. -DSHARED_LIBS_DEFAULT=OFF -DBUILD_SHARED_LIBS=OFF -DGMX_PREFER_STATIC_LIBS=YES'
        '-DGMX_BUILD_OWN_FFTW=OFF -DFFTW_LIBRARY=/usr/local/lib/libfftw3f.a'
        '-DFFTW_INCLUDE_DIR=/usr/local/include/'
        '-DGMX_GSL=OFF -DGMX_DEFAULT_SUFFIX=ON -DGMX_GPU=OFF -DGMX_MPI=OFF -DGMX_DOUBLE=OFF'
        '-DGMX_INSTALL_PREFIX=/home/%s/programs/gmx-4.6.5/no_mpi/'
        '-DCMAKE_INSTALL_PREFIX=/home/%s/programs/gmx-4.6.5/no_mpi/' % (user, user))
    sudo('make -j 8')
    sudo('make install')
    sudo('cd ../../')
    sudo('rm -r gromacs-4.6.5')
    sudo('rm gromacs-4.6.5.tar.gz')


#  verificar isso, como escreve em um arquivo com o fab
# http://docs.fabfile.org/en/latest/api/contrib/files.html
# ler a aprender
def setVirtualenv_server():
    sudo('vi ~/.bashrc')
    sudo('export WORKON_HOME=~/envs')
    sudo('source /usr/local/bin/virtualenvwrapper.sh')
    sudo('vi ~/.profile')
    sudo('export WORKON_HOME=~/envs')
    sudo('source /usr/local/bin/virtualenvwrapper.sh')
    sudo('source ~/.bashrc')
    sudo('source ~/.profile')


def installPyHighcharts_server():
    sudo('cd ~/programs')
    sudo('git clone git@github.com:%s/PyHighcharts.git' % koala_user)
    sudo('cd /usr/lib/python2.7/dist-packages')
    sudo('sudo ln -s /home/%s/programs/PyHighcharts/ PyHighcharts' % user)


# clone Koala
def cloneKoala_server():
    """ Criar novo projeto local """
    log('Criando novo projeto')

    sudo('git clone %s' % koala_repository)
    with cd('%s%s' % (folder_local, koala_project)):
        sudo('mkvirtualenv %s' % koala_project)
        sudo('setvirtualenvproject')
        sudo('pip install -r requirements.txt')


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

    sudo('git clone %s' % pulsar_repository)
    with cd('%s%s' % (folder_local, pulsar_project)):
        sudo('mkvirtualenv %s' % pulsar_project)
        sudo('setvirtualenvproject')
        sudo('pip install -r requirements.txt')


def buildEnvPulsar():  # tem que instalar na env do galaxy tbm
    sudo('workon %s' % pulsar_project)
    sudo('pip install -U distribute')
    sudo('pip install pycrypto')
    sudo('pip install natsort')
    sudo('pip install beautifulsoup4')
    sudo('pip install certifi')
    sudo('pip install pyopenssl ndg-httpsclient pyasn1')
    sudo('pip install pycurl')


def setKoalaLibLink_server():
    sudo('ln -s /home/koala/koala-server/lib/koala/ /home/koala/envs/%s/lib/python2.7/site-packages/koala' % pulsar_project)


# precisa configurar o nginx e iniciar
# precisa configurar o pulsar e iniciar
# precisa clonar/instalar/baixar/compilar o 2pg_cartesian


def newserver():
    """Configurar e instalar todos pacotes necessários para servidor"""
    log('Configurar e instalar todos pacotes necessários para servidor')

    locale_server()

    adduser_server('koala')

    update_server()

    upgrade_server()

    build_server()

    createDirectories_server()

    installzlib_server()



    # gera uma chave no servidor para utilizar o comando upload_public_key
    # run('ssh-keygen')

    # update_server()

    # update_server()
    # upgrade_server()

    # # pacotes
    # build_server()
    # python_server()
    # mysql_server()
    # git_server()
    # others_server()

    # # atualizando
    # update_server()
    # upgrade_server()

    # # mysql
    # mysql_restart

    # # nginx
    # write_file('nginx_server.conf', '/etc/nginx/nginx.conf')
    # nginx_restart()

    # # proftpd
    # write_file('proftpd.conf', '/etc/proftpd/proftpd.conf')
    # proftpd_restart()

    # # supervisor
    # write_file('supervisord_server.conf', '/etc/supervisor/supervisord.conf')
    # supervisor_restart()

    # # funcionar thumbnail no ubuntu 64bits
    # sudo("ln -s /usr/lib/'uname -i'-linux-gnu/libfreetype.so /usr/lib/")
    # sudo("ln -s /usr/lib/'uname -i'-linux-gnu/libjpeg.so /usr/lib/")
    # sudo("ln -s /usr/lib/'uname -i'-linux-gnu/libz.so /usr/lib/")

    # log('Anote a senha do banco de dados: {0}'.format(db_password))

    # log('Reiniciando a máquina')
    # reboot()

def listaccount():
    """Lista usuários do servidor"""
    log('Lista usuários do servidor')
    with cd('/home/'):
        run('ls')

def aptget(lib=None):
    """Executa apt-get install no servidor ex: fab aptget:lib=python-pip"""
    log('Executa apt-get install no servidor')
    if not lib:
        lib = raw_input('Digite o pacote para instalar: sudo apt-get install ')

    if lib:
        sudo('apt-get install {0}'.format(lib))
    # sudo('aptget {0}'.format(display))

# cria uma conta no servidor
def newaccount():
    """Criar uma nova conta do usuário no servidor"""
    log('Criar uma nova conta do usuário no servidor')

    # criando usuario
    if not env.conta:
        env.conta = raw_input('Digite o nome da conta: ')
    if not env.dominio:
        env.dominio = raw_input('Digite o domínio do site (sem www): ')
    if not env.linguagem:
        env.linguagem = raw_input('Linguagens disponíveis\n\n1) PYTHON\n2) PHP\n\nEscolha a linguagem: ')
        if not env.porta and int(env.linguagem) == 1:
            env.porta = raw_input('Digite o número da porta: ')
    if not env.mysql_password:
        env.mysql_password = raw_input('Digite a senha do ROOT do MySQL: ')

    # cria usuario no linux
    user_senha = create_password(12)
    adduser(env.conta, user_senha)

    sudo('mkdir /home/{0}/logs'.format(env.conta))
    sudo('touch /home/{0}/logs/access.log'.format(env.conta))
    sudo('touch /home/{0}/logs/error.log'.format(env.conta))

    if int(env.linguagem) == 1:
        sudo('virtualenv /home/{0}/env --no-site-packages'.format(env.conta))
        write_file('nginx.conf', '/home/{0}/nginx.conf'.format(env.conta))
        write_file('supervisor.ini', '/home/{0}/supervisor.ini'.format(env.conta))
        write_file('bash_login', '/home/{0}/.bash_login'.format(env.conta))
    else:
        write_file('nginx_php.conf', '/home/{0}/nginx.conf'.format(env.conta))
        sudo('mkdir /home/{0}/public_html/'.format(env.conta))

    # cria banco e usuario no banco
    banco_senha = create_password(12)
    newbase(env.conta, banco_senha)

    # da permissao para o usuario no diretorio
    sudo('chown -R {0}:{0} /home/{0}'.format(env.conta))

    nginx_restart()
    supervisor_restart()

    # log para salvar no docs
    log('Anotar dados da conta')
    print 'conta: {0} \n\n-- ssh\nuser: {0}\npw: {1} \n\n-- db\nuser: {0}\npw: {2}'.format(env.conta, user_senha, banco_senha)

def wri te_file(filename, destination):

    upload_template(
            filename=filename,
            destination=destination,
            template_dir=os.path.join(CURRENT_PATH, 'inc'),
            context=env,
            use_jinja=True,
            use_sudo=True,
            backup=True
        )

# deleta uma conta no servidor
def delaccount():
    """Deletar conta no servidor"""
    conta = raw_input('Digite o nome da conta: ')
    env.mysql_password = raw_input('Digite a senha do ROOT do MySQL: ')
    log('Deletando conta {0}'.format(conta))
    userdel(conta)
    dropbase(conta)


# cria usuario no servidor
# def adduser(conta=None, user_senha=None):
#     """Criar um usuário no servidor"""

#     if not user_senha:
#         user_senha = create_password(12)

#     if not conta:
#         conta = raw_input('Digite o nome do usuário: ')

#     log('Criando usuário {0}'.format(conta))
#     sudo('useradd -m -p pass=$(perl -e \'print crypt($ARGV[0], "password")\' \'{0}\') {1}'.format(user_senha, conta))
#     print '\nSenha usuário: {0}'.format(user_senha)
#     print '\n============================================================='


# MYSQL - cria usuario e banco de dados
def newbase(conta=None, banco_senha=None):
    """Criar banco de dados e usuário no servidor"""

    if not banco_senha:
        banco_senha = create_password(12)
    print 'Senha gerada para o banco: {0}'.format(banco_senha)

    if not conta:
        conta = raw_input('Digite o nome do banco: ')
    log('NEW DATABASE {0}'.format(conta))

    # cria acesso para o banco local
    sudo("echo CREATE DATABASE {0} | mysql -u root -p{1}".format(conta, env.mysql_password))
    sudo("echo \"CREATE USER '{0}'@'localhost' IDENTIFIED BY '{1}'\" | mysql -u root -p{2}".format(conta, banco_senha, env.mysql_password))
    sudo("echo \"GRANT ALL PRIVILEGES ON {0} . * TO '{0}'@'localhost'\" | mysql -u root -p{1}".format(conta, env.mysql_password))

    # cria acesso para o banco remoto
    sudo("echo \"CREATE USER '{0}'@'%' IDENTIFIED BY '{1}'\" | mysql -u root -p{2}".format(conta, banco_senha, env.mysql_password))
    sudo("echo \"GRANT ALL PRIVILEGES ON {0} . * TO '{0}'@'%'\" | mysql -u root -p{1}".format(conta, env.mysql_password))


# MYSQL - deleta o usuario e o banco de dados
def dropbase(conta=None):
    """Deletar banco de dados no servidor"""
    if not conta:
        conta = raw_input('Digite o nome do banco: ')
    if not env.mysql_password:
        env.mysql_password = raw_input('Digite a senha do ROOT do MySQL: ')
    sudo("echo DROP DATABASE {0} | mysql -u root -p{1}".format(conta, env.mysql_password))
    sudo("echo \"DROP USER '{0}'@'localhost'\" | mysql -u root -p{1}".format(conta, env.mysql_password))
    sudo("echo \"DROP USER '{0}'@'%'\" | mysql -u root -p{1}".format(conta, env.mysql_password))


# LINUX - deleta o usuario
def userdel(conta=None):
    """Deletar usuário no servidor"""
    if not conta:
        conta = raw_input('Digite o nome do usuario: ')
    log('Deletando usuário {0}'.format(conta))
    sudo('userdel -r {0}'.format(conta))




# upgrade no servidor
def upgrade_server():
    """Atualizar programas no servidor"""
    log('Atualizando programas')
    sudo('apt-get -y upgrade')


def build_server():
    """Instalar build-essential e outros pacotes importantes no servidor"""
    log('Instalando build-essential e outros pacotes')
    sudo('apt-get -y install build-essential automake')
    sudo('apt-get -y install libxml2-dev libxslt-dev')
    sudo('apt-get -y install libjpeg-dev libjpeg8-dev zlib1g-dev libfreetype6 libfreetype6-dev')

    # Then, on 32-bit Ubuntu, you should run:

    # sudo ln -s /usr/lib/i386-linux-gnu/libfreetype.so /usr/lib/
    # sudo ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib/
    # sudo ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib/

    # Otherwise, on 64-bit Ubuntu, you should run:

    # sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/
    # sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/
    # sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/

def python_server():
    """Instalar todos pacotes necessários do python no servidor"""
    log('Instalando todos pacotes necessários')
    sudo('sudo apt-get -y install python-imaging')
    sudo('apt-get -y install python python-dev python-setuptools python-mysqldb python-pip python-virtualenv')
    # sudo('easy_install -U distribute')


def mysql_server():
    """Instalar MySQL no servidor"""
    log('Instalando MySQL')

    db_password = create_password(12)

    sudo('echo mysql-server-5.0 mysql-server/root_password password {0} | debconf-set-selections'.format(db_password))
    sudo('echo mysql-server-5.0 mysql-server/root_password_again password {0} | debconf-set-selections'.format(db_password))
    sudo('apt-get -q -y install mysql-server')
    sudo('apt-get -y install libmysqlclient-dev') # nao perguntar senha do mysql pedir senha antes

    log('BANCO DE DADOS - PASSWORD')
    print 'password: '.format(db_password)


def git_server():
    """Instalar git no servidor"""
    log('Instalando git')
    sudo('apt-get -y install git')

def others_server():
    """Instalar nginx e supervisor"""
    log('Instalando nginx e supervisor')
    sudo('apt-get -y install nginx supervisor')
    sudo('apt-get -y install mercurial')
    try:
        sudo('apt-get -y install ruby rubygems')
    except:
        log('PACOTE DO RUBY GEMS FOI REMOVIDO DO PACKAGES DO UBUNTU')
    sudo('apt-get -y install php5-fpm php5-suhosin php-apc php5-gd php5-imagick php5-curl')
    sudo('apt-get -y install proftpd') # standalone nao perguntar
    sudo('gem install compass')

# def login():
#     """Acessa o servidor"""
#     if chave:
#         local("ssh %s -i %s" % (prod_server, env.key_filename))
#     else:
#         local("ssh %s" % prod_server)

def upload_public_key():
    """Faz o upload da chave ssh para o servidor"""
    log('Adicionando chave publica no servidor')
    ssh_file = '~/.ssh/id_rsa.pub'
    target_path = '~/.ssh/uploaded_key.pub'
    put(ssh_file, target_path)
    run('echo `cat ~/.ssh/uploaded_key.pub` >> ~/.ssh/authorized_keys && rm -f ~/.ssh/uploaded_key.pub')


# RESTART
def restart():
    """Reiniciar servicos no servidor"""
    log('reiniciando servicos')
    nginx_stop()
    nginx_start()
    nginx_restart()
    nginx_reload()
    supervisor_stop()
    supervisor_start()

def reboot():
    """Reinicia o servidor"""
    sudo('reboot')

def proftpd_restart():
    """restart proftpd"""
    log('restart proftpd')
    sudo('/etc/init.d/proftpd restart')

# SUPERVISOR APP
def start_server():
    """Start aplicação no servidor"""
    conta = raw_input('Digite o nome da app: ')
    log('inicia aplicação')
    sudo('supervisorctl start %s' % conta)


def stop_server():
    """Stop aplicação no servidor"""
    conta = raw_input('Digite o nome da app: ')
    log('para aplicação')
    sudo('supervisorctl stop %s' % conta)


def restart_server():
    """Restart aplicação no servidor"""
    conta = raw_input('Digite o nome da app: ')
    log('reinicia aplicação')
    sudo('supervisorctl restart %s' % conta)


# SUPERVISOR
def supervisor_start():
    """Start supervisor no servidor"""
    log('start supervisor')
    sudo('/etc/init.d/supervisor start')


def supervisor_stop():
    """Stop supervisor no servidor"""
    log('stop supervisor')
    sudo('/etc/init.d/supervisor stop')


def supervisor_restart():
    """Restart supervisor no servidor"""
    log('restart supervisor')
    sudo('/etc/init.d/supervisor stop')
    sudo('/etc/init.d/supervisor start')
    # sudo('/etc/init.d/supervisor restart')


# NGINX
def nginx_start():
    """Start nginx no servidor"""
    log('start nginx')
    sudo('/etc/init.d/nginx start')


def nginx_stop():
    """Stop nginx no servidor"""
    log('stop nginx')
    sudo('/etc/init.d/nginx stop')


def nginx_restart():
    """Restart nginx no servidor"""
    log('restart nginx')
    sudo('/etc/init.d/nginx restart')


def nginx_reload():
    """Reload nginx no servidor"""
    log('reload nginx')
    sudo('/etc/init.d/nginx reload')


def mysql_restart():
    """Restart mysql no servidor"""
    log('restart mysql')
    sudo('/etc/init.d/mysql restart')


def mysql_start():
    """start mysql no servidor"""
    log('start mysql')
    sudo('/etc/init.d/mysql start')


def mysql_stop():
    """stop mysql no servidor"""
    log('stop mysql')
    sudo('/etc/init.d/mysql stop')





# --------------------------------------------------------
# GLOBAL
# --------------------------------------------------------

# gera senha
def create_password(tamanho=12):
    """Gera uma senha - parametro tamanho"""
    from random import choice
    caracters = '0123456789abcdefghijlmnopqrstuwvxzkABCDEFGHIJLMNOPQRSTUWVXZK_#'
    senha = ''
    for char in xrange(tamanho):
        senha += choice(caracters)
    return senha


def log(message):
    print """
================================================================================
%s
================================================================================
    """ % message




# def mysql_local():
#     """Instalando MySQL"""
#     log('Instalando MySQL')
#     local('sudo apt-get -y install mysql-server libmysqlclient-dev')


# def python_local():
#     """Instalando todos pacotes necessários"""
#     log('Instalando todos pacotes necessários')
#     local('sudo apt-get -y install python python-dev python-setuptools python-mysqldb python-pip python-virtualenv')
#     local('sudo pip install -U distribute')
#     local('sudo pip install virtualenvwrapper')
#     local('sudo apt-get install python-imaging')

# def newproject():
#     """ Criar novo projeto local """
#     log('Criando novo projeto')
#     log('Cria a conta no bitbucket com o nome do projeto vazio que o script se encarregará do resto')

#     conta = raw_input('Digite o nome do projeto: ')

#     local('echo "clonando projeto %s"' % bitbucket_repository)
#     local('git clone {0} {1}{2}'.format(bitbucket_repository, folder_project_local, conta))
#     local('cd {0}{1}'.format(folder_project_local, conta))
#     local('mkvirtualenv {0}'.format(conta))
#     local('setvirtualenvproject')
#     local('pip install -r requirements.txt')
#     local('rm -rf {0}{1}/.git'.format(folder_project_local, conta))
#     local('rm -rf README.md')
#     local('git init')
#     local('git remote add origin git@bitbucket.org:{0}/{1}.git'.format(bitbucket_user, conta))