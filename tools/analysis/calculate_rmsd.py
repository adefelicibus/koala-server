#!/usr/bin/env python
# -*- coding: utf-8 -*-

import __main__
__main__.pymol_argv = ['pymol', '-qc']  # Quiet and no GUI

import pymol
from time import sleep
import os
from koala import classe
import optparse
import subprocess
import time
import datetime
from decimal import *
from collections import OrderedDict
import zipfile
import gzip
import cProfile
import shutil
import math

pymol.finish_launching()


class CalculateRMSD(object):
    """
    Calculate the RMSD value from a set of PDB files using GROMACS
    """

    path_execute = None
    methods = []
    ignoreoutfiles = ['.pdb']
    initTime = 0
    endTime = 0
    rmsd_values = None
    command = None
    progname = "CalculateRMSD"

    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.CalculateRMSD.CalculateRMSD
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()
        self.command = 'echo C-alpha C-alpha | @PATH_GROMACS@./g_rms -f @PROT@ -s @NATIVE@ -o temporary_rmsd.xvg 2>/dev/null'

    def timenow(self):
        """
        Return current time as a formmated string
        @type self: koala.CalculateRMSD.CalculateRMSD
        """

        return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))

    def getfSize(self, fpath, outpath):
        """
        Get the file size and return as string
        @type self: koala.CalculateRMSD.CalculateRMSD
        @type fpath: string
        @type outpath: string
        """

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

    def run_renameAtoms(self, path, path_gromacs):
        """
        Create a subprocess to rename the missing atoms in a PDB file using pdb2gmx
        @type self: koala.CalculateRMSD.CalculateRMSD
        @type path: string
        @type path_gromacs: string
        """

        try:
            cl = [
                '%s/scripts/rename_atoms.py' %
                self.opts.galaxyroot, path, path_gromacs, '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            pvalue = retProcess.wait()

            if pvalue != 0:
                return False

            return True
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error while renaming atoms.\n%s" % e)

    def run_checkPDB(self, path, path_gromacs):
        """
        Create a subprocess to check the PDB structure using pdb2gmx
        @type self: koala.CalculateRMSD.CalculateRMSD
        @type path: string
        @type path_gromacs: string
        """

        try:
            cl = [
                '%s/scripts/check_structures_gromacs.py' %
                self.opts.galaxyroot, path, path_gromacs, '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            pvalue = retProcess.wait()

            if pvalue != 0:
                return False

            directory = os.path.join(path, 'no_accepted_by_pdb2gmx')
            if os.path.exists(directory):
                pdbs = os.listdir(directory)
                self.ClassColection.showMessage(
                    'These files could not be accepted by Gromacs.\n%s\n\n' % pdbs)

            return True
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error while checking PDBs:\n%s" % e)

    def buildRMSDTable(self):
        """
        Create an HTML table with the calculated RMSD values
        @type self: koala.CalculateRMSD.CalculateRMSD
        """
        try:
            html = ''
            for key, value in self.rmsd_values.items():
                html += '<tr>'
                html += '<td>%s</td>' % str(key)  # PDBFile
                # if(math.isinf(value)):
                #     value = '> 15 Å'
                # else:
                #     value = '%d Å' % value * 10
                html += '<td align="center">%s Å</td>' % str(value)  # RMSD
                html += '</tr>'
            return html
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error while buildRMSDTable:\n%s" % e)

    def makeHtml(self):
        """
        Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.CalculateRMSD.CalculateRMSD
        """

        try:
            galhtmlprefix = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <meta name="generator" content="Galaxy %s tool output - see http://g2.trac.bx.psu.edu/" />
            <title></title>
            <link rel="stylesheet" href="/static/koala.css" type="text/css" />
            <link rel="stylesheet" href="/static/style/base.css" type="text/css" />
            <script type="text/javascript"
            src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
            <script src="http://code.highcharts.com/highcharts.js"></script>
            <script src="http://code.highcharts.com/highcharts-more.js"></script>
            <script src="http://code.highcharts.com/modules/exporting.js"></script>
            </head>
            <body>
            <div class="toolFormBody">"""
            galhtmlpostfix = """</div></body></html>\n"""

            flist = os.listdir(self.opts.htmlfiledir)
            html = []
            html.append(galhtmlprefix % self.progname)
            html.append('<div class="sucessmessage">')
            html.append('<br>')
            html.append('<h1 align="center">RMSD results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Below, there is a table with the RMSD values.<br><br></div>')

            html.append('<div class="filetables">')
            html.append('<table border="1"><tr><th>Model</th><th>RMSD-Score</th></tr>\n')
            html.append(str(self.buildRMSDTable()))
            html.append('</table></div><br/>')

            fhtml = []
            frontFiles = []
            outputfiles = []
            compressedFile = []
            imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = self.ClassColection.getFileSize(fname, self.opts.htmlfiledir)

                    if e.lower() == ".front":
                        frontFiles.append(fname)
                    elif e.lower() == ".png":
                        imageFiles.append(fname)
                    elif e.lower() in ".zip, .gz":
                        compressedFile.append(fname)
                    elif not e.lower() in self.ignoreoutfiles:
                        outputfiles.append(fname)

            # Arquivos front
            for front in frontFiles:
                sfsize = self.ClassColection.getFileSize(front, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append('<td><a href="%s">%s</a></td>' % (front, front))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Download Calculated fronts.<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            fhtml = []

            # images (e depois models)
            listaArquivosPdb = self.methods

            if len(listaArquivosPdb) <= 20:  # mostra tudo
                size = int(len(listaArquivosPdb) / 5)
                rest = len(listaArquivosPdb) % 5
            else:
                size = 4  # vai mostrar no máximo 20 imagens
                rest = 0
            idx = 0  # controla indice das imagens e dos metodos
            start = 0
            end = 5  # limite de colunas para uma linha

            if size < 1:
                n = len(listaArquivosPdb)
                fhtml.append('<tr>')
                idx_linha = idx
                for i in range(0, n):
                    fhtml.append(
                        '<td><a href="%s"><img src="%s" '
                        'title="Click to see %s bigger" width="130"/></a></td>'
                        % (imageFiles[idx], imageFiles[idx], imageFiles[idx]))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, n):
                    fhtml.append(
                        '<td><a href="%s">%s</a></td>' % (
                                listaArquivosPdb[idx], listaArquivosPdb[idx]))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, n):
                    sfsize = self.ClassColection.getFileSize(
                            listaArquivosPdb[idx],
                            self.opts.htmlfiledir)
                    fhtml.append('<td>%s</td>' % (sfsize))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr>')
            else:
                for img in range(0, size):
                    fhtml.append('<tr>')
                    idx_linha = idx
                    for i in range(start, end):
                        fhtml.append(
                            '<td><a href="%s"><img src="%s" '
                            'title="Click to see %s bigger" width="130"/></a></td>'
                            % (imageFiles[idx], imageFiles[idx], imageFiles[idx]))
                        idx += 1
                    idx = idx_linha
                    fhtml.append('</tr><tr>')
                    for i in range(start, end):
                        fhtml.append(
                            '<td><a href="%s">%s</a></td>' % (
                                    listaArquivosPdb[idx], listaArquivosPdb[idx]))
                        idx += 1
                    idx = idx_linha
                    fhtml.append('</tr><tr>')
                    for i in range(start, end):
                        sfsize = self.ClassColection.getFileSize(
                                listaArquivosPdb[idx],
                                self.opts.htmlfiledir)
                        fhtml.append('<td>%s</td>' % (sfsize))
                        idx += 1
                    fhtml.append('</tr>')

                fhtml.append('<tr>')
                idx_linha = idx
                for i in range(0, rest):
                    fhtml.append(
                        '<td><a href="%s"><img src="%s" '
                        'title="Click to see %s bigger" width="130"/></a></td>'
                        % (imageFiles[idx], imageFiles[idx], imageFiles[idx]))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, rest):
                    fhtml.append(
                        '<td><a href="%s">%s</a></td>' % (
                                listaArquivosPdb[idx], listaArquivosPdb[idx]))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, rest):
                    sfsize = self.ClassColection.getFileSize(
                            listaArquivosPdb[idx],
                            self.opts.htmlfiledir)
                    fhtml.append('<td>%s</td>' % (sfsize))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Best Tertiary Structures<br>')
                html.append('<br></div>')

                if(self.opts.useJmol == 'true'):
                    html.append('<div class="active-jmol">')
                    html.append('<br>')
                    html.append(
                        '<a href=/datasets/%s/display/%s.htm>Activate JMol</a>' % (
                            self.opts.datasetID, self.opts.datasetID))
                    html.append('<br></div>')

                model = ''
                if size < 1:
                    for i in range(0, len(listaArquivosPdb)):
                        model += '<th>Model</th>'
                else:
                    model = '<th>Model</th>'\
                        '<th>Model</th>'\
                        '<th>Model</th>'\
                        '<th>Model</th>'\
                        '<th>Model</th>'
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1">'
                    '<tr>' +
                    model +
                    '</tr>\n')
                fhtml.append('</table></div><br/>')
                html += fhtml

            fhtml = []

            # Outros arquivos de output
            for output in outputfiles:
                sfsize = self.ClassColection.getFileSize(output, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append('<td><a href="%s">%s</a></td>' % (output, output))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Download the output files:<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>Output File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            fhtml = []

            # arquivo zipado
            for output in compressedFile:
                sfsize = self.ClassColection.getFileSize(output, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append('<td><a href="%s">%s</a></td>' % (output, output))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Compressed file with all the output files<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            self.ClassColection.setjobEnd(datetime.datetime.now())
            self.endTime = datetime.datetime.now()

            dif = self.ClassColection.calcTimeExecution(self.initTime, self.endTime)

            html.append('<div>Time execution:<br>')
            html.append('Start: %s<br>' %
                        self.ClassColection.getjobStart().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('End: %s<br>' %
                        self.ClassColection.getjobEnd().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('Total time: ~%dh:%dm:%ds' % (dif[0], dif[1], dif[2]))
            html.append('</div>')

            html.append('<hr>')
            html.append('<div>Citation<br>')
            html.append('This tool uses the g_rms program, part of GROMACS package.<br>')
            html.append('Please, cite the used algorithm in this tool:<br><br>')
            html.append('Van Der Spoel, D., Lindahl, E., Hess, B., Groenhof, G., Mark, '
                        'A. E. and Berendsen, H. J. C., GROMACS: Fast, flexible, and free. J. '
                        'Comput. Chem., 1701–1718. 2005')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file(self.opts.filehtml, 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()

        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error on makeHtml: \n%s" % e)

    def makeHtmlWithJMol(self, pdbReference):
        """
        Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.SortByFront.SortByFront
        """

        try:
            galhtmlprefix = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <meta name="generator" content="Galaxy %s tool output - see http://g2.trac.bx.psu.edu/" />
            <title></title>
            <link rel="stylesheet" href="/static/koala.css" type="text/css" />
            <link rel="stylesheet" href="/static/style/base.css" type="text/css" />
            <script type="text/javascript"
            src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
            <script src="http://code.highcharts.com/highcharts.js"></script>
            <script src="http://code.highcharts.com/highcharts-more.js"></script>
            <script src="http://code.highcharts.com/modules/exporting.js"></script>

            <script type="text/javascript" src="/static/js/JSmol.min.js"></script>

            <script type="text/javascript">

                    Jmol._isAsync = false;

                    Jmol.getProfile() // records repeat calls to overridden or overloaded Java methods

                    var jmolApplet0; // set up in HTML table, below

                    jmol_isReady = function(applet) {
                        document.title = (applet._id + " is ready")
                        Jmol._getElement(applet, "appletdiv").style.border="1px solid blue"
                    }

                    Info = {
                        width: 400,
                        height: 300,
                        debug: false,
                        color: "#F0F0F0",
                        zIndexBase: 20000,
                        z:{monitorZIndex:100},
                        addSelectionOptions: false,
                        serverURL: "/static/js/php/jsmol.php",
                        use: "HTML5",
                        jarPath: "/static/js/java",
                        j2sPath: "/static/js/j2s",
                        jarFile: "JmolApplet.jar",
                        isSigned: false,
                        disableJ2SLoadMonitor: false,
                        disableInitialConsole: false,
                        readyFunction: jmol_isReady,
                        allowjavascript: true,
                        script: "set antialiasDisplay;set showtiming;load async /datasets/%s/display/%s;cartoons only;color  cartoons structure; spin on"
                        //,defaultModel: ":dopamine"
                        //,noscript: true
                        //console: "none", // default will be jmolApplet0_infodiv
                        //script: "set antialiasDisplay;background white;load data/caffeine.mol;"
                        //delay 3;background yellow;delay 0.1;background white;for (var i = 0; i < 10; i+=1){rotate y 3;delay 0.01}"
                    }

            </script>

            </head>
            <body>
            <div class="toolFormBody">"""
            galhtmlpostfix = """</div></body></html>\n"""

            flist = os.listdir(self.opts.htmlfiledir)
            flist.sort()
            html = []
            html.append(galhtmlprefix % (self.progname, self.opts.datasetID, pdbReference))
            html.append('<div class="sucessmessage">')
            html.append('<br>')
            html.append('<h1 align="center">RMSD results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Below, there is a table with the RMSD values.<br><br></div>')

            html.append('<div class="filetables">')
            html.append('<table border="1"><tr><th>Model</th><th>RMSD-Score</th></tr>\n')
            html.append(str(self.buildRMSDTable()))
            html.append('</table></div><br/>')

            fhtml = []
            frontFiles = []
            outputfiles = []
            compressedFile = []
            imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = self.ClassColection.getFileSize(fname, self.opts.htmlfiledir)

                    if e.lower() == ".front":
                        frontFiles.append(fname)
                    elif e.lower() == ".png":
                        imageFiles.append(fname)
                    elif e.lower() in ".zip, .gz":
                        compressedFile.append(fname)
                    elif not e.lower() in self.ignoreoutfiles:
                        outputfiles.append(fname)

            # Arquivos front
            for front in frontFiles:
                sfsize = self.ClassColection.getFileSize(front, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append('<td><a href="%s">%s</a></td>' % (front, front))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Download Calculated fronts.<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            fhtml = []

            # images (e depois models)
            listaArquivosPdb = self.methods

            if len(listaArquivosPdb) <= 20:
                size = int(len(listaArquivosPdb) / 5)
                rest = len(listaArquivosPdb) % 5
            else:
                size = 4  # vai mostrar no máximo 20 imagens
                rest = 0
            idx = 0  # controla indice das imagens e dos metodos
            start = 0
            end = 5  # limite de colunas para uma linha

            if size < 1:
                n = len(listaArquivosPdb)
                fhtml.append('<tr>')
                idx_linha = idx
                for i in range(0, n):
                    pdbName, ext = os.path.splitext(listaArquivosPdb[idx])
                    fhtml.append(
                        '<td><a href="/datasets/%s/display/%s.png">'
                        '<img src="/datasets/%s/display/%s.png" '
                        'title="Click to see %s.png bigger" width="130"/></a></td>'
                        % (self.opts.datasetID, pdbName, self.opts.datasetID, pdbName, pdbName))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, n):
                    fhtml.append(
                        '<td><a href="/datasets/%s/display/%s">%s</a></td>' % (
                                self.opts.datasetID, listaArquivosPdb[idx], listaArquivosPdb[idx]))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, n):
                    sfsize = self.ClassColection.getFileSize(
                            listaArquivosPdb[idx],
                            self.opts.htmlfiledir)
                    fhtml.append('<td>%s</td>' % (sfsize))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, n):
                    fhtml.append(
                        '<td>'
                        '<a href="javascript:Jmol.script(jmolApplet0,'
                        "'load /datasets/%s/display/%s;cartoons only;color  cartoons structure; spin on')"
                        '">Load on Jmol</a></td>' % (
                            self.opts.datasetID, listaArquivosPdb[idx]))
                    idx += 1
                idx = idx_linha
            else:
                for img in range(0, size):
                    fhtml.append('<tr>')
                    idx_linha = idx
                    for i in range(start, end):
                        pdbName, ext = os.path.splitext(listaArquivosPdb[idx])
                        fhtml.append(
                            '<td><a href="/datasets/%s/display/%s.png">'
                            '<img src="/datasets/%s/display/%s.png" '
                            'title="Click to see %s.png bigger" width="130"/></a></td>'
                            % (self.opts.datasetID, pdbName, self.opts.datasetID, pdbName, pdbName))
                        idx += 1
                    idx = idx_linha
                    fhtml.append('</tr><tr>')
                    for i in range(start, end):
                        fhtml.append(
                            '<td><a href="/datasets/%s/display/%s">%s</a></td>' % (
                                    self.opts.datasetID, listaArquivosPdb[idx], listaArquivosPdb[idx]))
                        idx += 1
                    idx = idx_linha
                    fhtml.append('</tr><tr>')
                    for i in range(start, end):
                        sfsize = self.ClassColection.getFileSize(
                                listaArquivosPdb[idx],
                                self.opts.htmlfiledir)
                        fhtml.append('<td>%s</td>' % (sfsize))
                        idx += 1
                    idx = idx_linha
                    fhtml.append('</tr><tr>')
                    for i in range(start, end):
                        fhtml.append(
                            '<td>'
                            '<a href="javascript:Jmol.script(jmolApplet0,'
                            "'load /datasets/%s/display/%s;cartoons only;color cartoons structure; spin on')"
                            '">Load on Jmol</a></td>' % (
                                self.opts.datasetID, listaArquivosPdb[idx]))
                        idx += 1
                    # idx = idx_linha

                fhtml.append('<tr>')
                idx_linha = idx
                for i in range(0, rest):
                    pdbName, ext = os.path.splitext(listaArquivosPdb[idx])
                    fhtml.append(
                        '<td><a href="/datasets/%s/display/%s.png">'
                        '<img src="/datasets/%s/display/%s.png" '
                        'title="Click to see %s.png bigger" width="130"/></a></td>'
                        % (self.opts.datasetID, pdbName, self.opts.datasetID, pdbName, pdbName))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, rest):
                    fhtml.append(
                        '<td><a href="/datasets/%s/display/%s">%s</a></td>' % (
                                self.opts.datasetID, listaArquivosPdb[idx], listaArquivosPdb[idx]))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, rest):
                    sfsize = self.ClassColection.getFileSize(
                            listaArquivosPdb[idx],
                            self.opts.htmlfiledir)
                    fhtml.append('<td>%s</td>' % (sfsize))
                    idx += 1
                idx = idx_linha
                fhtml.append('</tr><tr>')
                for i in range(0, rest):
                    fhtml.append(
                        '<td>'
                        '<a href="javascript:Jmol.script(jmolApplet0,'
                        "'load /datasets/%s/display/%s;cartoons only;color cartoons structure; spin on')"
                        '">Load on Jmol</a></td>' % (
                            self.opts.datasetID, listaArquivosPdb[idx]))
                    idx += 1
                idx = idx_linha

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Best Tertiary Structures<br>')
                html.append('<br></div>')
                model = ''
                if size < 1:
                    for i in range(0, len(listaArquivosPdb)):
                        model += '<th>Model</th>'
                else:
                    model = '<th>Model</th>'\
                        '<th>Model</th>'\
                        '<th>Model</th>'\
                        '<th>Model</th>'\
                        '<th>Model</th>'
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1">'
                    '<tr>' +
                    model +
                    '</tr>\n')
                fhtml.append('</table></div><br/>')
                # html += fhtml

                fhtml.append('<div class="jmol-applet">')
                fhtml.append('<script>')
                fhtml.append('jmolApplet0 = Jmol.getApplet("jmolApplet0", Info)')
                fhtml.append("var lastPrompt=0;")
                fhtml.append('</script></div>')

                html += fhtml

            fhtml = []

            # Outros arquivos de output
            for output in outputfiles:
                sfsize = self.ClassColection.getFileSize(output, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append(
                    '<td><a href="/datasets/%s/display/%s">%s</a></td>' % (
                        self.opts.datasetID, output, output))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Download the output files:<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>Output File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            fhtml = []

            # arquivo zipado
            for output in compressedFile:
                sfsize = self.ClassColection.getFileSize(output, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append(
                    '<td><a href="/datasets/%s/display/%s">%s</a></td>' % (
                        self.opts.datasetID, output, output))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Compressed file with all the output files<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            self.ClassColection.setjobEnd(datetime.datetime.now())
            self.endTime = datetime.datetime.now()

            dif = self.ClassColection.calcTimeExecution(self.initTime, self.endTime)

            html.append('<div>Time execution:<br>')
            html.append('Start: %s<br>' %
                        self.ClassColection.getjobStart().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('End: %s<br>' %
                        self.ClassColection.getjobEnd().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('Total time: ~%dh:%dm:%ds' % (dif[0], dif[1], dif[2]))
            html.append('</div>')

            html.append('<hr>')
            html.append('<div>Citation<br>')
            html.append('This tool uses the g_rms program, part of GROMACS package.<br>')
            html.append('Please, cite the used algorithm in this tool:<br><br>')
            html.append('Van Der Spoel, D., Lindahl, E., Hess, B., Groenhof, G., Mark, '
                        'A. E. and Berendsen, H. J. C., GROMACS: Fast, flexible, and free. J. '
                        'Comput. Chem., 1701–1718. 2005')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file("%s.htm" % os.path.join(self.opts.htmlfiledir, self.opts.datasetID), 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error on makeHtmlWithJMol: \n%s" % e)

    def copyPDBReference(self):
        """
        Copy the input PDB referente to the execute path
        @type self: koala.CalculateRMSD.CalculateRMSD
        """
        try:
            self.opts.inputPDBRefName = self.opts.inputPDBRefName.replace(
                '(', '_').replace(
                        ')', '').replace(
                            " ", "").strip()
            link_name = os.path.join(
                    self.opts.htmlfiledir, os.path.basename(self.opts.inputPDBRefName))
            if not os.path.exists(link_name):
                os.symlink(self.opts.inputPDBRef, link_name)
                # os.system("cp %s %s" % (link_name, self.path_execute))
                shutil.copy(link_name, self.path_execute)
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Erro on copyPDBReference method:\n%s" % e)

    def build_images(self):
        """
        Build images from PDB files using PyMol package.
        @type self: koala.CalculateRMSD.CalculateRMSD
        """

        try:
            os.chdir(self.path_execute)

            limit = 20
            if len(self.methods) < 20:
                limit = len(self.methods)

            for i in range(0, limit):

                pdb = self.methods[i]
                arq = os.path.join(self.path_execute, pdb)

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
            self.ClassColection.ShowErrorMessage("Erro on build_images method:\n%s" % e)

    def getRMSDValues(self):
        """
        Calculate the RMSD value to the input PDB files
        @type self: koala.CalculateRMSD.CalculateRMSD
        """
        try:
            pdbs = self.ClassColection.listDirectory(self.path_execute, "*.pdb")

            if not pdbs:
                raise Exception("getRMSDValues: No PDB file found.\n")

            dict_rmsd = {}
            for pdb in pdbs:
                if not (pdb == self.opts.inputPDBRefName):

                    # aux_command = self.command.replace(
                    #     "@PATH_GROMACS@",
                    #     self.ClassColection.getPathGromacs()).replace(
                    #         "@PROT@",
                    #         (os.path.join(self.path_execute,  pdb))).replace(
                    #             "@NATIVE@",
                    #             (os.path.join(self.path_execute, self.opts.inputPDBRefName)))

                    # os.system(aux_command)

                    # temp_rmsd = open("temporary_rmsd.xvg", "r")
                    # for line in temp_rmsd.readlines():
                    #     if line.find("@") < 0 and line.find("#") < 0:
                    #         rmsd_value = float(str(line).split()[1])
                    #         only_pdb_file_name = os.path.basename(pdb)
                    #         dict_rmsd[only_pdb_file_name] = rmsd_value
                    # temp_rmsd.close()
                    # os.remove("temporary_rmsd.xvg")

                    # Load Structures
                    a = os.path.join(self.path_execute,  pdb)
                    aname, ext = os.path.splitext(pdb)
                    b = os.path.join(self.path_execute, self.opts.inputPDBRefName)
                    bname, ext = os.path.splitext(self.opts.inputPDBRefName)
                    pymol.cmd.load(a, aname)
                    pymol.cmd.load(b, bname)
                    ret = pymol.cmd.align(aname, bname)
                    rms = list(ret)
                    print 'rmds %s, atoms %s, residues %s' % (rms[0], rms[1], rms[-1])
                    only_pdb_file_name = os.path.basename(pdb)
                    dict_rmsd[only_pdb_file_name] = round(rms[0], 3)

                    sleep(0.25)  # (in seconds)
                    pymol.cmd.reinitialize()

            return OrderedDict(sorted(dict_rmsd.items(), key=lambda x: x[1]))

        except Exception, e:
            self.ClassColection.ShowErrorMessage("Erro on getRMSDValues method:\n%s" % e)

    def run_CalculateRMSD(self):
        """
        Get the PDB input files and run the calculation
        @type self: koala.CalculateRMSD.CalculateRMSD
        """
        try:
            dir_execucao = self.ClassColection.CreateExecutionDirectory()
            self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

            if self.opts.compressedFile == '1':

                inputFiles = self.opts.inputPdbs.split(",")

                for input_f in inputFiles:
                    if zipfile.is_zipfile(input_f):
                        self.ClassColection.extractZipFile(input_f, self.path_execute)
                    else:
                        try:
                            inF = gzip.GzipFile(input_f, 'rb')
                            f = inF.read()
                            inF.close()
                            if f:
                                self.ClassColection.extractGzFile(input_f, self.path_execute)
                        except Exception, e:
                            raise Exception("The input file could not be read.\n%s" % e)
            else:
                    self.ClassColection.copyPDBsFromInput(
                            self.path_execute,
                            self.opts.htmlfiledir,
                            self.opts.inputnames,
                            self.opts.inputPdbs)

            self.copyPDBReference()

            if(self.opts.renameAtoms == 'true'):
                if not self.run_renameAtoms(
                        self.path_execute, self.ClassColection.getPathGromacs()):
                    raise Exception("The script to rename the atoms finished wrong.")

            if(self.opts.checkStructures == 'true'):
                if not self.run_checkPDB(self.path_execute, self.ClassColection.getPathGromacs()):
                    raise Exception("The script to check the structure finished wrong.")

            self.rmsd_values = self.getRMSDValues()

            for key, value in self.rmsd_values.items():
                self.methods.append(key)

            self.build_images()

            pdbsToCopy = [os.path.join(self.path_execute, method) for method in self.methods]
            self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, pdbsToCopy)

            result, filesHtml = self.ClassColection.getResultFiles(
                    self.path_execute,
                    self.opts.toolname)

            self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, filesHtml)
            self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, [result])

            self.makeHtml()

            if(self.opts.useJmol == 'true'):
                self.makeHtmlWithJMol(pdbsToCopy[0].split('/')[-1])

        except Exception, e:
            self.ClassColection.ShowErrorMessage("Erro on run_CalculateRMSD method:\n%s" % e)

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputPDBRef', default=None)
    op.add_option('-a', '--inputPDBRefName', default=None)
    op.add_option('-p', '--inputPdbs', default=None)
    op.add_option('-z', '--filehtml', default=None)
    op.add_option('-k', '--htmlfiledir', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-g', '--galaxyroot', default=None)
    op.add_option('-n', '--inputnames', default=None)
    op.add_option('-s', '--compressedFile', default=None)
    op.add_option('-x', '--useJmol', default=None)
    op.add_option('-b', '--datasetID', default=None)
    op.add_option('-y', '--checkStructures', default=None)
    op.add_option('-c', '--renameAtoms', default=None)

    opts, args = op.parse_args()

    if not os.path.exists(opts.htmlfiledir):
        os.makedirs(opts.htmlfiledir)

    calcrmsd = CalculateRMSD(opts)

    calcrmsd.ClassColection.setjobStart(datetime.datetime.now())
    calcrmsd.initTime = datetime.datetime.now()

    cProfile.run('calcrmsd.run_CalculateRMSD()', 'profileout.txt')

    calcrmsd.ClassColection.clearPathExecute(calcrmsd.path_execute)
