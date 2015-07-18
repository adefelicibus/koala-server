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
import cProfile

pymol.finish_launching()


class SortMethodByFront(object):
    """
    Execute the 2PG Sort Method By Front Dominance algorithm without evaluate objectivies
    """

    path_execute = None
    methods = []
    ignoreoutfiles = ['.pdb']
    initTime = 0
    endTime = 0
    progname = "SortMethodByFront"

    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.SortMethodByFront.SortMethodByFront
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()

    def timenow(self):
        """
        Return current time as a formmated string
        @type self: koala.SortMethodByFront.SortMethodByFront
        """

        return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))

    def getfSize(self, fpath, outpath):
        """
        Get the file size and return as string
        @type self: koala.SortMethodByFront.SortMethodByFront
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

    def buildHighchart(self):
        """
        Create a Highchart chart with the algorithm result
        @type self: koala.SortMethodByFront.SortMethodByFront
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
                "but the first as line and the others as scatter" % (obj1, obj2))

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
                    "valueDecimals": 3,
                },

            }

            data = []
            i_file = 0
            it = {}
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

    def makeHtml(self):
        """
        Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.SortMethodByFront.SortMethodByFront
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
        html.append('<h1 align="center">Sort Methods By Front Dominance results</h1><br></div>')

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
        if len(flist) > 0:
            for rownum, fname in enumerate(flist):
                dname, e = os.path.splitext(fname)
                sfsize = self.ClassColection.getFileSize(fname, self.opts.htmlfiledir)

                if e.lower() == ".front":
                    frontFiles.append(fname)
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

    def getBetterPDBs(self, path):
        """
        Get the methods that have been classified on the two first fronts
        @type self: koala.SortMethodByFront.SortMethodByFront
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
            raise Exception("Error on getBetterPDBs.\n%s" % e)

    def loadMatrixFile(self, matrix):
        """
        Read the input matrix file with the objectivies values
        """
        try:
            newResultFiles = open(self.path_execute + "objectivies.txt", "wr")

            for line in file(matrix, "r"):
                newResultFiles.write(line)

            newResultFiles.close()

        except Exception, e:
            raise Exception("Error on loadMatrixFile.\n%s" % e)

    def run_SortByFront(self):
        """
        Run the 2PG Sort Method algorithm to calculate the Pareto fronts and sorting
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

        self.ClassColection.CreateConfigurationFile(self.path_execute)

        self.loadMatrixFile(self.opts.inputTxt)

        objFile = os.path.join(self.path_execute, 'objectivies.txt')

        self.ClassColection.setCommand(
                '2pg_cartesian',
                'protpred-Gromacs-Sort_Method_by_Front_Dominance')

        cl = ['nohup', self.ClassColection.getCommand(), objFile, '&']

        retProcess = subprocess.Popen(cl, 0, None, None, None, False)
        retProcess.wait()

        self.getBetterPDBs(self.path_execute)

        result, filesHtml = self.ClassColection.getResultFiles(
                self.path_execute,
                self.opts.toolname)

        self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, filesHtml)
        self.ClassColection.sendOutputFilesHtml(self.opts.htmlfiledir, [result])

        self.makeHtml()

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputTxt', default=None)
    op.add_option('-k', '--htmlfiledir', default=None)
    op.add_option('-z', '--filehtml', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-g', '--galaxyroot', default=None)
    opts, args = op.parse_args()
    if not os.path.exists(opts.htmlfiledir):
        os.makedirs(opts.htmlfiledir)

    sort = SortMethodByFront(opts)

    sort.ClassColection.setjobStart(datetime.datetime.now())
    sort.initTime = datetime.datetime.now()

    cProfile.run('sort.run_SortByFront()', 'profileout.txt')

    sort.ClassColection.clearPathExecute(sort.path_execute)
