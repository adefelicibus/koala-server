#!/usr/bin/env python
# -*- coding: utf-8 -*-

import __main__
__main__.pymol_argv = ['pymol', '-qc']  # Quiet and no GUI

import pymol
import os
from koala import classe
import optparse
import subprocess
import datetime
import time
import cProfile
import shutil

pymol.finish_launching()


class NSGAII2PG(object):
    """
    Execute the 2PG NSGA-II multiobjective evolutionary algorithm.
    """

    path_execute = None
    sequence = None
    initTime = 0
    endTime = 0
    ignoreoutfiles = ['.pdb']

    progname = "2PG NSGA-II"
    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.NSGAII2PG.NSGAII2PG
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()
        self.ClassColection.setFramework("2PG")

    def makeHtml(self):
        """ Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.NSGAII2PG.NSGAII2PG
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
            flist.sort()
            html = []
            html.append(galhtmlprefix % self.progname)
            html.append('<div class="sucessmessage">')
            html.append('<br>')
            html.append('<h1 align="center">2PG NSGA-II Ab Initio Algorithm results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Submitted Primary Sequence.<br><br></div>')
            html.append('<div class="code">')
            html.append('Length: %s<br>' % len(self.sequence))
            html.append('%s<br></div>' % self.sequence)

            # Dowload arquivos pop_X.pdb
            # mostrar artigo do 2PG, com link da publicação

            fhtml = []
            fitFiles = []
            # popFiles = []
            outputfiles = []
            compressedFile = []
            imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = self.ClassColection.getFileSize(fname, self.opts.htmlfiledir)

                    if e.lower() == ".fit":
                        fitFiles.append(fname)
                    elif e.lower() == ".png":
                        imageFiles.append(fname)
                    elif e.lower() in ".zip, .gz":
                        compressedFile.append(fname)
                    elif not e.lower() in self.ignoreoutfiles:
                        outputfiles.append(fname)

            # Arquivos fit
            for fit in fitFiles:
                sfsize = self.ClassColection.getFileSize(fit, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append('<td><a href="%s">%s</a></td>' % (fit, fit))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Download Calculated values of selected Objectives.<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            fhtml = []

            # images (e depois models)
            listaArquivosPdb = self.ClassColection.listDirectory(
                self.path_execute, 'NSGAIISolutions-M*.pdb')

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
                        listaArquivosPdb[idx], self.opts.htmlfiledir)
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
                        listaArquivosPdb[idx], self.opts.htmlfiledir)
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
            html.append('End: %s<br>' % self.ClassColection.getjobEnd().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('Total time: ~%dh:%dm:%ds' % (dif[0], dif[1], dif[2]))
            html.append('</div>')

            html.append('<hr>')
            html.append('<div>Citation<br>')
            html.append('Please, cite the used algorithm in this tool:<br><br>')
            html.append('R. A. Faccioli, L. O. Bortot and A. C. B. Delbem. Multi-Objective'
                        'Evolutionary Algorithm NSGA-II for Protein Structure Prediction using '
                        'Structural and Energetic Properties. IJNCR, 4(1), 43-53, 2014.')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file(self.opts.filehtml, 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()

        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error on makeHtml:\n%s" % e)

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
            html.append('<h1 align="center">2PG NSGA-II Ab Initio Algorithm results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Submitted Primary Sequence.<br><br></div>')
            html.append('<div class="code">')
            html.append('Length: %s<br>' % len(self.sequence))
            html.append('%s<br></div>' % self.sequence)

            fhtml = []
            fitFiles = []
            outputfiles = []
            compressedFile = []
            imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = self.ClassColection.getFileSize(fname, self.opts.htmlfiledir)

                    if e.lower() == ".fit":
                        fitFiles.append(fname)
                    elif e.lower() == ".png":
                        imageFiles.append(fname)
                    elif e.lower() in ".zip, .gz":
                        compressedFile.append(fname)
                    elif not e.lower() in self.ignoreoutfiles:
                        outputfiles.append(fname)

            # Arquivos fit
            for fit in fitFiles:
                sfsize = self.ClassColection.getFileSize(fit, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append('<td><a href="%s">%s</a></td>' % (fit, fit))
                fhtml.append('<td>%s</td>' % (sfsize))
                fhtml.append('</tr>')

            if len(fhtml) > 0:
                html.append('<br>')
                html.append('<div class="sectionmessage">')
                html.append('<br>Download Calculated values of selected Objectives.<br><br></div>')
                fhtml.insert(
                    0,
                    '<div class="filetables"><table border="1"><tr><th>File</th>'
                    '<th>Size</th></tr>\n')
                fhtml.append('</table></div><br>')
                html += fhtml

            fhtml = []

            # images (e depois models)
            listaArquivosPdb = self.ClassColection.listDirectory(
                self.path_execute, 'NSGAIISolutions-M*.pdb')

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
                            '<td><a href="/datasets/%s/display/%s">%s</a></td>'
                            % (
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
            html.append('Please, cite the used algorithm in this tool:<br><br>')
            html.append('R. A. Faccioli, L. O. Bortot and A. C. B. Delbem. Multi-Objective'
                        'Evolutionary Algorithm NSGA-II for Protein Structure Prediction using '
                        'Structural and Energetic Properties. IJNCR, 4(1), 43-53, 2014.')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file("%s.htm" % os.path.join(self.opts.htmlfiledir, self.opts.datasetID), 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()

        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error on makeHtmlWithJMol:\n%s" % str(e))

    def build_images(self):
        """
        Build images from PDB files using PyMol package.

        @type self: koala.NSGAII2PG.NSGAII2PG
        """
        try:
            listaArquivosPdb = self.ClassColection.listDirectory(
                    self.path_execute, 'NSGAIISolutions-M*.pdb')

            os.chdir(self.path_execute)

            limit = 20
            if len(listaArquivosPdb) < 20:
                limit = len(listaArquivosPdb)
            for i in range(0, limit):

                pdb = listaArquivosPdb[i]
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

                pymol.cmd.save("%s.pdb" % os.path.join(self.path_execute, name), name)

                time.sleep(0.25)  # (in seconds)

                pymol.cmd.reinitialize()

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

    def runCheckPDB(self, path, path_gromacs):
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

    def runPreparePDB(self, path, path_gromacs):
        try:
            cl = [
                '%s/scripts/prepare_structures.py' %
                self.opts.galaxyroot, path, '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            pvalue = retProcess.wait()

            if pvalue != 0:
                return False

            return True
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error while preparing PDBs:\n%s" % e)

    def runResidueRenumber(self, path, path_gromacs):
        try:
            cl = [
                '%s/scripts/residue_renumber_all_pdbs.py' %
                self.opts.galaxyroot, path, path_gromacs, '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            pvalue = retProcess.wait()

            if pvalue != 0:
                return False

            return True
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error while renumbering PDBs:\n%s" % e)

    def runMinimization(self, path, path_gromacs, pdbPrefix=None):
        try:
            cl = ['%s/min.sh' % path, path, path_gromacs, pdbPrefix, '&']

            shutil.copy(
                os.path.join(
                    '%s/scripts/%s' % (self.opts.galaxyroot, 'min.sh')),
                self.path_execute)

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            pvalue = retProcess.wait()

            if pvalue != 0:
                return False

            return True
        except Exception, e:
            self.ClassColection.ShowErrorMessage("Error while minimization PDBs:\n%s" % e)

    def minimization(self, path, path_gromacs, pdbPrefix=None):
        if not self.runCheckPDB(path, path_gromacs):
            raise Exception("The script to check the PDBs finished wrong.")

        if not self.runPreparePDB(path, path_gromacs):
            raise Exception("The script to prepare the PDBs finished wrong.")

        if not self.runResidueRenumber(path, path_gromacs):
            raise Exception("The script to renumber the residues finished wrong.")

        if not self.runMinimization(path, path_gromacs, pdbPrefix):
            raise Exception("The script of minimization finished wrong.")

    def run_NSGAII(self):
        """
        Create the 2PG NSGA-II configuration file and begin the execution.

        @type self: koala.NSGAII2PG.NSGAII2PG
        """
        try:
            if(self.opts.inputEmail):
                email = self.ClassColection.ValidateEmail(self.opts.inputEmail)
                dir_execucao = self.ClassColection.CreateExecutionDirectory(email)
            else:
                dir_execucao = self.ClassColection.CreateExecutionDirectory()

            self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

            self.sequence = self.ClassColection.CreateLocalFastaFile(
                        self.path_execute,
                        self.opts.fromFasta,
                        self.opts.inputFasta,
                        self.opts.toolname)

            SizePopulation = self.ClassColection.CreateLocalPopFile(
                    self.path_execute, self.opts.inputPop)

            self.ClassColection.CopyNecessaryFiles(self.path_execute)

            self.ClassColection.setParameter('NumberGeration', self.opts.numberGeration)
            self.ClassColection.setParameter('SizePopulation', SizePopulation)
            self.ClassColection.setParameter(
                    'SequenceAminoAcidsPathFileName',
                    self.path_execute + 'fasta.txt')
            self.ClassColection.setParameter('How_Many_Rotation', self.opts.howManyRotation)
            self.ClassColection.setParameter('rotamer_library', self.opts.rotamerLibrary)
            self.ClassColection.setParameter(
                    'objective_analisys_dimo_source',
                    '/home/%s/programs/dimo/DIMO2' % self.ClassColection.getLoggedUser())
            self.ClassColection.setParameter('Local_Execute', self.path_execute)
            self.ClassColection.setParameter(
                    'Path_Gromacs_Programs',
                    '/home/%s/programs/gmx-4.6.5/no_mpi/bin/' % self.ClassColection.getLoggedUser())
            self.ClassColection.setParameter('NativeProtein', '%s1VII.pdb' % self.path_execute)
            self.ClassColection.setParameter(
                    'Database',
                    '%sDatabase/' % self.ClassColection.getPathAlgorithms('2pg_build_conformation'))

            NumberObjective, Fitness_Energy = self.ClassColection.format_fitness(
                    self.opts.inputFitness)

            self.ClassColection.setParameter('NumberObjective', NumberObjective)
            self.ClassColection.setParameter('Fitness_Energy', Fitness_Energy)

            self.ClassColection.CreateConfigurationFile(self.path_execute)

            self.ClassColection.setCommand('2pg_cartesian', 'protpred-Gromacs-NSGA2')

            config = self.ClassColection.getConfigurationFile('configuration.conf')

            cl = [self.ClassColection.getCommand(), config, '&']

            retProcess = subprocess.Popen(
                cl, 0, stdout=None,  stderr=subprocess.STDOUT, shell=False)
            retCode = retProcess.wait()
            if(retCode != 0):
                self.ClassColection.ShowErrorMessage(
                    "The 2PG framework finished wrong.\nContact the system administrator.")

            self.ClassColection.parse_PDB(
                    self.path_execute,
                    'pop_NON_DOMINATED_%s.pdb' % self.opts.numberGeration,
                    20,
                    'NSGAIISolutions')

            if(self.opts.runMinimization == 'true'):
                self.minimization(
                    self.path_execute,
                    self.ClassColection.getPathGromacs(),
                    "NSGAIISolutions")

            self.build_images()

            path_output, file_output = os.path.split(self.opts.filehtml)

            name, ext = os.path.splitext(self.opts.filehtml)

            htmldir = os.path.join(path_output, '%s_files' % name)

            if not os.path.exists(htmldir):
                os.makedirs(htmldir)

            self.opts.htmlfiledir = htmldir

            result, filesHtml = self.ClassColection.getResultFiles(
                self.path_execute,
                self.opts.toolname,
                'NSGAIISolutions-M')

            self.ClassColection.sendOutputResults(path_output, file_output, result)

            self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, filesHtml)
            self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, [result])

            pdbs = self.ClassColection.listDirectory(self.path_execute, 'NSGAIISolutions-M*.pdb')

            if self.opts.createCompressFile == "True":
                if self.ClassColection.compressFiles(pdbs, self.path_execute, "2PGNSGAII"):
                    path_output, file_output = os.path.split(self.opts.outputZip)
                    self.ClassColection.sendOutputResults(
                            path_output,
                            file_output,
                            os.path.join(self.path_execute, '2PGNSGAII.zip'))

            self.makeHtml()

            if(self.opts.useJmol in ('True', 'true')):
                self.makeHtmlWithJMol(pdbs[0])

            if(self.opts.inputEmail):
                self.ClassColection.SendEmail(
                        'adefelicibus@gmail.com',
                        email,
                        '%s Execution on Galaxy - Cloud USP' % self.opts.toolname,
                        self.ClassColection.getMessageEmail(self.opts.toolname),
                        [],
                        'smtp.gmail.com')

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-g', '--numberGeration', default=None)
    op.add_option('-i', '--inputFasta', default=None)
    op.add_option('-p', '--inputPop', default=None)
    op.add_option('-m', '--howManyRotation', default=None)
    op.add_option('-l', '--rotamerLibrary', default=None)
    op.add_option('-f', '--inputFitness', default=None)
    op.add_option('-w', '--fromFasta', default=None)
    op.add_option('-e', '--inputEmail', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    op.add_option('-k', '--htmlfiledir', default=None)
    op.add_option('-z', '--filehtml', default=None)
    op.add_option('-a', '--createCompressFile', default=None)
    op.add_option('-b', '--outputZip', default=None)
    op.add_option('-x', '--useJmol', default=None)
    op.add_option('-c', '--datasetID', default=None)
    op.add_option('-n', '--runMinimization', default=None)

    opts, args = op.parse_args()

    nsga2 = NSGAII2PG(opts)

    nsga2.ClassColection.setjobStart(datetime.datetime.now())
    nsga2.initTime = datetime.datetime.now()

    cProfile.run('nsga2.run_NSGAII()', 'profileout.txt')

    nsga2.ClassColection.clearPathExecute(nsga2.path_execute)
