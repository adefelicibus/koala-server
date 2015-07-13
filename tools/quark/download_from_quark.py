#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import classe
import optparse
from bs4 import BeautifulSoup
import urllib2
import cProfile


class DownloadFromQuark(object):
    """
    Conect to the Quark server and download the Job results
    """

    path_execute = None

    def __init__(self, opts=None):
        """
        @type self: koala.DownloadFromQuark.DownloadFromQuark
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()

    def getQuarkFiles(self):
        """
        Get the Quark job result files
        @type self: koala.DownloadFromQuark.DownloadFromQuark
        """

        try:
            response = urllib2.urlopen(self.opts.inputURL)
            html = response.read()

            dir_execucao = self.ClassColection.CreateExecutionDirectory()
            self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

            soup = BeautifulSoup(html)
            for link in soup.find_all('a'):
                href = (link.get('href'))
                dname, e = os.path.splitext(href)
                filename = href.split('/')[-1]
                if e in ('.txt', '.pdb'):
                    url = href
                    self.ClassColection.openURL(url, self.path_execute, filename)

            path_output, file_output = os.path.split(self.opts.output)

            result, html = self.ClassColection.getResultFiles(self.path_execute, self.opts.toolname)

            self.ClassColection.sendOutputResults(path_output, file_output, result)

            if self.opts.createCompressFile == "True":

                pdbs = self.ClassColection.listDirectory(self.path_execute, '*.pdb')

                if self.ClassColection.compressFiles(pdbs, self.path_execute, "QuarkResults"):
                    path_output, file_output = os.path.split(self.opts.outputZip)
                    self.ClassColection.sendOutputResults(
                            path_output,
                            file_output,
                            os.path.join(self.path_execute, 'QuarkResults.zip'))

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputURL', default=None)
    op.add_option('-o', '--output', default=None)
    op.add_option('-d', '--outputdir', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    op.add_option('-e', '--createCompressFile', default=None)
    op.add_option('-z', '--outputZip', default=None)
    opts, args = op.parse_args()

    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    qfiles = DownloadFromQuark(opts)

    cProfile.run('qfiles.getQuarkFiles()', 'profileout.txt')

    qfiles.ClassColection.clearPathExecute(qfiles.path_execute)
