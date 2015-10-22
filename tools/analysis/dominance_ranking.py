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

pymol.finish_launching()


class DominanceRanking(object):
    """
    Calculate the Dominance Ranking of Protein Structure Prediction methods
    """

    path_execute = None
    methods = []
    headers = []
    ordered_headers = None
    data = []
    ignoreoutfiles = ['.pdb']
    initTime = 0
    endTime = 0
    combinations = None
    progname = "DominanceRanking"

    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.DominanceRanking.DominanceRanking
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
        @type self: koala.DominanceRanking.DominanceRanking
        """

        return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))

    def getfSize(self, fpath, outpath):
        """
        Get the file size and return as string
        @type self: koala.DominanceRanking.DominanceRanking
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

    def build_Highchart(self, objectivies, container="container"):
        """
        Create a Highchart chart with the algorithm result
        @type self: koala.DominanceRanking.DominanceRanking
        @type objectivies: string
        @type container: string
        """
        try:
            # Load files
            objs = objectivies.split(",")
            print objs
            files = self.ClassColection.listDirectory(
                    self.path_execute, '*%s_%s*.xvg' % (objs[0], objs[1]))
            images = self.methods

            print files

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
                arq.close()

            print 'criou x e y'

            chart = Highchart(renderTo=container)
            chart.title("Pareto Fronts")
            chart.subtitle("A graph with %s and %s objectivies" % (objs[0], objs[1]))

            graph_options = {
                "xAxis": {
                    "minPadding": 0.05,
                    "maxPadding": 0.1,
                    "title": {
                        'offset': 30,
                        'text': objs[0],
                        'rotation': 0,
                    },
                },

                "yAxis": {
                    "minPadding": 0.05,
                    "maxPadding": 0.1,
                    "title": {
                        'offset': 50,
                        'text': objs[1],
                        'rotation': -90,
                    },
                },

                "tooltip": {
                    "shared": True,
                    "useHTML": False,
                    "valueDecimals": 3,
                },
            }

            print 'criou graph options'

            data = []
            it = {}
            i_file = 0
            context = Context(prec=3, rounding=ROUND_UP)

            if(len(x) >= 4):
                fronts = 4
            else:
                # fronts = 2
                fronts = len(x)

            print 'definiu fronts ', fronts

            for i in range(fronts):
                data = []
                z = x[i]
                for ii, w in enumerate(z):
                    if(i_file < len(images)):
                        it["name"] = images[i_file]
                        i_file += 1
                    else:
                        it["name"] = "front%d" % i
                    it["x"] = (context.create_decimal_from_float(z[ii])).quantize(
                            Decimal('.1'),
                            rounding=ROUND_UP)
                    it["y"] = (context.create_decimal_from_float(y[i][ii])).quantize(
                            Decimal('.1'),
                            rounding=ROUND_UP)
                    data.append(it)
                    it = {}

                if(i == 0):
                    chart.add_data_set(data, name="front%d" % i, index=i, marker={"enabled": True})
                else:
                    chart.add_data_set(data, series_type="scatter", name="front%d" % i, index=i)

            chart.set_options(graph_options)
            return chart.generate()

        except Exception, e:
            raise Exception("Error while building the Highchart:\n%s" % e)

    def buildDominanceRankingTable(self):
        """
        Create an HTML table with the calculated dominance ranking
        @type self: koala.DominanceRanking.DominanceRanking
        """

        try:
            html = ''
            for i in range(len(self.ordered_headers)):
                html += '<tr>'
                html += '<td>%s</td>' % self.ordered_headers[i][0]  # PDBFile
                html += '<td align="center">%s</td>' % self.ordered_headers[i][1]  # Dominance
                html += '<td align="center">%s</td>' % self.ordered_headers[i][2]  # Wins
                html += '<td align="center">%s</td>' % self.ordered_headers[i][3]  # Loses
                wins = float(self.ordered_headers[i][2])
                loses = float(self.ordered_headers[i][3])
                soma = wins + loses
                divisao = round(float(wins / soma) * 100, 2)
                html += '<td align="center">%s %%</td>' % str(divisao)  # %
            return html
        except Exception, e:
            raise e

    def makeHtml(self):
        """
        Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.DominanceRanking.DominanceRanking
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
        html.append('<br>')
        html.append('<div class="sucessmessage">')
        html.append('<br>')
        html.append('<h1 align="center">Dominance Ranking results</h1><br></div>')

        html.append('<br>')
        html.append('<div class="sectionmessage">')
        html.append(
            '<br>Below, there is a table with the result of dominance ranking.<br><br></div>')

        html.append('<div class="filetables">')
        html.append('<table border="1">'
                    '<tr>'
                    '<th>Model</th>'
                    '<th>Dominance</th>'
                    '<th>Wins</th>'
                    '<th>Loses</th>'
                    '<th>Percentage Wins</th>'
                    '</tr>\n')
        html.append(str(self.buildDominanceRankingTable()))
        html.append('</table></div><br/>')

        html.append('<br>')
        html.append('<div class="sectionmessage">')
        html.append(
            '<br> A graph with the best solutions for each objectivies combination.<br><br></div>')

        for i, fit in enumerate(self.combinations):
            html.append(
                '<div id="container%s" style="min-width: '
                '310px; height: 400px; margin: 0 auto">' % i)
            html.append('<script type="text/javascript">')
            html.append(str(self.build_Highchart(fit, "container%s" % i)))
            html.append('</script></div><br>')

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

        html.append(galhtmlpostfix)
        htmlf = file(self.opts.filehtml, 'w')
        htmlf.write('\n'.join(html))
        htmlf.write('\n')
        htmlf.close()

    def makeHtmlWithJMol(self, pdbReference):
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
        html.append('<br>')
        html.append('<div class="sucessmessage">')
        html.append('<br>')
        html.append('<h1 align="center">Dominance Ranking results</h1><br></div>')

        html.append('<br>')
        html.append('<div class="sectionmessage">')
        html.append(
            '<br>Below, there is a table with the result of dominance ranking.<br><br></div>')

        html.append('<div class="filetables">')
        html.append('<table border="1">'
                    '<tr>'
                    '<th>Model</th>'
                    '<th>Dominance</th>'
                    '<th>Wins</th>'
                    '<th>Loses</th>'
                    '<th>Percentage Wins</th>'
                    '</tr>\n')
        html.append(str(self.buildDominanceRankingTable()))
        html.append('</table></div><br/>')

        html.append('<br>')
        html.append('<div class="sectionmessage">')
        html.append(
            '<br> A graph with the best solutions for each objectivies combination.<br><br></div>')

        for i, fit in enumerate(self.combinations):
            html.append(
                '<div id="container%s" style="min-width: '
                '310px; height: 400px; margin: 0 auto">' % i)
            html.append('<script type="text/javascript">')
            html.append(str(self.build_Highchart(fit, "container%s" % i)))
            html.append('</script></div><br>')

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

        html.append(galhtmlpostfix)
        htmlf = file("%s.htm" % os.path.join(self.opts.htmlfiledir, self.opts.datasetID), 'w')
        htmlf.write('\n'.join(html))
        htmlf.write('\n')
        htmlf.close()

    def run_renameAtoms(self, path, path_gromacs):
        """
        Create a subprocess to rename the missing atoms in a PDB file using pdb2gmx
        @type self: koala.DominanceRanking.DominanceRanking
        @type path: string
        @type path_gromacs: string
        """

        try:
            cl = [
                '%s/scripts/rename_atoms.py' % self.opts.galaxyroot, path, path_gromacs,
                '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            pvalue = retProcess.wait()

            if pvalue != 0:
                return False

            return True
        except Exception, e:
            raise Exception("Error while renaming atoms.\n%s" % e)

    def run_checkPDB(self, path, path_gromacs):
        """
        Create a subprocess to check the PDB structure using pdb2gmx
        @type self: koala.DominanceRanking.DominanceRanking
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
            raise Exception("Error while checking PDBs:\n%s" % e)

    def getBetterPDBs(self):
        """
        Get the methods that has positive dominance
        @type self: koala.DominanceRanking.DominanceRanking
        """

        try:
            for i in range(len(self.ordered_headers)):
                # add only the methods that has positive dominance
                if self.ordered_headers[i][1] > 0:
                    self.methods.append(self.ordered_headers[i][0])

        except Exception, e:
            raise Exception("Error on getBetterPDBs.\n%s" % e)

    def build_images(self):
        """
        Build images from PDB files using PyMol package.
        @type self: koala.DominanceRanking.DominanceRanking
        """

        try:
            path = self.path_execute
            self.getBetterPDBs()
            for pdb in self.methods:
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
            raise e

    def build_rankingDominance(self):
        """
        Create the 2PG Sort configuration file and build the dominance
        @type self: koala.DominanceRanking.DominanceRanking
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

        self.combinations = self.ClassColection.format_fitness(
                self.opts.inputFitness, self.opts.toolname)

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
                    self.ClassColection.getParameterValue('Path_Gromacs_Programs')):
                raise Exception("The script to rename the atoms finished wrong.")

        if(self.opts.checkStructures == 'true'):
            if not self.run_checkPDB(
                    self.path_execute,
                    self.ClassColection.getParameterValue('Path_Gromacs_Programs')):
                raise Exception("The script to check the structure finished wrong.")

        self.ClassColection.setCommand(
                '2pg_cartesian',
                'protpred-Gromacs-Sort_Method_Files_by_Front_Dominance')

        for fit in self.combinations:
            self.run_SortByFront(fit)

        self.CreateDominanceMatrix()

    def run_SortByFront(self, fitness):
        """
        Run the 2PG Sort algorithm for each objectivies combinations
        @type self: koala.DominanceRanking.DominanceRanking
        @type fitness: string
        """

        NumberObjective, Fitness_Energy = self.ClassColection.format_fitness(fitness)

        self.ClassColection.setParameter('NumberObjective', NumberObjective)
        self.ClassColection.setParameter('Fitness_Energy', Fitness_Energy)

        self.ClassColection.CreateConfigurationFile(self.path_execute)

        config = self.ClassColection.getConfigurationFile('configuration.conf')

        cl = [self.ClassColection.getCommand(), config, '&']

        retProcess = subprocess.Popen(
            cl, 0, stdout=None,  stderr=subprocess.STDOUT, shell=False)
        retCode = retProcess.wait()
        if(retCode != 0):
            self.ClassColection.ShowErrorMessage(
                "The 2PG framework finished wrong.\n"
                "Try to check and rename the PDB input files or contact the system administrator.")

    def SortMatrix(self):
        """
        Sort the dominance ranking matrix by dominance
        @type self: koala.DominanceRanking.DominanceRanking
        """
        self.ordered_headers = sorted(self.headers, key=lambda score: score[1], reverse=True)

    def CalculateDominance(self):
        """
        Calculate the Dominance of the PSP methods
        @type self: koala.DominanceRanking.DominanceRanking
        """

        # Faz diferença se a matriz está ordenada?
        # percorre todas as linhas da matriz
        for i in range(len(self.data)):
            # para cada header percorre todas as colunas da linha
            for h in range(len(self.headers)-1):
                # percorre todas as colunas da matriz
                for j in range(h, len(self.data[i])-1):
                    if float(self.data[i][h]) < float(self.data[i][j + 1]):

                        self.headers[h][1] = self.headers[h][1] + 1
                        self.headers[j+1][1] = self.headers[j+1][1] - 1

                        self.headers[h][2] = self.headers[h][2] + 1
                        self.headers[j+1][3] = self.headers[j+1][3] + 1
                    else:

                        self.headers[j+1][1] = self.headers[j+1][1] + 1
                        self.headers[h][1] = self.headers[h][1] - 1

                        self.headers[h][3] = self.headers[h][3] + 1
                        self.headers[j+1][2] = self.headers[j+1][2] + 1

        self.SortMatrix()
        self.build_images()

        pdbsToCopy = [os.path.join(self.path_execute, method) for method in self.methods]
        self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, pdbsToCopy)

        result, filesHtml = self.ClassColection.getResultFiles(
                self.path_execute,
                self.opts.toolname)

        self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, filesHtml)
        self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, [result])

    def CreateDominanceMatrix(self):
        """
        Create a text file with the dominance ranking matrix
        @type self: koala.DominanceRanking.DominanceRanking
        """

        try:
            front = self.ClassColection.listDirectory(self.path_execute, "*.front")

            if len(front) == 0:
                raise Exception("There is no .front file.\n")

            objectivies = [[]]*len(front)
            ranking = [[]]*len(front)
            methods = [[]]*len(front)
            values = {}

            # matriz to be used on dominance ranking
            temp = []

            for i, f in enumerate(front):
                f = os.path.join(self.path_execute, f)
                arq = open(f, "r")

                # Loading File
                objectivies[i] = []
                ln_objectives = ''
                ranking[i] = []
                methods[i] = []

                for line in arq:
                    if line.find("#") == -1:
                        ranking[i].append(line.split("\t")[0].strip())
                        methods[i].append(line.split("\t")[6].strip())
                        if line.split("\t")[6].strip() not in values:
                            values[line.split("\t")[6].strip()] = [line.split("\t")[0].strip()]
                            self.headers.append(
                                [line.split("\t")[6].strip(), 0, 0, 0])  # DOMINANCE, WINS, LOSES
                        else:
                            ranks = values[line.split("\t")[6].strip()]
                            ranks.append(line.split("\t")[0].strip())
                            values[line.split("\t")[6].strip()] = ranks
                    else:
                        col = line.split("\t")
                        if len(col) > 1:
                            objectivies[i].append(col[2])
                            objectivies[i].append(col[4])
                            ln_objectives += col[2]
                            ln_objectives += ';'
                            ln_objectives += col[4]

                arq.close()

            matrixFile = open(os.path.join(self.path_execute, 'dr_matrix.txt'), 'w+')

            # utilizando os metodos como header
            for i in range(len(values)):
                if i == 0:
                    matrixFile.write('#%s' % methods[0][i])
                else:
                    matrixFile.write(methods[0][i])
                matrixFile.write('\t\t')

            matrixFile.write('\n')

            # executa a quantidade de x correspondente a qtde de metodos
            for i in range(len(values)):
                pdb = methods[0][i]
                if pdb in values:
                    ranks = values[pdb]
                    temp.append(ranks)

            for i in range(len(temp[0])):
                self.data.append([])
                for j in range(len(temp)):
                    self.data[i].append(temp[j][i])

            for i in range(len(temp[0])):
                for j in range(len(temp)):
                    matrixFile.write(temp[j][i])
                    matrixFile.write('\t\t')
                matrixFile.write('\n')

            matrixFile.close()

            self.CalculateDominance()

            self.makeHtml()

            pdbsToCopy = [os.path.join(self.path_execute, method) for method in self.methods]

            if(self.opts.useJmol == 'true'):
                self.makeHtmlWithJMol(pdbsToCopy[0].split('/')[-1])

        except Exception, e:
            raise Exception("Error on CreateDominanceMatrix.\n%s" % e)


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

    if not os.path.exists(opts.htmlfiledir):
        os.makedirs(opts.htmlfiledir)

    dr = DominanceRanking(opts)

    dr.ClassColection.setjobStart(datetime.datetime.now())
    dr.initTime = datetime.datetime.now()

    cProfile.run('dr.build_rankingDominance()', 'profileout.txt')

    dr.ClassColection.clearPathExecute(dr.path_execute)
