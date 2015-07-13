#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import classe
import optparse
import subprocess
import cProfile


class BuildConformation2PG(object):
    """
    Execute the 2PG Build Conformation algorithm.
    """

    path_execute = None
    os.environ["GMX_MAXBACKUP"] = "-1"

    def __init__(self, opts=None):
        """
        @type self: koala.BuildConformation2PG.BuildConformation2PG
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()

    def run_Build_Conformation(self):
        """
        Create the 2PG Build Conformation configuration file and begin
        the execution to create a initial population.

        @type self: koala.BuildConformation2PG.BuildConformation2PG
        """
        try:
            dir_execucao = self.ClassColection.CreateExecutionDirectory()
            self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

            self.ClassColection.CreateLocalFastaFile(
                    self.path_execute,
                    self.opts.fromFasta,
                    self.opts.inputFasta,
                    self.opts.toolname)

            self.ClassColection.CopyNecessaryFiles(self.path_execute)

            self.ClassColection.setParameter('gromacs_energy_min', self.opts.gromacsEnergyMin)
            self.ClassColection.setParameter('SizePopulation', self.opts.sizePopulation)
            self.ClassColection.setParameter('force_field', self.opts.forceField)
            self.ClassColection.setParameter('rotamer_library', self.opts.rotamerLibrary)
            if(self.ClassColection.getParameterValue('force_field') == 'amber99sb-ildn'):
                self.ClassColection.setParameter('c_terminal_charge', self.opts.cTerminal)
                self.ClassColection.setParameter('n_terminal_charge', self.opts.nTerminal)
            self.ClassColection.setParameter(
                    'objective_analisys_dimo_source',
                    '/home/%s/programs/dimo/DIMO2' % self.ClassColection.getLoggedUser())
            self.ClassColection.setParameter(
                    'SequenceAminoAcidsPathFileName',
                    self.path_execute + 'fasta.txt')
            self.ClassColection.setParameter('Local_Execute', self.path_execute)
            self.ClassColection.setParameter(
                    'Path_Gromacs_Programs',
                    '/home/%s/programs/gmx-4.6.5/no_mpi/bin/' % self.ClassColection.getLoggedUser())
            self.ClassColection.setParameter('NativeProtein', '%s1VII.pdb' % self.path_execute)
            self.ClassColection.setParameter(
                    'Database',
                    '%sDatabase/' % self.ClassColection.getPathAlgorithms('2pg_build_conformation'))

            self.ClassColection.CreateConfigurationFile(self.path_execute)

            self.ClassColection.setCommand('2pg_build_conformation', 'protpred-Gromacs_pop_initial')

            config = self.ClassColection.getConfigurationFile('configuration.conf')

            cl = [self.ClassColection.getCommand(), config, '&']

            retProcess = subprocess.Popen(
                cl, 0, stdout=None,  stderr=subprocess.STDOUT, shell=False)
            retCode = retProcess.wait()
            if(retCode != 0):
                self.ClassColection.ShowErrorMessage(
                    "The 2PG framework finished wrong.\nContact the system administrator.")

            path_output, file_output = os.path.split(self.opts.output)

            result, html = self.ClassColection.getResultFiles(self.path_execute, self.opts.toolname)

            self.ClassColection.sendOutputResults(path_output, file_output, result)

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

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

    bc.ClassColection.clearPathExecute(bc.path_execute)
