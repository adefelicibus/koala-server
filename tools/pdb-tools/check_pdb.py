#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
from subprocess import Popen, PIPE
import zipfile
import gzip
import cProfile
import shutil

from koala.utils import show_error_message, list_directory, compress_files
from koala.utils import extract_zip_file, extract_gz_file
from koala.utils.output import send_multiple_outputs, send_output_results
from koala.utils.path import PathRuns, clear_path_execute, get_path_gromacs
from koala.utils.input import copy_pdbs_from_input
from koala.utils.pdb import delete_check_files


class CheckPDBStructure(object):
    """
    Check PDB structure according to GROMACS.
    This scripts uses the pdb2gmx to verify the PDB files.
    """
    path_execute = None
    check_pdb_log = 'check-pdb-log.txt'

    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.CheckPDBStructure.CheckPDBStructure
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.path_runs = PathRuns()

    def log_by_pdb2gmx(self, pdbfile, stderr=None, stdout=None):
        """
        Write the log file with the stderr from pdb2gmx
        @type self: koala.CheckPDBStructure.CheckPDBStructure
        @type pdbfile: file
        @type stderr: string
        @type stdout: string
        """
        try:
            f_log = open(
                os.path.join(self.path_runs.get_path_execution(), self.check_pdb_log), "a+")
            pdbfile = os.path.split(pdbfile)[1]
            outline = "STARTING LOG OF " + pdbfile + "\n"
            f_log.write(outline)
            outline = stderr + "\n"
            f_log.write(outline)
            outline = "FINISHED LOG OF " + pdbfile + "\n\n\n"
            f_log.write(outline)
            f_log.close()
        except Exception, e:
            show_error_message(str(e))

    def move_structures(self, pdbfile):
        """
        Move a PDB file to a specific directory
        @type self: koala.CheckPDBStructure.CheckPDBStructure
        @type pdbfile: file
        """
        try:
            directory = os.path.join(
                self.path_runs.get_path_execution(), 'no_accepted_by_pdb2gmx')
            if(not os.path.exists(directory)):
                os.makedirs(directory)
            shutil.move(pdbfile, directory)
        except Exception, e:
            show_error_message(str(e))

    def check_structue_by_pdb2gmx(self, pdbfile, gmx_path, forcefield):
        """
        Create a subprocess to verify all the PDB input files
        @type self: koala.CheckPDBStructure.CheckPDBStructure
        @type pdbfile: file
        @type gmx_path: string
        @type forcefield: string
        """
        try:
            delete_check_files(self.path_runs.get_path_execution())

            program = os.path.join(gmx_path, "pdb2gmx")

            process = Popen([
                    program,
                    '-f',
                    pdbfile,
                    '-o',
                    'check.gro',
                    '-p',
                    'check.top',
                    '-water',
                    'none',
                    '-ff',
                    forcefield,
                    '-ignh'], stdout=PIPE, stderr=PIPE)

            stdout, stderr = process.communicate()
            process.wait()

            # Checking output of pdb2gmx of pdbfile
            if stderr.find('Fatal error') >= 0:
                self.log_by_pdb2gmx(pdbfile, stderr)
                self.move_structures(pdbfile)

            delete_check_files(self.path_runs.get_path_execution())

        except Exception, e:
            show_error_message(str(e))

    def run_CheckPDBStructure(self):
        """
        Get the PDB files and run the checking
        @type self: koala.CheckPDBStructure.CheckPDBStructure
        """
        try:
            self.path_runs.set_path_execute()
            self.path_runs.set_execution_directory()

            if self.opts.compressedFile == '1':

                inputFiles = self.opts.inputPDBs.split(",")

                for input_f in inputFiles:
                    if zipfile.is_zipfile(input_f):
                        extract_zip_file(input_f, self.path_runs.get_path_execution())
                    else:
                        try:
                            inF = gzip.GzipFile(input_f, 'rb')
                            f = inF.read()
                            inF.close()
                            if f:
                                extract_gz_file(input_f, self.path_runs.get_path_execution())
                        except Exception, e:
                            raise Exception("The input file could not be read.\n%s" % e)
            else:
                    copy_pdbs_from_input(
                        self.path_runs.get_path_execution(),
                        self.opts.outputdir,
                        self.opts.inputnames,
                        self.opts.inputPDBs)

            pdbs = list_directory(self.path_runs.get_path_execution(), "*.pdb")

            for pdb in pdbs:
                self.check_structue_by_pdb2gmx(
                        os.path.join(self.path_runs.get_path_execution(), pdb),
                        get_path_gromacs(),
                        self.opts.forceField)

            path_output, file_output = os.path.split(self.opts.output)

            pdbs_accepted = list_directory(self.path_runs.get_path_execution(), "*.pdb")

            if compress_files(pdbs_accepted, self.path_runs.get_path_execution(), "PDBsChecked"):
                send_output_results(
                        path_output,
                        file_output,
                        os.path.join(self.path_runs.get_path_execution(), 'PDBsChecked.zip'))

            if(os.path.exists(
                    os.path.join(self.path_runs.get_path_execution(), self.check_pdb_log))):
                send_multiple_outputs(
                        path_output,
                        [os.path.join(self.path_runs.get_path_execution(), self.check_pdb_log)],
                        self.opts.galaxydir,
                        self.opts.outputID)

        except Exception, e:
            show_error_message(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputPDBs', default=None)
    op.add_option('-f', '--forceField', default='amber99sb-ildn')
    op.add_option('-n', '--inputnames', default=None)
    op.add_option('-o', '--output', default=None)
    op.add_option('-d', '--outputdir', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    op.add_option('-s', '--compressedFile', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-c', '--outputID', default=None)
    op.add_option('-g', '--galaxydir', default=None)
    opts, args = op.parse_args()

    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    checkpdb = CheckPDBStructure(opts)

    cProfile.run('checkpdb.run_CheckPDBStructure()', 'profileout.txt')

    clear_path_execute(checkpdb.path_runs.get_path_execution())
