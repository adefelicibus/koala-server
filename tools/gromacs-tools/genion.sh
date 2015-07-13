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

# atualiza diretório de execução
diretorio="/home/$USER/execute/$datetime/"
cd $datetime

# renomeia arquivo de entrada
mv "${1##*/}" tpr.tpr # $1 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)
mv "${2##*/}" top.top # $2 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)

#Local onde estao os binarios do gromacs
if [ $gromacsVersion == "5.0.2" ]; then
        gmx_path="/home/$USER/programs/gmx-5.0.2/no_mpi/bin/"
    else
        gmx_path="/home/$USER/programs/gmx-4.6.5/no_mpi/bin/"
fi

if [ $gromacsVersion == "5.0.2" ]; then
    echo "SOL" | "$gmx_path""./"gmx genion -s tpr.tpr -o gro.gro -p top.top -pname NA -nname CL -pq 1 -nq -1 -neutral -conc $3  > /dev/null 2> /dev/null
else
    echo "SOL" | "$gmx_path""./"genion -s tpr.tpr -o gro.gro -p top.top -pname NA -nname CL -pq 1 -nq -1 -neutral -conc $3  > /dev/null 2> /dev/null
fi

# adicionar íons
#echo "SOL" | "$gmx_path""./"gmx genion -s tpr.tpr -o gro.gro -p top.top -pname NA -nname CL -pq 1 -nq -1 -neutral -conc $3  > /dev/null 2> /dev/null

# arquivos de saída
gro="gro.gro"
top="top.top"

# cópia dos arquivos de saída para o dataset
cp $diretorio$gro $4
cp $diretorio$top $5

# remove diretório temporário
cd ..
rm -rf $datetime
