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

# atualiza diretório de execução
diretorio="/home/$USER/execute/$datetime/"
cd $datetime

# renomeia arquivo de entrada
mv "${1##*/}" $2 # $1 (remove o maior prefixo do tipo *., i.e., do começo até a última barra)

#PDB - Input
pdb_input=$2

#no (retira o ignh), yes mantêm. Quais proteínas e/ou qual protonoção aceita a opção no?
if [ "$5" = true ] ;
then
	ignh=" -ignh "
else
	ignh=" "
fi

#Local onde estao os binarios do gromacs
#gmx_path="/home/$USER/programs/gmx-5.0.2/no_mpi/bin/"
#gmx_path="/home/$USER/programs/gmx-4.6.5/no_mpi/bin/"

#Local onde estao os binarios do gromacs
if [ $gromacsVersion == "5.0.2" ]; then
        gmx_path="/home/$USER/programs/gmx-5.0.2/no_mpi/bin/"
    else
        gmx_path="/home/$USER/programs/gmx-4.6.5/no_mpi/bin/"
fi

# Gerar .gro e .top
# Ajustar os valores passados por echo de acordo com as histidinas presentes.
#IMPORTANTE: Checar protonação dos resíduos com propka sempre que for trabalhar com uma proteína nova.
# Se houver algum diferente do padrão (ASP e GLU com carga negativa e ARG e LYS com carga positiva),
# então usar -lys, -arg, -asp, -glu ou -inter.
# Lembrar da HIS. Realizar uma análise para saber qual melhor configuração HIS (HID ou HIE). Algumas observações
# estão no arquivo comando_DM. Somente para Lembrar que a HIS além de distância, devemos considerar o ângulo.
# CAPS: Verificar se há necessidade de acrescentá-los. Rever o arquivo Adicionar_caps.txt

#Observar o caso acima ANTES de executar o pdb2gmx.
# O echo eh para nao solicitar as his, pois sao todas HID
#echo 0 0 0 0 |"$gmx_path""./"gmx pdb2gmx -f $pdb_input -o prot -p top$ignh-ff $3 -water $4 -his  > /dev/null 2> /dev/null
#echo 0 0 0 0 |"$gmx_path""./"pdb2gmx -f $pdb_input -o prot -p top$ignh-ff $3 -water $4 -his  > /dev/null 2> /dev/null

if [ $gromacsVersion == "5.0.2" ]; then
        "$gmx_path""./"gmx pdb2gmx -f $pdb_input -o prot -p top$ignh-ff $3 -water $4  > /dev/null 2> /dev/null
        #echo 0 0 0 0 |"$gmx_path""./"gmx pdb2gmx -f $pdb_input -o prot -p top$ignh-ff $3 -water $4 -his  > /dev/null 2> /dev/null
    else
        "$gmx_path""./"pdb2gmx -f $pdb_input -o prot -p top$ignh-ff $3 -water $4  > /dev/null 2> /dev/null
        #echo 0 0 0 0 |"$gmx_path""./"pdb2gmx -f $pdb_input -o prot -p top$ignh-ff $3 -water $4 -his  > /dev/null 2> /dev/null
fi

# arquivos de saída
gro="prot.gro"
top="top.top"
itp="posre.itp"

# cópia dos arquivos de saída para o dataset
cp $diretorio$gro $6
cp $diretorio$top $7
cp $diretorio$itp $8

# remove diretório temporário
cd ..
rm -rf $datetime
