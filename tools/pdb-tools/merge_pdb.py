#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
from decimal import *
import zipfile
import gzip
import cProfile

from koala.utils import extract_zip_file, extract_gz_file, list_directory
from koala.utils.output import send_output_results
from koala.utils.path import PathRuns, clear_path_execute
from koala.utils.input import copy_pdbs_from_input
from koala.utils.pdb import merge_pdb


class MergePDB(object):
    """
    Merge a set of PDB files into models on a single PDB file
    """

    methods = []
    ignoreoutfiles = ['.pdb']

    def __init__(self, opts=None):
        """
        @type self: koala.MergePDB.MergePDB
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.path_runs = PathRuns()

    def run_MergePDB(self):
        """
        Get the input PDB files and run to merge
        @type self: koala.MergePDB.MergePDB
        """

        self.path_runs.set_execution_directory()

        if self.opts.compressedFile == '1':
            if zipfile.is_zipfile(opts.inputPDBs):
                extract_zip_file(opts.inputPDBs, self.path_runs.get_path_execution())
            else:
                try:
                    inF = gzip.GzipFile(opts.inputPDBs, 'rb')
                    f = inF.read()
                    inF.close()
                    if f:
                        extract_gz_file(opts.inputPDBs, self.path_runs.get_path_execution())
                except Exception, e:
                    raise Exception("The input file could not be read.\n%s" % e)
        else:
                copy_pdbs_from_input(
                    self.path_runs.get_path_execution(),
                    self.opts.outputdir,
                    self.opts.inputnames,
                    self.opts.inputPDBs)

        pdbs = list_directory(self.path_runs.get_path_execution(), "*.pdb")

        newpdb = merge_pdb(self.path_runs.get_path_execution(), pdbs)

        path_output, file_output = os.path.split(self.opts.fileoutput)

        send_output_results(path_output, file_output, newpdb)

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

    clear_path_execute(merge.path_runs.get_path_execution())
