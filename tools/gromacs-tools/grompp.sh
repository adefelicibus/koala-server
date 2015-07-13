#!/bin/sh

# nao criar arquivos de backup do gromacs
export GMX_MAXBACKUP=-1

getGromacsVersion() {
    if command -v /home/$USER/programs/gmx-5.0.2/no_mpi/bin/mdrun >/dev/null 2>&1; then
        gromacsVersion="5.0.2"
    else
        gromacsVersion="4.6.5"
    fi
}

getGromacsVersion

# diretório padrão de execução
#diretorio="/home/$USER/execute/"
# $USER pega o usuário logado
diretorio="/home/$USER/execute/"
cd $diretorio

# cria diretório temporário nomeado pela data completa atual sem espaços
date=`date`
datetime=${date// /} # substitui todas as ocorrências de " " por ""
mkdir $datetime

# copia parâmetro de entrada para a nova pasta temporária
cp $1 $datetime
cp $2 $datetime
cp $3 $datetime

# atualiza diretório de execução
diretorio="/home/$USER/execute/$datetime/"
cd $datetime

# renomeia arquivo de entrada
mv "${1##*/}" mdp.mdp # $1 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)
mv "${2##*/}" gro.gro # $2 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)
mv "${3##*/}" top.top # $3 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)

#Local onde estao os binarios do gromacs
if [ $gromacsVersion == "5.0.2" ]; then
        gmx_path="/home/$USER/programs/gmx-5.0.2/no_mpi/bin/"
    else
        gmx_path="/home/$USER/programs/gmx-4.6.5/no_mpi/bin/"
fi

if [ $gromacsVersion == "5.0.2" ]; then
    "$gmx_path""./"gmx grompp -f mdp.mdp -c gro.gro -p top.top -o tpr.tpr > /dev/null 2> /dev/null
else
    "$gmx_path""./"grompp -f mdp.mdp -c gro.gro -p top.top -o tpr.tpr > /dev/null 2> /dev/null
fi

#"$gmx_path""./"gmx grompp -f mdp.mdp -c gro.gro -p top.top -o tpr.tpr > /dev/null 2> /dev/null

# arquivos de saída
tpr="tpr.tpr"

# cópia dos arquivos de saída para o dataset
cp $diretorio$tpr $4

# remove diretório temporário
cd ..
rm -rf $datetime
