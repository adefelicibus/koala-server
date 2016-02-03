#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
import shutil
import zipfile


def sendMultipleOutputs(path, files, path_output, outputID):
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
            self.ShowErrorMessage("Error when sendMultipleOutputs:\n%s" % e)
            # raise Exception("Error sendMultipleOutputs: %s" % e)

def openURL(url, path_output, file_name):
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
        self.ShowErrorMessage("Error when openURL:\n%s" % e)


def sendOutputResults(path_output, file_output, file_result):
        try:
            dest = path_output + "/" + file_output
            copia = "cp " + file_result + " " + dest
            os.system(copia)
            # shutil.copy(arquivo, new_path)
        except Exception, e:
            self.ShowErrorMessage("Error when sendOutputResults:\n%s" % e)


def sendOutputFilesHtml(path, files):  # copia os arquivos listados em files para o path
    try:
        for f in files:
            shutil.copy(f, path)
    except Exception, e:
        self.ShowErrorMessage("Error when sendOutputFilesHtml:\n%s" % e)


def getResultFiles(path, tool, fileName=None):
    try:
        resultFile = ''
        filesToHtml = []
        os.chdir(path)
        # if tool == '2PG_Random_Tool':
        #     resultFile = '%s%s' % (path, 'random_algorithm_solutions.pdb')
        if tool == '2PG_SortByFront_Tool':
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            listaArquivosFront = self.listDirectory(path, '*.front')
            for arq in listaArquivosFront:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosXvg = self.listDirectory(path, '*.xvg')
            for arq in listaArquivosXvg:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosPng = self.listDirectory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosLog = self.listDirectory(path, '*.log')
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
            listaArquivosFront = self.listDirectory(path, '*.front')
            for arq in listaArquivosFront:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosXvg = self.listDirectory(path, '*.xvg')
            for arq in listaArquivosXvg:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosPdf = self.listDirectory(path, '*.pdf')
            for arq in listaArquivosPdf:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosPng = self.listDirectory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosTxt = self.listDirectory(path, '*.txt')
            for arq in listaArquivosTxt:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosLog = self.listDirectory(path, '*.log')
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
                listaArquivosPDB = self.listDirectory(path, '%s*.pdb' % fileName)
            else:
                listaArquivosPDB = self.listDirectory(path, '*.pdb')
            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosXvg = self.listDirectory(path, '*.xvg')
            for arq in listaArquivosXvg:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosFit = self.listDirectory(path, '*.fit')
            for arq in listaArquivosFit:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosPng = self.listDirectory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
        elif(tool == 'ProtPred_EDA'):
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            listaArquivosPDB = self.listDirectory(path, '*.pdb')
            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosPng = self.listDirectory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
        elif tool == 'Download_From_Quark':
            resultFile = '%s%s' % (path, '/ResultQuark.zip')
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            listaArquivosPDB = self.listDirectory(path, '*.pdb')
            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
            listaArquivosTxt = self.listDirectory(path, '*.txt')
            for arq in listaArquivosTxt:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
        elif(tool == 'MEAMT_BuildConformation_Tool'):
            resultFile = '%s%s' % (path, 'pop_meamt.txt')
        elif(tool == 'MEAMT_Tool'):  # criar o html tbm, depois
            # resultFile = '%s%s' % (path, 'protein.pdb')
            resultFile = '%s%s.zip' % (path, tool)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            listaArquivosPDB = self.listDirectory(path, '*.pdb')
            for arq in listaArquivosPDB:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosPng = self.listDirectory(path, '*.png')
            for arq in listaArquivosPng:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
            listaArquivosTxt = self.listDirectory(path, 'subpop*.txt')
            for arq in listaArquivosTxt:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
                filesToHtml.append(os.path.join(path, arq))
        return resultFile, filesToHtml
    except Exception, e:
        self.ShowErrorMessage("Error when getResultFiles:\n%s" % e)
