#!/usr/bin/env python
# -*- coding: utf-8 -*-

from koala import classe
import argparse
import cProfile
import subprocess
import os


class ArgsParse(object):
    """
    Parse the args passed by the Galaxy tool
    """
    pass


class ProtPredEDACEDA(object):
    """
    Execute the ProtPred-EDA CEDA evolutionary algorithm.
    """
    path_execute = None

    def __init__(self, opts=None):
        """
        @type self: koala.ProtPredEDA.ProtPredEDA
        @type opts: ArgsParse parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()
        self.ClassColection.setFramework("ProtPred-EDA")

    def main(self):
        """
        Create the ProtPred-EDA configuration file and begin the execution.

        @type self: koala.ProtPredEDA.ProtPredEDA
        """
        try:
            if(self.opts.inputEmail):
                email = self.ClassColection.ValidateEmail(self.opts.inputEmail)
                dir_execucao = self.ClassColection.CreateExecutionDirectory(email)
            else:
                dir_execucao = self.ClassColection.CreateExecutionDirectory()

            self.path_execute = self.ClassColection.getPathExecute() + dir_execucao

            self.ClassColection.CreateLocalFastaFile(
                    self.path_execute,
                    self.opts.fromFasta,
                    self.opts.SequenceFile,
                    self.opts.toolname)

            self.ClassColection.CopyNecessaryFiles(self.path_execute)

            # Config
            self.ClassColection.setParameter('OptimMethod', 'ceda')
            self.ClassColection.setParameter('MaxEval', self.opts.MaxEval)
            self.ClassColection.setParameter('Threshold', self.opts.Threshold)

            # FitnessPSP
            self.ClassColection.setParameter('VanderWaals', self.opts.VanderWaals)
            # ClassColection.setParameter('SASA', self.opts.SASA)
            self.ClassColection.setParameter('Coulomb', self.opts.Coulomb)
            self.ClassColection.setParameter('Solvatation', self.opts.Solvatation)
            self.ClassColection.setParameter('HydrogenBond', self.opts.HydrogenBond)
            self.ClassColection.setParameter('Torsion', self.opts.Torsion)
            self.ClassColection.setParameter('UseAngleDB', self.opts.UseAngleDB)
            self.ClassColection.setParameter('AminoAcidL', self.opts.AminoAcidL)

            # CEDA
            self.ClassColection.setParameter('SamplingMode', self.opts.SamplingMode_CEDA)
            self.ClassColection.setParameter('MaxEval1', self.opts.MaxEval1)
            self.ClassColection.setParameter('MaxEval2', self.opts.MaxEval2)
            self.ClassColection.setParameter('Overlap', self.opts.Overlap)

            # SelectionConfig
            self.ClassColection.setParameter('SelSize', self.opts.SelSize)
            self.ClassColection.setParameter('TouSize', self.opts.TouSize)
            self.ClassColection.setParameter('SelMethod', self.opts.SelMethod)

            if(self.opts.SamplingMode_CEDA == "fgm"):
                # FGM
                self.ClassColection.setParameter(
                        'MixtureComponents',
                        self.opts.MixtureComponents_CEDA)
                self.ClassColection.setParameter('Threshold', self.opts.Threshold_CEDA)
                self.ClassColection.setParameter('Lambda', self.opts.Lambda)
                self.lassColection.setParameter('CutTree', self.opts.CutTree)

            self.ClassColection.CreateConfigurationFile(self.path_execute)

            self.ClassColection.setCommand('ProtPredEDA', 'protpred')

            config = self.ClassColection.getConfigurationFile('input.ini')

            cl = [self.ClassColection.getCommand(), config, '&']

            retProcess = subprocess.Popen(
                cl, 0, stdout=None,  stderr=None, shell=False)
            retCode = retProcess.wait()
            if(retCode != 0):
                self.ClassColection.ShowErrorMessage(
                    "The ProtPred-EDA framework finished wrong.\nContact the system administrator.")

            path_output, file_output = os.path.split(self.opts.output)

            result, filesHtml = self.ClassColection.getResultFiles(
                    self.path_execute,
                    self.opts.toolname)

            self.ClassColection.sendOutputResults(
                            path_output,
                            file_output,
                            result)

            if(self.opts.inputEmail):
                self.ClassColection.SendEmail(
                        'adefelicibus@gmail.com',
                        email,
                        '%s Execution on Galaxy - Cloud USP' % self.opts.toolname,
                        self.ClassColection.getMessageEmail(self.opts.toolname),
                        [],
                        'smtp.gmail.com')

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

if __name__ == '__main__':

    ap = ArgsParse()

    parser = argparse.ArgumentParser()

    parser.add_argument('Threshold')
    parser.add_argument('MaxEval')
    parser.add_argument('VanderWaals')
    parser.add_argument('Coulomb')
    parser.add_argument('Solvatation')
    parser.add_argument('HydrogenBond')
    parser.add_argument('Torsion')
    parser.add_argument('fromFasta')
    parser.add_argument('SequenceFile')
    parser.add_argument('UseAngleDB')
    parser.add_argument('AminoAcidL')
    parser.add_argument('Lambda')
    parser.add_argument('SelSize')
    parser.add_argument('TouSize')
    parser.add_argument('SelMethod')
    parser.add_argument('MaxEval1')
    parser.add_argument('MaxEval2')
    parser.add_argument('Overlap')
    parser.add_argument('SamplingMode_CEDA')
    parser.add_argument('MixtureComponents_CEDA')
    parser.add_argument('Threshold_CEDA')
    parser.add_argument('CutTree')
    parser.add_argument('output')
    parser.add_argument('outputdir')
    parser.add_argument('inputEmail')
    parser.add_argument('toolname')
    parser.add_argument('galaxyroot')
    parser.parse_args(namespace=ap)

    protpred_eda = ProtPredEDACEDA(ap)

    cProfile.run('protpred_eda.main()', 'profileout.txt')

    protpred_eda.ClassColection.clearPathExecute(protpred_eda.path_execute)
