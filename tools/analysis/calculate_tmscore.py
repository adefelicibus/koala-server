#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
import datetime
from decimal import *
from collections import OrderedDict
import zipfile
import gzip
import cProfile

from koala.utils import get_file_size, list_directory, show_warning_message, show_error_message
from koala.utils import extract_zip_file, extract_gz_file, TimeJobExecution
from koala.utils.input import copy_pdb_reference
from koala.utils.output import send_output_files_html, get_result_files, build_images
from koala.utils.path import PathRuns, clear_path_execute
from koala.utils.input import copy_pdbs_from_input


class CalculateTMScore(object):
    """
    Calculate the TM-Score value from a set of PDB files using TM-Score program
    """

    methods = []
    ignoreoutfiles = ['.pdb']
    initTime = 0
    endTime = 0
    tmscore_value = None
    command = None

    progname = "CalculateTMScore"

    def __init__(self, opts=None):
        """
        @type self: koala.CalculateTMScore.CalculateTMScore
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts

        self.time_execution = TimeJobExecution()
        self.path_runs = PathRuns()

        self.command = "@PATH@./TMscore @NATIVE@ @MODEL@ -o TM.sup > \
    @PATHEXECUTE@@NAMENATIVE@_@NAMEMODEL@.txt"

    def buildTMScoreTable(self):
        """
        Create an HTML table with the calculated TM-Score values
        @type self: koala.CalculateTMScore.CalculateTMScore
        """
        try:
            html = ''
            for key, value in self.tmscore_value.items():
                html += '<tr>'
                html += '<td>%s</td>' % str(key)  # PDBFile
                html += '<td align="center">%s</td>' % str(value)  # TMScore
                html += '</tr>'
            return html
        except Exception, e:
            show_error_message("Error while buildTMScoreTable:\n%s" % e)

    def makeHtml(self):
        """
        Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.CalculateTMScore.CalculateTMScore
        """

        try:
            galhtmlprefix = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <meta name="generator" content="Galaxy %s tool output" />
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
            html.append('<h1 align="center">TM-Score results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Below, there is a table with the TM-Score values.<br><br></div>')

            html.append('<div class="filetables">')
            html.append('<table border="1"><tr><th>Model</th><th>TM-Score</th></tr>\n')
            html.append(str(self.buildTMScoreTable()))
            html.append('</table></div><br/>')

            fhtml = []
            frontFiles = []
            outputfiles = []
            compressedFile = []
            imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = get_file_size(fname, self.opts.htmlfiledir)

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
                sfsize = get_file_size(front, self.opts.htmlfiledir)
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
                    sfsize = get_file_size(
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
                        sfsize = get_file_size(
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
                    sfsize = get_file_size(
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
                sfsize = get_file_size(output, self.opts.htmlfiledir)
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
                sfsize = get_file_size(output, self.opts.htmlfiledir)
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

            self.time_execution.set_job_end(datetime.datetime.now())
            self.endTime = datetime.datetime.now()

            dif = self.time_execution.calculate_time_execution()

            html.append('<div>Time execution:<br>')
            html.append('Start: %s<br>' %
                        self.time_execution.get_job_start().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('End: %s<br>' %
                        self.time_execution.get_job_end().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('Total time: ~%dh:%dm:%ds' % (dif[0], dif[1], dif[2]))
            html.append('</div>')

            html.append('<hr>')
            html.append('<div>Citation<br>')
            html.append('Please, cite the used algorithm in this tool:<br><br>')
            html.append('Y. Zhang, J. Skolnick, Scoring function for automated '
                        'assessment of protein structure template quality, '
                        'Proteins, 57: 702-710. 2004.')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file(self.opts.filehtml, 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()
        except Exception, e:
            show_error_message("Error while makeHtml:\n%s" % e)

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
            <meta name="generator" content="Galaxy %s tool output" />
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

                    Jmol.getProfile()
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
                        script: "set antialiasDisplay;set showtiming; \
                        load async /datasets/%s/display/%s;cartoons only; \
                        color  cartoons structure; spin on"
                        //,defaultModel: ":dopamine"
                        //,noscript: true
                        //console: "none", // default will be jmolApplet0_infodiv
                        //script: "set antialiasDisplay;background white;load data/caffeine.mol;"
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
            html.append('<h1 align="center">TM-Score results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Below, there is a table with the TM-Score values.<br><br></div>')

            html.append('<div class="filetables">')
            html.append('<table border="1"><tr><th>Model</th><th>TM-Score</th></tr>\n')
            html.append(str(self.buildTMScoreTable()))
            html.append('</table></div><br/>')

            fhtml = []
            frontFiles = []
            outputfiles = []
            compressedFile = []
            imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = get_file_size(fname, self.opts.htmlfiledir)

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
                sfsize = get_file_size(front, self.opts.htmlfiledir)
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
                    sfsize = get_file_size(
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
                        "'load /datasets/%s/display/%s;cartoons only; \
                        color  cartoons structure; spin on')"
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
                                self.opts.datasetID,
                                listaArquivosPdb[idx],
                                listaArquivosPdb[idx]))
                        idx += 1
                    idx = idx_linha
                    fhtml.append('</tr><tr>')
                    for i in range(start, end):
                        sfsize = get_file_size(
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
                            "'load /datasets/%s/display/%s;cartoons only; \
                            color cartoons structure; spin on')"
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
                    sfsize = get_file_size(
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
                        "'load /datasets/%s/display/%s;cartoons only; \
                        color cartoons structure; spin on')"
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
                sfsize = get_file_size(output, self.opts.htmlfiledir)
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
                sfsize = get_file_size(output, self.opts.htmlfiledir)
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

            self.time_execution.set_job_end(datetime.datetime.now())
            self.endTime = datetime.datetime.now()

            dif = self.time_execution.calculate_time_execution()

            html.append('<div>Time execution:<br>')
            html.append('Start: %s<br>' %
                        self.time_execution.get_job_start().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('End: %s<br>' %
                        self.time_execution.get_job_end().strftime("%d/%m/%Y %H:%M:%S"))
            html.append('Total time: ~%dh:%dm:%ds' % (dif[0], dif[1], dif[2]))
            html.append('</div>')

            html.append('<hr>')
            html.append('<div>Citation<br>')
            html.append('Please, cite the used algorithm in this tool:<br><br>')
            html.append('Y. Zhang, J. Skolnick, Scoring function for automated '
                        'assessment of protein structure template quality, '
                        'Proteins, 57: 702-710. 2004.')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file("%s.htm" % os.path.join(self.opts.htmlfiledir, self.opts.datasetID), 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()
        except Exception, e:
            show_error_message("Error while makeHtmlWithJMol:\n%s" % e)

    def getTMScoreValues(self):
        """
        Calculate the TM-Score value to the input PDB files
        @type self: koala.CalculateTMScore.CalculateTMScore
        """

        try:

            pdbs = list_directory(self.path_runs.get_path_execution(), "*.pdb")

            if not pdbs:
                raise "getTMScoreValues: No PDB file found.\n"

            dict_tmscore = {}
            for pdb in pdbs:
                if not (pdb == self.opts.inputPDBRefName):

                    name_pdb, ext = os.path.splitext(pdb)
                    name_reference, ext = os.path.splitext(self.opts.inputPDBRefName)

                    aux_command = self.command.replace(
                        "@PATH@",
                        self.path_runs.get_path_execute()).replace(
                            "@MODEL@",
                            (os.path.join(self.path_runs.get_path_execution(), pdb))).replace(
                                "@NATIVE@",
                                (os.path.join(
                                    self.path_runs.get_path_execution(),
                                    self.opts.inputPDBRefName)))
                    aux_command = aux_command.replace(
                        "@PATHEXECUTE@",
                        self.path_runs.get_path_execution()).replace(
                            "@NAMEMODEL@",
                            name_pdb).replace(
                                "@NAMENATIVE@",
                                name_reference)

                    os.system(aux_command)  # TODO: USAR SUBPROCESS

                    os.chdir(self.path_runs.get_path_execution())

                    result_file = name_reference + '_' + name_pdb + '.txt'

                    temp_tmscore = open(result_file, "r")
                    for line in temp_tmscore.readlines():
                        if line.startswith("TM-score"):
                            tmscore_value = line.split("=", 1)[1].strip()
                            only_pdb_file_name = os.path.basename(pdb)
                            dict_tmscore[only_pdb_file_name] = tmscore_value
                    temp_tmscore.close()

            return OrderedDict(sorted(dict_tmscore.items(), key=lambda x: x[1], reverse=True))

        except Exception, e:
            show_error_message("Erro on getTMScoreValues method:\n%s" % e)

    def run_CalculateTMscore(self):
        """
        Get the PDB input files and run the calculation
        @type self: koala.CalculateTMScore.CalculateTMScore
        """
        try:
            self.path_runs.set_execution_directory()

            if self.opts.compressedFile == '1':

                inputFiles = self.opts.inputPdbs.split(",")

                for input_f in inputFiles:
                    if zipfile.is_zipfile(input_f):
                        extract_zip_file(input_f, self.path_runs.get_path_execution())
                    else:
                        try:
                            inF = gzip.GzipFile(input_f, 'rb')
                            f = inF.read()
                            inF.close()
                            if f:
                                extract_gz_file(input_f, self.path_runs.get_path_execution())
                        except Exception, e:
                            raise Exception("The input file could not be read.\n%s" % e)
            else:
                    copy_pdbs_from_input(
                        self.path_runs.get_path_execution(),
                        self.opts.htmlfiledir,
                        self.opts.inputnames,
                        self.opts.inputPdbs)

            copy_pdb_reference(
                self.opts.htmlfiledir,
                self.path_runs.get_path_execution(),
                self.opts.inputPDBRefName,
                self.opts.inputPDBRef
            )

            self.tmscore_value = self.getTMScoreValues()

            if(len(self.tmscore_value) == 0):
                show_warning_message(
                    "There is no common residues in the input structures")
            else:
                for key, value in self.tmscore_value.items():
                    self.methods.append(key)

                build_images(self.methods, self.path_runs.get_path_execution())

                pdbsToCopy = [os.path.join(
                    self.path_runs.get_path_execution(), method) for method in self.methods]
                send_output_files_html(self.opts.htmlfiledir, pdbsToCopy)

                result, filesHtml = get_result_files(
                    self.path_runs.get_path_execution(), self.opts.toolname)

                send_output_files_html(self.opts.htmlfiledir, filesHtml)

                self.makeHtml()

                if(self.opts.useJmol == 'true'):
                    self.makeHtmlWithJMol(pdbsToCopy[0].split('/')[-1])

        except Exception, e:
            show_error_message("Erro on run_CalculateTMscore method:\n%s" % e)

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
    opts, args = op.parse_args()

    if not os.path.exists(opts.htmlfiledir):
        os.makedirs(opts.htmlfiledir)

    calctm = CalculateTMScore(opts)

    calctm.time_execution.set_job_start(datetime.datetime.now())
    calctm.initTime = datetime.datetime.now()

    cProfile.run('calctm.run_CalculateTMscore()', 'profileout.txt')

    clear_path_execute(calctm.path_runs.get_path_execution())
