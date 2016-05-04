#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
import subprocess
import datetime
from PyHighcharts.highcharts.chart import Highchart
from decimal import *
import cProfile

from koala.utils import get_file_size, show_error_message, list_directory
from koala.utils import TimeJobExecution, copy_necessary_files
from koala.utils.output import send_output_files_html, get_result_files
from koala.utils.path import PathRuns, clear_path_execute
# from koala.utils.input import create_configuration_file
from koala.frameworks.params import Params


class SortMethodByFront(object):
    """
    Execute the 2PG Sort Method By Front Dominance algorithm without evaluate objectivies
    """

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

        self.time_execution = TimeJobExecution()
        self.path_runs = PathRuns()
        self.framework = Params('2PG')

    def buildHighchart(self):
        """
        Create a Highchart chart with the algorithm result
        @type self: koala.SortMethodByFront.SortMethodByFront
        """

        try:
            # Load files
            files = list_directory(self.path_runs.get_path_execution(), '*.xvg')

            methods = self.methods

            # Objectivies
            obj1 = ""
            obj2 = ""

            x = [[]] * len(files)
            y = [[]] * len(files)

            for i, f in enumerate(files):
                f = os.path.join(self.path_runs.get_path_execution(), f)
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
            show_error_message("Error while building the Highchart:\n%s" % e)

    def makeHtml(self):
        """
        Create an HTML file content to list all the artifacts found in the html_dir
        @type self: koala.SortMethodByFront.SortMethodByFront
        """

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
                sfsize = get_file_size(fname, self.opts.htmlfiledir)

                if e.lower() == ".front":
                    frontFiles.append(fname)
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
        html.append('Total time: ~%dd %dh:%dm:%ds' % (dif[0], dif[1], dif[2], dif[3]))
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
            front = list_directory(path, "*.front")
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
            show_error_message("Error on getBetterPDBs.\n%s" % e)

    def loadMatrixFile(self, matrix):
        """
        Read the input matrix file with the objectivies values
        """
        try:
            newResultFiles = open(self.path_runs.get_path_execution() + "objectivies.txt", "wr")

            for line in file(matrix, "r"):
                newResultFiles.write(line)

            newResultFiles.close()

        except Exception, e:
            show_error_message("Error on loadMatrixFile.\n%s" % e)

    def run_SortByFront(self):
        """
        Run the 2PG Sort Method algorithm to calculate the Pareto fronts and sorting
        @type self: koala.SortByFront.SortByFront
        """

        self.path_runs.set_execution_directory()

        copy_necessary_files(
            self.path_runs.get_path_execute(),
            self.path_runs.get_path_execution(),
            self.framework.get_framework())

        self.loadMatrixFile(self.opts.inputTxt)

        objFile = os.path.join(self.path_runs.get_path_execution(), 'objectivies.txt')

        self.framework.set_command(
            self.path_runs.get_path_execution(),
            'protpred-Gromacs-Sort_Method_by_Front_Dominance')

        cl = ['nohup', self.framework.get_command(), objFile, '&']

        retProcess = subprocess.Popen(cl, 0, None, None, None, False)
        retProcess.wait()

        self.getBetterPDBs(self.path_runs.get_path_execution())

        result, filesHtml = get_result_files(
            self.path_runs.get_path_execution(),
            self.opts.toolname)

        send_output_files_html(self.opts.htmlfiledir, filesHtml)
        send_output_files_html(self.opts.htmlfiledir, [result])

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

    sort.time_execution.set_job_start(datetime.datetime.now())
    sort.initTime = datetime.datetime.now()

    cProfile.run('sort.run_SortByFront()', 'profileout.txt')

    clear_path_execute(sort.path_runs.get_path_execution())
