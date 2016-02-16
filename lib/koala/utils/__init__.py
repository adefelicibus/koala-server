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
import time
# from koala.utils.path import PathRuns

# TODO: review exception rules
# TODO: fix the time calculation when the diff is more than a day


def validate_email(email):
    try:
        email = email.replace('__at__', '@')

        if not(re.match('(.+)@(.+)\.(.+)', email, re.IGNORECASE)):
            raise Exception("Invalid email address. Please, insert a valid email adress.")

        return email

    except Exception, e:
        show_error_message("Error when ValidateEmail\n%s" % e)


def copy_necessary_files(source, destiny, framework):
    try:
        os.chdir(destiny)
        fileList = [os.path.normcase(f)
                    for f in os.listdir(source)]
        fileList = [os.path.join(source, f)
                    for f in fileList]
        for arquivo in fileList:
            if not os.path.isdir(arquivo):
                if(framework == 'MEAMT'):
                    shutil.copy(arquivo, destiny)
                else:
                    if(os.path.splitext(arquivo.split('/')[-1])[1] != '.txt'):
                        shutil.copy(arquivo, destiny)
            else:
                if not(re.search(r'\w+@\w+', arquivo)) and not(re.search(r'\d+_', arquivo)):
                    shutil.copytree(arquivo, os.path.join(destiny, arquivo.split('/')[-1]))
    except Exception, e:
        show_error_message("Error when CopyNecessaryFiles:\n%s" % e)


def get_file_size(fpath, outpath):
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
        show_error_message("Error on getFileSize\n%s" % e)


def compress_files(files, path, toolname):
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
        show_error_message("Error when compressFiles:\n%s" % e)


def extract_gz_file(gzfile, path):
    # TODO: Verificar se o arquivo tem folder e tratar
    try:
        shutil.copy(gzfile, path)

        subprocess.call(
            ["atool", '-q', '-X', path, os.path.join(path, os.path.basename(gzfile))])

    except Exception, e:
        show_error_message("Error when extractGzFile:\n%s" % e)


def extract_zip_file(zipFile, path):
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
        show_error_message("Error when extractZipFile:\n%s" % e)


def zip_folder(folder_path, output_path):
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
        show_error_message("Error when zipFolder:\n%s" % e)


def list_directory(directory, ereg=None):
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
        show_error_message("Error when listDirectory:\n%s" % e)


def get_logged_user():
    try:
        return getpass.getuser()
    except Exception, e:
        show_error_message("Error when getLoggedUser\n%s" % e)


def show_error_message(msg):
    error = sys.__stderr__
    error.write(msg)
    error.flush()
    sys.stderr = error
    sys.exit(1)


def show_message(msg):
    print msg


def show_warning_message(msg):
    info = sys.__stdout__
    info.write(msg)
    info.flush()
    sys.stdout = info


def get_timenow():
    """
    Return current time as a formmated string
    """

    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))


class TimeJobExecution(object):
    """docstring for TimeJobExecution"""

    def __init__(self):
        super(TimeJobExecution, self).__init__()

        self.jobStart = ''
        self.jobEnd = ''

    def get_job_start(self):
        return self.jobStart

    def set_job_start(self, jobStart):
        self.jobStart = jobStart

    def get_job_end(self):
        return self.jobEnd

    def set_job_end(self, jobEnd):
        self.jobEnd = jobEnd

    def calculate_time_execution(self):

        dif = self.jobEnd - self.jobStart

        minutes = 0
        if (dif.seconds / 60) > 60:
            minutes = (dif.seconds / 60) - ((dif.seconds / 3600) * 60)
        else:
            minutes = dif.seconds / 60

        return [
            dif.seconds / 3600,
            minutes,
            dif.seconds - ((dif.seconds / 60) * 60)]
