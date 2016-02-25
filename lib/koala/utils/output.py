#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
import shutil
import zipfile
from time import sleep
from koala.utils import show_error_message, list_directory

# TODO: review exception rules
# TODO: use shutil.copy instead os.system


def send_multiple_outputs(path, files, path_output, outputID):
    try:
        for pdb in files:
            # pdb_name = pdb.split(".")[0].split("_")[2]
            name, ext = os.path.splitext(pdb)
            ext = ext.replace('.', '')
            pdb_name = os.path.basename(pdb)
            new_name = "%s_%s_%s_%s_%s" % ('primary', outputID, pdb_name, 'visible', ext)
            f = os.path.join(path, pdb)
            dest = path_output + '/' + new_name
            copia = "cp " + f + " " + dest
            os.system(copia)
    except Exception, e:
        show_error_message("Error when sendMultipleOutputs:\n%s" % e)


def open_url(url, path_output, file_name):
    """
    Download the file from `url` and save it locally under `file_name`
    """
    try:
        response = urllib2.urlopen(url)
        file_result = os.path.join(path_output, file_name)
        out_file = open(file_result, 'wb')
        out_file.write(response.read())
        out_file.close()
    except Exception, e:
        show_error_message("Error when openURL:\n%s" % e)


def send_output_results(path_output, file_output, file_result):
    try:
        dest = path_output + "/" + file_output
        copia = "cp " + file_result + " " + dest
        os.system(copia)
        # shutil.copy(arquivo, new_path)
    except Exception, e:
        show_error_message("Error when sendOutputResults:\n%s" % e)


def send_output_files_html(path, files):
    try:
        for f in files:
            shutil.copy(f, path)
    except Exception, e:
        show_error_message("Error when sendOutputFilesHtml:\n%s" % e)


def get_result_files(path, tool, fileName=None):
    try:
        resultFile = ''
        filesToHtml = []
        os.chdir(path)

        if tool == '2PG_SortByFront_Tool':
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)

            listaArquivosFront = list_directory(path, '*.front')
            for arq in listaArquivosFront:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosXvg = list_directory(path, '*.xvg')
            for arq in listaArquivosXvg:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosPng = list_directory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosLog = list_directory(path, '*.log')
            for arq in listaArquivosLog:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

        elif tool in (
                'Dominance_Ranking', '2PG_SortMethodByFront_Tool',
                'CalculateRMSD', 'CalculateTMScore', 'CalculateGDTTS'):
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)

            listaArquivosFront = list_directory(path, '*.front')
            for arq in listaArquivosFront:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosXvg = list_directory(path, '*.xvg')
            for arq in listaArquivosXvg:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosPdf = list_directory(path, '*.pdf')
            for arq in listaArquivosPdf:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosPng = list_directory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosTxt = list_directory(path, '*.txt')
            for arq in listaArquivosTxt:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosLog = list_directory(path, '*.log')
            for arq in listaArquivosLog:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

        elif tool == '2PG_BuildConformation_Tool':
            resultFile = '%s%s' % (path, 'pop_0.pdb')

        elif tool in (
                '2PG_NSGA2_Tool', '2PG_Mono_Tool',
                '2PG_MC_Metropolis', '2PG_Random_Tool'):
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)

            if(fileName):
                listaArquivosPDB = list_directory(path, '%s*.pdb' % fileName)
            else:
                listaArquivosPDB = list_directory(path, '*.pdb')

            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosXvg = list_directory(path, '*.xvg')
            for arq in listaArquivosXvg:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosFit = list_directory(path, '*.fit')
            for arq in listaArquivosFit:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosPng = list_directory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

        elif(tool == 'ProtPred_EDA'):
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)

            listaArquivosPDB = list_directory(path, '*.pdb')
            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosPng = list_directory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

        elif tool == 'Download_From_Quark':
            resultFile = '%s%s' % (path, '/ResultQuark.zip')
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            listaArquivosPDB = list_directory(path, '*.pdb')

            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
            listaArquivosTxt = list_directory(path, '*.txt')

            for arq in listaArquivosTxt:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()

        elif(tool == 'MEAMT_BuildConformation_Tool'):
            resultFile = '%s%s' % (path, 'pop_meamt.txt')

        elif(tool == 'MEAMT_Tool'):
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)

            listaArquivosPDB = list_directory(path, '*.pdb')
            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosPng = list_directory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

            listaArquivosTxt = list_directory(path, 'subpop*.txt')
            for arq in listaArquivosTxt:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))

        return resultFile, filesToHtml

    except Exception, e:
        show_error_message("Error when getResultFiles:\n%s" % e)


def build_images(methods, path_execution):
    """
    Build images from PDB files using PyMol package.
    @type self: koala.CalculateGDTTS.CalculateGDTTS
    """
    import __main__
    __main__.pymol_argv = ['pymol', '-qc']
    import pymol
    __main__.pymol = pymol
    pymol.finish_launching()

    try:
        os.chdir(path_execution)

        limit = 20
        if len(methods) < 20:
            limit = len(methods)

        for i in range(0, limit):

            pdb = methods[i]
            arq = os.path.join(path_execution, pdb)

            name, ext = os.path.splitext(pdb)

            # Load Structures
            pymol.cmd.load(arq, pdb)
            pymol.cmd.disable("all")
            pymol.cmd.set('ray_opaque_background', 0)
            pymol.cmd.set('antialias', 1)
            pymol.cmd.hide("everything")
            pymol.cmd.show("cartoon")
            pymol.cmd.show("ribbon")
            pymol.cmd.enable(pdb)
            pymol.cmd.ray()
            pymol.cmd.png("%s.png" % name, dpi=300)

            sleep(0.25)  # (in seconds)

            pymol.cmd.reinitialize()

    except Exception, e:
        show_error_message("Erro on build_images method:\n%s" % e)
