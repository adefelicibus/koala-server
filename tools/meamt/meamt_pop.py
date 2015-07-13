#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import classe
import optparse
import subprocess
import cProfile


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
        self.ClassColection = classe.IcmcGalaxy()
        self.ClassColection.setFramework("MEAMT")

    def main(self):
        """
        Create the MEAMT Build Population configuration file and begin
        the execution to create a initial population.

        @type self: koala.BuildPopulationMEAMT.BuildPopulationMEAMT
        """
        try:
            dir_execucao = self.ClassColection.CreateExecutionDirectory()
            self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

            self.sequence = self.ClassColection.CreateLocalFastaFile(
                    self.path_execute,
                    self.opts.fromFasta,
                    self.opts.inputFasta,
                    self.opts.toolname)

            self.ClassColection.CopyNecessaryFiles(self.path_execute)

            # self.ClassColection.setParameter('tam_population', self.opts.sizePopulation)

            # self.ClassColection.setParameter('pop_vdw', str(size))
            # self.ClassColection.setParameter('pop_charge', str(size))
            # self.ClassColection.setParameter('pop_solv', str(size))
            # self.ClassColection.setParameter('pop_hbond', str(size))
            # self.ClassColection.setParameter('pop_nondom', str(size))
            # self.ClassColection.setParameter('pop_pond1', str(size))
            # self.ClassColection.setParameter('pop_pond2', str(size))
            # self.ClassColection.setParameter('pop_pond3', str(size))
            # self.ClassColection.setParameter('pop_pond4', str(size))
            # self.ClassColection.setParameter('pop_pond5', str(size))
            # self.ClassColection.setParameter('pop_pond6', str(size))
            # self.ClassColection.setParameter('pop_pond7', str(size))
            # self.ClassColection.setParameter('pop_pond8', str(size))
            # self.ClassColection.setParameter('pop_pond9', str(size))
            # self.ClassColection.setParameter('pop_pond10', str(size))
            # self.ClassColection.setParameter('pop_pond11', str(size))
            # self.ClassColection.setParameter('vdw_w', self.opts.VanderWaalsWeight)
            # self.ClassColection.setParameter('charge_w', self.opts.ChargeWeight)
            # self.ClassColection.setParameter('solv_w', self.opts.SolvWeight)
            # self.ClassColection.setParameter('hbond_w', self.opts.HbondWeight)
            # self.ClassColection.setParameter(
            #         'inputfasta', os.path.join(self.path_execute, "fasta.txt"))
            # self.ClassColection.setParameter(
            #         'resultTxt', os.path.join(self.path_execute, "result.txt"))
            # self.ClassColection.setParameter(
            #         'inputPop', os.path.join(self.path_execute, "pop_meamt.txt"))
            # self.ClassColection.setParameter(
            #         'inputPDB', os.path.join(self.path_execute, "protein.pdb"))
            # self.ClassColection.setParameter(
            #         'saida1', os.path.join(self.path_execute, "saida1.txt"))
            # self.ClassColection.setParameter(
            #         'angles', os.path.join(self.path_execute, "angles.txt"))
            # self.ClassColection.setParameter(
            #         'meat', os.path.join(self.path_execute, "meat.txt"))

            self.ClassColection.setCommand('meamt', 'aemt-pop-up2')

            size = int(self.opts.sizePopulation) / 15

            cl = [
                self.ClassColection.getCommand(),
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
                os.path.join(self.path_execute, "fasta.txt"),
                os.path.join(self.path_execute, "result.txt"),
                os.path.join(self.path_execute, "pop_meamt.txt"),
                os.path.join(self.path_execute, "protein.pdb"),
                os.path.join(self.path_execute, "saida1.txt"),
                os.path.join(self.path_execute, "angles.txt"),
                str(0),
                os.path.join(self.path_execute, "meat.txt"),
                '&']

            retProcess = subprocess.Popen(cl, 0, None, None, None, False)
            retProcess.wait()

            path_output, file_output = os.path.split(self.opts.output)

            result, html = self.ClassColection.getResultFiles(self.path_execute, self.opts.toolname)

            self.ClassColection.sendOutputResults(path_output, file_output, result)

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

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

    bp.ClassColection.clearPathExecute(bp.path_execute)
