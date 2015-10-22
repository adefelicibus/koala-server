#!/usr/bin/env python
# -*- coding: utf-8 -*-

import __main__
__main__.pymol_argv = ['pymol', '-qc']  # Quiet and no GUI

import pymol
import os
from koala import classe
import optparse
import subprocess
import time
import datetime
import urllib2
from PyHighcharts.highcharts.chart import Highchart
from decimal import *
import zipfile
import gzip
import cProfile
import math

pymol.finish_launching()


class SortByFront(object):
    """
    Execute the 2PG Sort By Front Dominance algorithm to classify the PSP methods in Pareto fronts
    """

    path_execute = None
    methods = []
    ignoreoutfiles = ['.pdb', '.png']
    initTime = 0
    endTime = 0
    progname = "SortByFront"

    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.SortByFront.SortByFront
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()

    # def getHistoryID(self):
    #     url = 'http://localhost:8004/api/datasets/%s' % self.opts.datasetID

    #     response = urllib2.urlopen(url)

    #     html = response.read()

    #     html = html.replace(' ', '')
    #     html = html.replace('\n', '')
    #     lines = html.split(",")

    #     for line in lines:
    #         if line.split(':')[0] == '"hid"':
    #             self.hid = line.split(':')[1]
    #             break

    def timenow(self):
        """
        Return current time as a formmated string
        @type self: koala.SortByFront.SortByFront
        """

        return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))

    def buildHighchart(self):
        """
        Create a Highchart chart with the algorithm result
        @type self: koala.SortByFront.SortByFront
        """

        try:
            # Load files
            files = self.ClassColection.listDirectory(self.path_execute, '*.xvg')

            methods = self.methods

            # Objectivies
            obj1 = ""
            obj2 = ""

            x = [[]]*len(files)
            y = [[]]*len(files)

            for i, f in enumerate(files):
                f = os.path.join(self.path_execute, f)
                arq = open(f, "r")

                # Loading File
                x[i] = []
                y[i] = []
                for line in arq:
                    if line.find("#") == -1:
                        x[i].append(float(line.split("\t")[0].strip()))
                        y[i].append(float(line.split("\t")[1]))
                    else:
                        col = line.split("\t")
                        if len(col) > 1:
                            obj1 = col[0].replace('#', ' ')
                            obj2 = col[2]
                arq.close()

            chart = Highchart(renderTo="container2")
            chart.title("Pareto Fronts")
            chart.subtitle(
                "A graph with %s and %s objectivies showing at most four fronts, "
                "but the first as line and the others as scatter"
                % (obj1, obj2))

            graph_options = {
                "xAxis": {
                    "minPadding": 0.05,
                    "maxPadding": 0.1,
                    "title": {
                        'offset': 30,
                        'text': obj1,
                        'rotation': 0,
                    },
                },

                "yAxis": {
                    "minPadding": 0.05,
                    "maxPadding": 0.1,
                    "title": {
                        'offset': 50,
                        'text': obj2,
                        'rotation': -90,
                    },
                },

                "tooltip": {
                    "shared": True,
                    "useHTML": False,
                    # "valueDecimals": 3,
                },

            }

            data = []
            it = {}
            i_file = 0
            context = Context(prec=3, rounding=ROUND_UP)

            if(len(x) > 5):
                fronts = 4
            else:
                fronts = len(x)

            for i in range(fronts):  # no máximo as duas primeiras fronteiras
                data = []
                z = x[i]
                for ii, w in enumerate(z):
                    if(i == 0):
                        it["name"] = methods[i_file]
                        i_file += 1
                    else:
                        it["name"] = "front%d" % i
                    if(not math.isinf(z[ii])):
                        it["x"] = (context.create_decimal_from_float(z[ii])).quantize(
                            Decimal('.2'),
                            rounding=ROUND_UP)
                    else:
                        it["x"] = "0.0"
                    if(not math.isinf(y[i][ii])):
                        it["y"] = (context.create_decimal_from_float(y[i][ii])).quantize(
                            Decimal('.2'),
                            rounding=ROUND_UP)
                    else:
                        it["y"] = "0.0"
                    data.append(it)
                    it = {}

                if(i == 0):
                    chart.add_data_set(data, name="front%d" % i, index=i, marker={"enabled": True})
                else:
                    chart.add_data_set(data, series_type="scatter", name="front%d" % i, index=i)

            chart.set_options(graph_options)
            return chart.generate()

        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error on building highcharts.\n%s" % e)
            # raise Exception("Error while building the Highchart:\n%s" % e)

    def makeHtml(self):
        try:
            pass
            """
            Create an HTML file content to list all the artifacts found in the html_dir
            @type self: koala.SortByFront.SortByFront
            """

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
            html.append('<h1 align="center">Sort By Front Dominance results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Below, there is a graph with the best solutions.<br><br></div>')

            html.append('<div id="container2" style="min-width: 310px; height: 400px; margin: 0 auto">')
            html.append('<script type="text/javascript">')
            html.append(str(self.buildHighchart()))
            html.append('</script></div><br>')

            fhtml = []
            frontFiles = []
            outputfiles = []
            compressedFile = []
            # imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = self.ClassColection.getFileSize(fname, self.opts.htmlfiledir)

                    if e.lower() == ".front":
                        frontFiles.append(fname)
                    # elif e.lower() == ".png":
                    #     imageFiles.append(fname)
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
                        sfsize = self.ClassColection.getFileSize(
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

            html.append(galhtmlpostfix)
            htmlf = file(self.opts.filehtml, 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()
        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error on Create HTML output\n%s" % e)

    def makeHtmlWithJMol(self, pdbReference):
        try:
            """
            Create an HTML file content to list all the artifacts found in the html_dir
            @type self: koala.SortByFront.SortByFront
            """

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
                        script: "set antialiasDisplay;set showtiming;load /datasets/%s/display/%s;cartoons only;color  cartoons structure; spin on"
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
            html.append('<h1 align="center">Sort By Front Dominance results</h1><br></div>')

            html.append('<br>')
            html.append('<div class="sectionmessage">')
            html.append('<br>Below, there is a graph with the best solutions.<br><br></div>')

            html.append('<div id="container2" style="min-width: 310px; height: 400px; margin: 0 auto">')
            html.append('<script type="text/javascript">')
            html.append(str(self.buildHighchart()))
            html.append('</script></div><br>')

            fhtml = []
            frontFiles = []
            outputfiles = []
            compressedFile = []
            # imageFiles = []
            if len(flist) > 0:
                for rownum, fname in enumerate(flist):
                    dname, e = os.path.splitext(fname)
                    sfsize = self.ClassColection.getFileSize(fname, self.opts.htmlfiledir)

                    if e.lower() == ".front":
                        frontFiles.append(fname)
                    # elif e.lower() == ".png":
                    #     imageFiles.append(fname)
                    elif e.lower() in ".zip, .gz":
                        compressedFile.append(fname)
                    elif not e.lower() in self.ignoreoutfiles:
                        outputfiles.append(fname)

            # Arquivos front

            # /datasets/%s/display/

            for front in frontFiles:
                sfsize = self.ClassColection.getFileSize(front, self.opts.htmlfiledir)
                fhtml.append('<tr>')
                fhtml.append(
                    '<td><a href="/datasets/%s/display/%s">%s</a></td>' % (
                        self.opts.datasetID, front, front))
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
                        "'load /datasets/%s/display/%s;cartoons only;color cartoons structure; spin on')"
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

            html.append(galhtmlpostfix)
            htmlf = file("%s.htm" % os.path.join(self.opts.htmlfiledir, self.opts.datasetID), 'w')
            htmlf.write('\n'.join(html))
            htmlf.write('\n')
            htmlf.close()
        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error on CreateHTML with Jmol.\n%s" % e)

    def run_renameAtoms(self, path, path_gromacs):
        """
        Create a subprocess to rename the missing atoms in a PDB file using pdb2gmx
        @type self: koala.SortByFront.SortByFront
        @type path: string
        @type path_gromacs: string
        """

        try:
            cl = [
                '%s/scripts/rename_atoms.py' % self.opts.galaxyroot,
                path,
                path_gromacs,
                '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            pvalue = retProcess.wait()

            if pvalue != 0:
                return False

            return True
        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error on Renaming Atoms.\n%s" % e)
            # raise Exception("Error while renaming atoms.\n%s" % e)

    def run_checkPDB(self, path, path_gromacs):
        """
        Create a subprocess to check the PDB structure using pdb2gmx
        @type self: koala.SortByFront.SortByFront
        @type path: string
        @type path_gromacs: string
        """

        try:
            cl = [
                '%s/scripts/check_structures_gromacs.py' % self.opts.galaxyroot,
                path,
                path_gromacs,
                '&']

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
            self.ClassColection.ShowErrorMessage(
                "Error on Checking PDBs.\n%s" % e)
            # raise Exception("Error while checking PDBs:\n%s" % e)

    def getBetterPDBs(self, path):
        """
        Get the methods that have been classified on the two first fronts
        @type self: koala.SortByFront.SortByFront
        """

        try:
            front = self.ClassColection.listDirectory(path, "*.front")
            if len(front) > 1:
                raise Exception("There is more than one .front file.\n")

            if len(front) == 0:
                raise Exception("There is no .front file.\n")

            for l in file(front[0], 'r'):
                ln = l.split("\n")
                if not ln[0].startswith('#', 0, 1):
                    ll = ln[0].split("\t")
                    if(int(ll[1]) < 2):  # ll[1] = fronteira fronteiras 0 e 1
                        self.methods.append(ll[6].strip())  # ll[6] = metodo

        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error on getBetterPDBs.\n%s" % e)
            # raise Exception("Error on getBetterPDBs.\n%s" % e)

    def build_images(self):
        """
        Build images from PDB files using PyMol package.
        @type self: koala.SortByFront.SortByFront
        """

        try:
            path = self.path_execute

            self.getBetterPDBs(path)

            limit = 20
            if len(self.methods) < 20:
                limit = len(self.methods)

            # for pdb in self.methods:

            for i in range(0, limit):

                pdb = self.methods[i]
                arq = os.path.join(path, pdb)

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

                time.sleep(0.25)  # (in seconds)

                pymol.cmd.reinitialize()

        except Exception, e:
            self.ClassColection.ShowErrorMessage(
                "Error when build images.\n%s" % e)

    def run_SortByFront(self):
        """
        Run the 2PG Sort algorithm to calculate the Pareto fronts and sorting
        @type self: koala.SortByFront.SortByFront
        """

        dir_execucao = self.ClassColection.CreateExecutionDirectory()
        self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

        self.ClassColection.CopyNecessaryFiles(self.path_execute)

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

        NumberObjective, Fitness_Energy = self.ClassColection.format_fitness(self.opts.inputFitness)

        self.ClassColection.setParameter('NumberObjective', NumberObjective)
        self.ClassColection.setParameter('Fitness_Energy', Fitness_Energy)

        self.ClassColection.CreateConfigurationFile(self.path_execute)

        config = self.ClassColection.getConfigurationFile('configuration.conf')

        if self.opts.compressedFile == '1':

            inputFiles = self.opts.inputPDBs.split(",")

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
                        self.opts.inputPDBs)

        if(self.opts.renameAtoms == 'true'):
            if not self.run_renameAtoms(
                                            self.path_execute,
                                            self.ClassColection.getParameterValue(
                                                    'Path_Gromacs_Programs')):
                raise Exception("The script to rename the atoms finished wrong.")

        if(self.opts.checkStructures == 'true'):
            if not self.run_checkPDB(
                                        self.path_execute,
                                        self.ClassColection.getParameterValue(
                                            'Path_Gromacs_Programs')):
                raise Exception("The script to check the structure finished wrong.")

        self.ClassColection.setCommand(
                                            '2pg_cartesian',
                                            'protpred-Gromacs-Sort_Method_Files_by_Front_Dominance')

        cl = [self.ClassColection.getCommand(), config, '&']

        retProcess = subprocess.Popen(
            cl, 0, stdout=None,  stderr=None, shell=False)
        retCode = retProcess.wait()
        if(retCode != 0):
            self.ClassColection.ShowErrorMessage(
                "The 2PG framework finished wrong.\nContact the system administrator.")

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

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputPDBs', default=None)
    op.add_option('-f', '--inputFitness', default=None)
    op.add_option('-k', '--htmlfiledir', default=None)
    op.add_option('-z', '--filehtml', default=None)
    op.add_option('-n', '--inputnames', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-g', '--galaxyroot', default=None)
    op.add_option('-a', '--datasetID', default=None)
    op.add_option('-s', '--compressedFile', default=None)
    op.add_option('-x', '--useJmol', default=None)
    op.add_option('-y', '--checkStructures', default=None)
    op.add_option('-b', '--renameAtoms', default=None)
    opts, args = op.parse_args()

    os.chdir(opts.galaxyroot)

    if not os.path.exists(opts.htmlfiledir):
        os.makedirs(opts.htmlfiledir)

    sort = SortByFront(opts)

    sort.ClassColection.setjobStart(datetime.datetime.now())
    sort.initTime = datetime.datetime.now()

    cProfile.run('sort.run_SortByFront()', 'profileout.txt')

    sort.ClassColection.clearPathExecute(sort.path_execute)
