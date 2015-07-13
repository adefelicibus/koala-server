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

echo $gromacsVersion

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
mv "${1##*/}" water.gro # $1 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)
mv "${2##*/}" water.tpr # $2 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)
mv "${3##*/}" top.top # $3 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)

#Local onde estao os binarios do gromacs
if [ $gromacsVersion == "5.0.2" ]; then
        gmx_path="/home/$USER/programs/gmx-5.0.2/no_mpi/bin/"
    else
        gmx_path="/home/$USER/programs/gmx-4.6.5/no_mpi/bin/"
fi

# Remove as águas a 5A da proteina.
# water_ok.gro é o arquivo sem a "camada" de águas ao redor da proteina e sem as águas dentro das cavidades
if [ $gromacsVersion == "5.0.2" ]; then
    "$gmx_path""./"gmx select -f water.gro -s water.tpr -on remover.ndx -select 'not same residue as resname SOL and within '$4' of group Protein' > /dev/null 2> /dev/null
    "$gmx_path""./"gmx trjconv -f water.gro -s water.tpr -n remover.ndx -o water_ok.gro > /dev/null 2> /dev/null
else
    "$gmx_path""./"g_select -f water.gro -s water.tpr -on remover.ndx -select 'not same residue as resname SOL and within '$4' of group Protein' > /dev/null 2> /dev/null
    "$gmx_path""./"trjconv -f water.gro -s water.tpr -n remover.ndx -o water_ok.gro > /dev/null 2> /dev/null
fi

# Até aqui as águas foram retiradas com sucesso no .gro, mas é preciso atualizar a quantidade de águas da topologia. O bloco em bash abaixo faz isso:
head -n-1 top.top > top_temporary		# top_temporary é top.top sem a última linha, que tem a quantidade de águas
total_aguas=$(grep SOL water_ok.gro | grep OW | wc -l | awk '{print $1}')	#conta o número de águas em water_ok.gro
echo "SOL              ""$total_aguas" >> top_temporary		# Adiciona a última linha corrigida ao top_temporary
mv top_temporary top.top		# Troca top_temporary por top.top, que agora tem o número de águas atualizado

# arquivos de saída
gro="water_ok.gro"
top="top.top"

# cópia dos arquivos de saída para o dataset
cp $diretorio$gro $5
cp $diretorio$top $6

# remove diretório temporário
cd ..
rm -rf $datetime
