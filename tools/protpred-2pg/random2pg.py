#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
import subprocess
import datetime
import cProfile

from koala.utils import get_file_size, show_error_message, list_directory, compress_files
from koala.utils import TimeJobExecution, copy_necessary_files, validate_email
from koala.utils.output import send_output_files_html, get_result_files, build_images
from koala.utils.output import send_output_results
from koala.utils.path import PathRuns, clear_path_execute, get_path_gromacs, get_path_algorithms
from koala.utils.input import create_local_fasta_file, create_local_pop_file
from koala.utils.input import create_configuration_file
from koala.frameworks.params import Params
from koala.utils.scripts import check_pdb, prepare_pdb, residue_renumber, minimization
from koala.utils.mail import send_email, get_message_email
from koala.utils.pdb import parse_pdb


class Random2PG(object):
    """
    Execute the 2PG Random evolutionary algorithm.
    """

    progname = "2PG Random"
    opts = None
    sequence = None
    initTime = 0
    endTime = 0
    ignoreoutfiles = ['.pdb']

    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.Random2PG.Random2PG
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts

        self.time_execution = TimeJobExecution()
        self.path_runs = PathRuns()
        self.framework = Params('2PG')

    def makeHtml(self):
        """ Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.Random2PG.Random2PG
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
            flist.sort()
            html = []
            html.append(galhtmlprefix % self.progname)
            html.append('<div class="sucessmessage">')
            html.append('<br>')
            html.append('<h1 align="center">2PG Random Ab Initio Algorithm results</h1><br></div>')

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
                    sfsize = get_file_size(fname, self.opts.htmlfiledir)

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
                sfsize = get_file_size(fit, self.opts.htmlfiledir)
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
            listaArquivosPdb = list_directory(
                        self.path_runs.get_path_execution(),
                        'randomSolution-M*.pdb')

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
                        '<td><a href="%s.png"><img src="%s.png" '
                        'title="Click to see %s.png bigger" width="130"/></a></td>'
                        % (pdbName, pdbName, pdbName))
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
                        pdbName, ext = os.path.splitext(listaArquivosPdb[idx])
                        fhtml.append(
                            '<td><a href="%s.png"><img src="%s.png" '
                            'title="Click to see %s.png bigger" width="130"/></a></td>'
                            % (pdbName, pdbName, pdbName))
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
                    pdbName, ext = os.path.splitext(listaArquivosPdb[idx])
                    fhtml.append(
                        '<td><a href="%s.png"><img src="%s.png" '
                        'title="Click to see %s.png bigger" width="130"/></a></td>'
                        % (pdbName, pdbName, pdbName))
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
            html.append('')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file(self.opts.filehtml, 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()

        except Exception, e:
            show_error_message("Error on makeHtml:\n%s" % str(e))

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

                    var jmolApplet0;

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
            html.append('<h1 align="center">2PG Random Ab Initio Algorithm results</h1><br></div>')

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
                    sfsize = get_file_size(fname, self.opts.htmlfiledir)

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
                sfsize = get_file_size(fit, self.opts.htmlfiledir)
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
            listaArquivosPdb = list_directory(
                        self.path_runs.get_path_execution(),
                        'randomSolution-M*.pdb')

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
                            '<td><a href="/datasets/%s/display/%s">%s</a></td>'
                            % (
                                self.opts.datasetID, listaArquivosPdb[idx], listaArquivosPdb[idx]))
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
            html.append('')
            html.append('<br></div>')

            html.append(galhtmlpostfix)
            htmlf = file("%s.htm" % os.path.join(self.opts.htmlfiledir, self.opts.datasetID), 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()

        except Exception, e:
            show_error_message("Error on makeHtmlWithJMol:\n%s" % str(e))

    def do_minimization(self, pdbPrefix=''):
        if not check_pdb(self.path_runs.get_path_execution(), self.opts.galaxyroot):
            raise Exception("The script to check the PDBs finished wrong.")

        if not prepare_pdb(self.path_runs.get_path_execution(), self.opts.galaxyroot):
            raise Exception("The script to prepare the PDBs finished wrong.")

        if not residue_renumber(
                self.path_runs.get_path_execution(), self.opts.galaxyroot):
            raise Exception("The script to renumber the residues finished wrong.")

        if not minimization(
                self.path_runs.get_path_execution(), self.opts.galaxyroot, pdbPrefix):
            raise Exception("The script of minimization finished wrong.")

    def run_Random(self):
        """
        Create the 2PG Random configuration file and begin the execution.

        @type self: koala.Random2PG.Random2PG
        """

        try:
            self.path_runs.set_path_execute()
            if self.opts.inputEmail:
                email = validate_email(self.opts.inputEmail)
                self.path_runs.set_execution_directory(email)
            else:
                self.path_runs.set_execution_directory()

            self.sequence = create_local_fasta_file(
                    self.path_runs.get_path_execution(),
                    self.opts.fromFasta,
                    self.opts.inputFasta,
                    self.opts.toolname,
                    self.framework)

            SizePopulation = create_local_pop_file(
                    self.path_runs.get_path_execution(),
                    self.opts.inputPop,
                    self.framework)

            if SizePopulation > 1:
                show_error_message(
                    "Error: The population file must contain only one model")

            copy_necessary_files(
                self.path_runs.get_path_execute(),
                self.path_runs.get_path_execution(),
                self.framework.get_framework())

            self.framework.set_parameter(
                'rotamer_library', self.opts.rotamerLibrary)
            self.framework.set_parameter(
                'StepNumber', self.opts.stepNumber)
            self.framework.set_parameter(
                'How_Many_Rotation', self.opts.howManyRotation)
            self.framework.set_parameter(
                'force_field', self.opts.forceField)
            self.framework.set_parameter(
                    'SequenceAminoAcidsPathFileName',
                    self.path_runs.get_path_execution() + 'fasta.txt')
            self.framework.set_parameter(
                'Local_Execute', self.path_runs.get_path_execution())
            self.framework.set_parameter(
                    'Path_Gromacs_Programs',
                    get_path_gromacs())
            self.framework.set_parameter(
                'NativeProtein', '%s1VII.pdb' % self.path_runs.get_path_execution())
            self.framework.set_parameter(
                    'Database',
                    '%s/Database/' %
                    get_path_algorithms('2pg_build_conformation'))

            create_configuration_file(
                self.path_runs.get_path_execution(), self.framework)

            self.framework.set_command(
                self.path_runs.get_path_execution(),
                'protpred-Gromacs-Random_Algorithm')

            config = 'configuration.conf'

            cl = [self.framework.get_command(), config, '&']

            retProcess = subprocess.Popen(
                cl, 0, stdout=None,  stderr=subprocess.STDOUT, shell=False)
            retCode = retProcess.wait()
            if(retCode != 0):
                show_error_message(
                    "The 2PG framework finished wrong.\nContact the system administrator.")

            parse_pdb(
                    self.path_runs.get_path_execution(),
                    'random_algorithm_solutions.pdb',
                    20,
                    'randomSolution')

            if(self.opts.runMinimization == 'true'):
                self.do_minimization("randomSolution")

            pdbs = list_directory(
                self.path_runs.get_path_execution(), 'randomSolution-M*.pdb')

            build_images(pdbs, self.path_runs.get_path_execution())

            path_output, file_output = os.path.split(self.opts.filehtml)

            name, ext = os.path.splitext(self.opts.filehtml)

            htmldir = os.path.join(path_output, '%s_files' % name)

            if not os.path.exists(htmldir):
                os.makedirs(htmldir)

            self.opts.htmlfiledir = htmldir

            result, filesHtml = get_result_files(
                    self.path_runs.get_path_execution(),
                    self.opts.toolname,
                    'randomSolution-M')

            send_output_files_html(self.opts.htmlfiledir, filesHtml)
            send_output_files_html(self.opts.htmlfiledir, [result])

            if self.opts.createCompressFile == "True":
                if compress_files(pdbs, self.path_runs.get_path_execution(), "2PGRandom"):
                    path_output, file_output = os.path.split(self.opts.outputZip)
                    send_output_results(
                            path_output,
                            file_output,
                            os.path.join(self.path_runs.get_path_execution(), '2PGRandom.zip'))

            self.makeHtml()

            if(self.opts.useJmol in ('True', 'true')):
                self.makeHtmlWithJMol(pdbs[0])

            if(self.opts.inputEmail):
                send_email(
                        'adefelicibus@gmail.com',
                        email,
                        '%s Execution on Galaxy - Cloud USP' % self.opts.toolname,
                        get_message_email(self.opts.toolname),
                        [],
                        'smtp.gmail.com')

        except Exception, e:
            show_error_message(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputFasta', default=None)
    op.add_option('-p', '--inputPop', default=None)
    op.add_option('-s', '--stepNumber', default=None)
    op.add_option('-m', '--howManyRotation', default=None)
    op.add_option('-a', '--rotamerLibrary', default=None)
    op.add_option('-f', '--forceField', default=None)
    op.add_option('-w', '--fromFasta', default=None)
    op.add_option('-o', '--filehtml', default=None)
    op.add_option('-d', '--htmlfiledir', default=None)
    op.add_option('-e', '--inputEmail', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    op.add_option('-b', '--createCompressFile', default=None)
    op.add_option('-c', '--outputZip', default=None)
    op.add_option('-x', '--useJmol', default=None)
    op.add_option('-g', '--datasetID', default=None)
    op.add_option('-n', '--runMinimization', default=None)

    opts, args = op.parse_args()

    random = Random2PG(opts)

    random.time_execution.set_job_start(datetime.datetime.now())
    random.initTime = datetime.datetime.now()

    cProfile.run('random.run_Random()', 'profileout.txt')

    clear_path_execute(random.path_runs.get_path_execution())
