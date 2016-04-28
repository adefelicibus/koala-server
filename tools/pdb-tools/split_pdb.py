#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
import cProfile

from koala.utils import show_error_message, compress_files
from koala.utils.output import send_multiple_outputs, send_output_results
from koala.utils.path import PathRuns, clear_path_execute
from koala.utils.pdb import parse_pdb


class SplitPDB(object):
    """
    Split the models of a PDB file into new PDB file, where a model corresponds to a new PDB file
    """

    def __init__(self, opts=None):
        """
        @type self: koala.SplitPDB.SplitPDB
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.path_runs = PathRuns()

    def run_SplitPDB(self):
        """
        Get the PDB input files and run the splitting
        @type self: koala.SplitPDB.SplitPDB
        """
        try:
            self.path_runs.set_execution_directory()

            link_name = os.path.join(self.opts.outputdir, os.path.basename(self.opts.pdbName))
            if not os.path.exists(link_name):
                os.symlink(self.opts.inputPDB, link_name)
                os.system("cp %s %s" % (link_name, self.path_runs.get_path_execution()))

            pdbs = parse_pdb(
                self.path_runs.get_path_execution(),
                os.path.join(self.path_runs.get_path_execution(), self.opts.pdbName))

            path_output, file_output = os.path.split(self.opts.output)

            send_multiple_outputs(
                self.path_runs.get_path_execution(),
                pdbs, self.opts.galaxydir,
                self.opts.outputID)

            if self.opts.createCompressFile == "True":
                if compress_files(pdbs, self.path_runs.get_path_execution(), self.opts.toolname):
                    path_output, file_output = os.path.split(self.opts.outputZip)
                    send_output_results(
                        path_output,
                        file_output,
                        os.path.join(
                            self.path_runs.get_path_execution(), '%s.zip' % self.opts.toolname))

        except Exception, e:
            show_error_message(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputPDB', default=None)
    op.add_option('-n', '--pdbName', default=None)
    op.add_option('-o', '--output', default=None)
    op.add_option('-d', '--outputdir', default=None)
    op.add_option('-e', '--createCompressFile', default=None)
    op.add_option('-c', '--outputID', default=None)
    op.add_option('-z', '--outputZip', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    op.add_option('-g', '--galaxydir', default=None)
    op.add_option('-t', '--toolname', default=None)
    opts, args = op.parse_args()

    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    splitpdb = SplitPDB(opts)

    cProfile.run('splitpdb.run_SplitPDB()', 'profileout.txt')

    clear_path_execute(splitpdb.path_runs.get_path_execution())
