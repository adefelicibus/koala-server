#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
import subprocess
import cProfile

from koala.utils import copy_necessary_files, show_error_message
from koala.utils.output import get_result_files, send_output_results
from koala.utils.path import PathRuns, clear_path_execute
from koala.utils.input import create_configuration_file, create_local_fasta_file
from koala.frameworks.params import Params


class BuildConformation2PG(object):
    """
    Execute the 2PG Build Conformation algorithm.
    """

    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.BuildConformation2PG.BuildConformation2PG
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.path_runs = PathRuns()
        self.framework = Params('2PG')

    def run_Build_Conformation(self):
        """
        Create the 2PG Build Conformation configuration file and begin
        the execution to create a initial population.

        @type self: koala.BuildConformation2PG.BuildConformation2PG
        """
        try:
            self.path_runs.set_execution_directory()

            self.sequence = create_local_fasta_file(
                self.path_runs.get_path_execution(),
                self.opts.fromFasta,
                self.opts.inputFasta,
                self.opts.toolname,
                self.framework)

            copy_necessary_files(
                self.path_runs.get_path_execute(),
                self.path_runs.get_path_execution(),
                self.framework.get_framework())

            self.framework.set_parameter(
                'gromacs_energy_min', self.opts.gromacsEnergyMin)
            self.framework.set_parameter(
                'SizePopulation', self.opts.sizePopulation)
            self.framework.set_parameter(
                'force_field', self.opts.forceField)
            self.framework.set_parameter(
                'rotamer_library', self.opts.rotamerLibrary)

            if(self.opts.forceField == 'amber99sb-ildn'):
                self.framework.set_parameter(
                    'c_terminal_charge', self.opts.cTerminal)
                self.framework.set_parameter(
                    'n_terminal_charge', self.opts.nTerminal)

            self.framework.set_parameter(
                'SequenceAminoAcidsPathFileName',
                self.path_runs.get_path_execution() + 'fasta.txt')
            self.framework.set_parameter(
                'Local_Execute',
                self.path_runs.get_path_execution())
            self.framework.set_parameter(
                'Path_Gromacs_Programs',
                self.path_runs.get_path_gromacs())
            self.framework.set_parameter(
                'NativeProtein',
                '%s1VII.pdb' % self.path_runs.get_path_execution())
            self.framework.set_parameter(
                'Database',
                '%sDatabase/' % self.path_runs.get_path_algorithms('build_conformation_2pg'))

            create_configuration_file(
                self.path_runs.get_path_execution(), self.framework)

            self.framework.set_command(
                self.path_runs.get_path_execution(),
                'protpred-Gromacs_pop_initial')

            config = 'configuration.conf'

            cl = [self.framework.get_command(), config, '&']

            retProcess = subprocess.Popen(
                cl, 0, stdout=None, stderr=subprocess.STDOUT, shell=False)
            retCode = retProcess.wait()
            if(retCode != 0):
                show_error_message(
                    "The 2PG framework finished wrong.\nContact the system administrator.")

            path_output, file_output = os.path.split(self.opts.output)

            result, html = get_result_files(self.path_runs.get_path_execution(), self.opts.toolname)

            send_output_results(path_output, file_output, result)

        except Exception, e:
            show_error_message(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-g', '--gromacsEnergyMin', default=None)
    op.add_option('-i', '--inputFasta', default=None)
    op.add_option('-s', '--sizePopulation', default=None)
    op.add_option('-f', '--forceField', default=None)
    op.add_option('-l', '--rotamerLibrary', default=None)
    op.add_option('-c', '--cTerminal', default=None)
    op.add_option('-n', '--nTerminal', default=None)
    op.add_option('-w', '--fromFasta', default=None)
    op.add_option('-o', '--output', default=None)
    op.add_option('-d', '--outputdir', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    opts, args = op.parse_args()

    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    bc = BuildConformation2PG(opts)
    cProfile.run('bc.run_Build_Conformation()', 'profileout.txt')

    clear_path_execute(bc.path_runs.get_path_execution())
