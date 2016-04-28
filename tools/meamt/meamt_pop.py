#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import optparse
import subprocess
import cProfile

from koala.utils import TimeJobExecution, copy_necessary_files, show_error_message
from koala.utils.output import get_result_files, send_output_results
from koala.utils.path import PathRuns, clear_path_execute
from koala.utils.input import create_local_fasta_file
from koala.frameworks.params import Params


class BuildPopulationMEAMT(object):
    """
    Execute the MEAMT Build Population algorithm.
    """

    sequence = None
    path_execute = None
    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.BuildPopulationMEAMT.BuildPopulationMEAMT
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.time_execution = TimeJobExecution()
        self.path_runs = PathRuns()
        self.framework = Params('MEAMT')

    def main(self):
        """
        Create the MEAMT Build Population configuration file and begin
        the execution to create a initial population.

        @type self: koala.BuildPopulationMEAMT.BuildPopulationMEAMT
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

            self.framework.set_command(
                self.path_runs.get_path_execution(),
                'aemt-pop-up2')

            size = int(self.opts.sizePopulation) / 15

            cl = [
                self.framework.get_command(),
                str(0),
                self.opts.sizePopulation,
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(size),
                str(0),
                str(0),
                self.opts.VanderWaalsWeight,
                self.opts.ChargeWeight,
                str(0),
                str(0),
                str(0),
                str(0),
                str(0),
                self.opts.SolvWeight,
                self.opts.HbondWeight,
                os.path.join(self.path_runs.get_path_execution(), "fasta.txt"),
                os.path.join(self.path_runs.get_path_execution(), "result.txt"),
                os.path.join(self.path_runs.get_path_execution(), "pop_meamt.txt"),
                os.path.join(self.path_runs.get_path_execution(), "protein.pdb"),
                os.path.join(self.path_runs.get_path_execution(), "saida1.txt"),
                os.path.join(self.path_runs.get_path_execution(), "angles.txt"),
                str(0),
                os.path.join(self.path_runs.get_path_execution(), "meat.txt"),
                '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            retProcess.wait()

            path_output, file_output = os.path.split(self.opts.output)

            result, html = get_result_files(
                self.path_runs.get_path_execution(), self.opts.toolname)

            send_output_results(path_output, file_output, result)

        except Exception, e:
            show_error_message(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputFasta', default=None)
    op.add_option('-s', '--sizePopulation', default=None)
    op.add_option('-l', '--fitnessEnergy', default=None)
    op.add_option('-a', '--VanderWaalsWeight', default=None)
    op.add_option('-b', '--HbondWeight', default=None)
    op.add_option('-c', '--SolvWeight', default=None)
    op.add_option('-d', '--ChargeWeight', default=None)
    op.add_option('-w', '--fromFasta', default=None)
    op.add_option('-o', '--output', default=None)
    op.add_option('-g', '--outputdir', default=None)
    op.add_option('-t', '--toolname', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    opts, args = op.parse_args()

    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    bp = BuildPopulationMEAMT(opts)
    cProfile.run('bp.main()', 'profileout.txt')

    clear_path_execute(bp.path_runs.get_path_execution())
