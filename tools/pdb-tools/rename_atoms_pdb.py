#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
from subprocess import Popen, PIPE
import cProfile

from koala.utils import show_error_message
from koala.utils.output import send_output_results
from koala.utils.path import PathRuns, clear_path_execute, get_path_gromacs
from koala.utils.pdb import delete_check_files


class RenameAtoms(object):
    """
    Rename the missing atoms of a PDB file according to GROMACS
    """

    path_execute = None
    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.RenameAtoms.RenameAtoms
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.path_runs = PathRuns()

    def rename_atoms_structure(self, pdbfile, gmx_path, forcefield):
        """
        Create a subprocess to rename the atoms of the PDB input file using pdb2gmx
        @type self: koala.RenameAtoms.RenameAtoms
        @type pdbfile: file
        @type gmx_path: string
        @type forcefield: string
        """
        delete_check_files(self.path_runs.get_path_execution())

        program = os.path.join(gmx_path, "pdb2gmx")
        process = Popen([
                program,
                '-f',
                pdbfile,
                '-o',
                pdbfile,
                '-p',
                'check.top',
                '-water',
                'none',
                '-ff',
                forcefield], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        process.wait()

        delete_check_files(self.path_runs.get_path_execution())

    def run_RenameAtoms(self):
        """
        Get the PDB file and run the renaming
        @type self: koala.CheckPDBStructure.CheckPDBStructure
        """
        try:
            self.path_runs.set_path_execute()
            self.path_runs.set_execution_directory()

            self.opts.pdbName = self.opts.pdbName.replace(
                ' ', '-').replace('(', '').replace(')', '')

            link_name = os.path.join(self.opts.outputdir, os.path.basename(self.opts.pdbName))
            if not os.path.exists(link_name):
                os.symlink(self.opts.inputPDB, link_name)
                os.system("cp %s %s" % (link_name, self.path_runs.get_path_execution()))

            self.rename_atoms_structure(
                    os.path.join(self.path_runs.get_path_execution(), self.opts.pdbName),
                    get_path_gromacs(),
                    self.opts.forceField
            )

            path_output, file_output = os.path.split(self.opts.output)

            send_output_results(
                    path_output,
                    file_output,
                    os.path.join(self.path_runs.get_path_execution(), self.opts.pdbName))

        except Exception, e:
            show_error_message(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputPDB', default=None)
    op.add_option('-f', '--forceField', default='amber99sb-ildn')
    op.add_option('-n', '--pdbName', default=None)
    op.add_option('-o', '--output', default=None)
    op.add_option('-d', '--outputdir', default=None)
    op.add_option('-r', '--galaxyroot', default=None)

    opts, args = op.parse_args()
    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    rnatoms = RenameAtoms(opts)

    cProfile.run('rnatoms.run_RenameAtoms()', 'profileout.txt')

    clear_path_execute(rnatoms.path_runs.get_path_execution())
