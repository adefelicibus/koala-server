#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import classe
import optparse
from decimal import *
import zipfile
import gzip
import cProfile

progname = "MergePDB"


class MergePDB(object):
    """
    Merge a set of PDB files into models on a single PDB file
    """

    path_execute = None
    methods = []
    ignoreoutfiles = ['.pdb']

    def __init__(self, opts=None):
        """
        @type self: koala.MergePDB.MergePDB
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()

    def run_MergePDB(self):
        """
        Get the input PDB files and run to merge
        @type self: koala.MergePDB.MergePDB
        """

        dir_execucao = self.ClassColection.CreateExecutionDirectory()
        self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

        if self.opts.compressedFile == '1':
            if zipfile.is_zipfile(opts.inputPDBs):
                self.ClassColection.extractZipFile(opts.inputPDBs, self.path_execute)
            else:
                try:
                    inF = gzip.GzipFile(opts.inputPDBs, 'rb')
                    f = inF.read()
                    inF.close()
                    if f:
                        self.ClassColection.extractGzFile(opts.inputPDBs, self.path_execute)
                except Exception, e:
                    raise Exception("The input file could not be read.\n%s" % e)
        else:
                self.ClassColection.copyPDBsFromInput(
                        self.path_execute,
                        self.opts.outputdir,
                        self.opts.inputnames,
                        self.opts.inputPDBs)

        pdbs = self.ClassColection.listDirectory(self.path_execute, "*.pdb")

        newpdb = self.ClassColection.mergePDB(self.path_execute, pdbs)

        path_output, file_output = os.path.split(self.opts.fileoutput)

        self.ClassColection.sendOutputResults(path_output, file_output, newpdb)

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputPDBs', default=None)
    op.add_option('-k', '--outputdir', default=None)
    op.add_option('-z', '--fileoutput', default=None)
    op.add_option('-n', '--inputnames', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-g', '--galaxyroot', default=None)
    op.add_option('-a', '--datasetID', default=None)
    op.add_option('-s', '--compressedFile', default=None)
    opts, args = op.parse_args()

    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    merge = MergePDB(opts)

    cProfile.run('merge.run_MergePDB()', 'profileout.txt')

    self.ClassColection.clearPathExecute(merge.path_execute)
