#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import shutil
import zipfile
import subprocess
from natsort import natsorted
import fnmatch
import getpass
import sys


def validateEmail(email):
        try:
            email = email.replace('__at__', '@')

            if not(re.match('(.+)@(.+)\.(.+)', email, re.IGNORECASE)):
                raise Exception("Invalid email address. Please, insert a valid email adress.")

            return email

        except Exception, e:
            self.ShowErrorMessage("Error when ValidateEmail\n%s" % e)


def copyNecessaryFiles(new_path):
        try:
            os.chdir(new_path)
            fileList = [os.path.normcase(f)
                        for f in os.listdir(self.getPathExecute())]
            fileList = [os.path.join(self.getPathExecute(), f)
                        for f in fileList]
            for arquivo in fileList:
                if not os.path.isdir(arquivo):
                    if(self.framework == 'MEAMT'):
                        shutil.copy(arquivo, new_path)
                    else:
                        if(os.path.splitext(arquivo.split('/')[-1])[1] != '.txt'):
                            shutil.copy(arquivo, new_path)
                else:
                    if not(re.search(r'\w+@\w+', arquivo)) and not(re.search(r'\d+_', arquivo)):
                        shutil.copytree(arquivo, os.path.join(new_path, arquivo.split('/')[-1]))
        except Exception, e:
            self.ShowErrorMessage("Error when CopyNecessaryFiles:\n%s" % e)


def getFileSize(fpath, outpath):
        """
        format a nice file size string
        """
        try:
            size = ''
            fp = os.path.join(outpath, fpath)
            if os.path.isfile(fp):
                size = '0 B'
                n = float(os.path.getsize(fp))
                if n > 2**20:
                    size = '%1.1f MB' % (n/2**20)
                elif n > 2**10:
                    size = '%1.1f KB' % (n/2**10)
                elif n > 0:
                    size = '%d B' % (int(n))
            return size
        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error on getFileSize\n%s" % e)


def compressFiles(files, path, toolname):
        # TODO: validar se files is a list
        try:
            os.chdir(path)
            resultFile = '%s%s.zip' % (path, toolname)
            z = zipfile.ZipFile(resultFile, 'w', zipfile.ZIP_DEFLATED)
            for arq in files:
                z = zipfile.ZipFile(resultFile, 'a', zipfile.ZIP_DEFLATED)
                z.write(arq)
                z.close()
            return True
        except Exception, e:
            self.ShowErrorMessage("Error when compressFiles:\n%s" % e)


def extractGzFile(gzfile, path):
        try:
            shutil.copy(gzfile, path)

            subprocess.call(
                ["atool", '-q', '-X', path, os.path.join(path, os.path.basename(gzfile))])

            # TODO: Verificar se o arquivo tem folder e tratar

        except Exception, e:
            self.ShowErrorMessage("Error when extractGzFile:\n%s" % e)


def extractZipFile(zipFile, path):
        try:
            with zipfile.ZipFile(zipFile) as zip_file:
                for member in zip_file.namelist():
                    filename = os.path.basename(member)

                    # skip directories
                    if not filename:
                        continue

                    # copy file (taken from zipfile's extract)
                    source = zip_file.open(member)
                    target = file(os.path.join(path, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
        except Exception, e:
            self.ShowErrorMessage("Error when extractZipFile:\n%s" % e)


def zipFolder(folder_path, output_path):
        """Zip the contents of an entire folder (with that folder included
        in the archive). Empty subfolders will be included in the archive
        as well.
        """
        parent_folder = os.path.dirname(folder_path)
        # Retrieve the paths of the folder contents.
        contents = os.walk(folder_path)
        try:
            zip_file = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
            for root, folders, files in contents:
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(parent_folder + '\\', '')
                    zip_file.write(absolute_path, relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path.replace(parent_folder + '\\', '')
                    zip_file.write(absolute_path, relative_path)
            zip_file.close()
        except Exception, e:
            self.ShowErrorMessage("Error when zipFolder:\n%s" % e)


def listDirectory(directory, ereg=None):
    try:
        # if self.framework == '2PG':
        fileList = [os.path.normcase(f)
                    for f in os.listdir(directory)]
        fileList = [os.path.normcase(f)
                    for f in fileList
                    if fnmatch.fnmatch(f, ereg)]
        # else:
        #     fileList = [os.path.normcase(f)
        #                 for f in os.listdir(directory)]
        #     fileList = [os.path.normcase(f)
        #                 for f in fileList
        #                 if os.path.isdir(f) and (re.search(r'out', f))]
        return natsorted(fileList)
    except Exception, e:
        self.ShowErrorMessage("Error when listDirectory:\n%s" % e)
        # raise Exception("Error while listing the directory.\n%s" % e)

def getjobStart():
        return self.jobStart


def setjobStart(jobStart):
    self.jobStart = jobStart


def getjobEnd():
    return self.jobEnd


def setjobEnd(jobEnd):
    self.jobEnd = jobEnd


def calcTimeExecution(start, end):

    dif = end - start

    minutes = 0
    if (dif.seconds / 60) > 60:
        minutes = (dif.seconds / 60) - ((dif.seconds / 3600) * 60)
    else:
        minutes = dif.seconds / 60

    return [
        dif.seconds / 3600,
        minutes,
        dif.seconds - ((dif.seconds / 60) * 60)]


def getLoggedUser():
    try:
        return getpass.getuser()
    except Exception, e:
        self.ShowErrorMessage("Error when setCommand\n%s" % e)


def ShowErrorMessage(msg):
        error = sys.__stderr__
        error.write(msg)
        error.flush()
        sys.stderr = error
        sys.exit(1)


def showMessage(msg):
    print msg


def ShowWarningMessage(msg):
    info = sys.__stdout__
    info.write(msg)
    info.flush()
    sys.stdout = info
