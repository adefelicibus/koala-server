#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from koala import classe
import optparse
import cProfile


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
        self.ClassColection = classe.IcmcGalaxy()

    def run_SplitPDB(self):
        """
        Get the PDB input files and run the splitting
        @type self: koala.SplitPDB.SplitPDB
        """
        try:
            dir_execucao = self.ClassColection.CreateExecutionDirectory()
            self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

            link_name = os.path.join(self.opts.outputdir, os.path.basename(self.opts.pdbName))
            if not os.path.exists(link_name):
                os.symlink(self.opts.inputPDB, link_name)
                os.system("cp %s %s" % (link_name, self.path_execute))

            pdbs = self.ClassColection.parse_PDB(
                    self.path_execute,
                    os.path.join(self.path_execute, self.opts.pdbName))

            path_output, file_output = os.path.split(self.opts.output)

            self.ClassColection.sendMultipleOutputs(
                    self.path_execute,
                    pdbs, self.opts.galaxydir,
                    self.opts.outputID)

            if self.opts.createCompressFile == "True":
                if self.ClassColection.compressFiles(pdbs, self.path_execute, self.opts.toolname):
                    path_output, file_output = os.path.split(self.opts.outputZip)
                    self.ClassColection.sendOutputResults(
                            path_output,
                            file_output,
                            os.path.join(self.path_execute, '%s.zip' % self.opts.toolname))

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

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

    splitpdb.ClassColection.clearPathExecute(splitpdb.path_execute)
