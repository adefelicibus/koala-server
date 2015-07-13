#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import classe
import optparse
import cProfile


class PDBDownload(object):
    """
    Download PDB files from RCSB mirror using PDBID
    """

    def __init__(self, opts=None):
        """
        @type self: koala.PDBDownload.PDBDownload
        @type opts: OptionParser parameters
        """
        assert opts is not None
        self.opts = opts
        self.ClassColection = classe.IcmcGalaxy()

    def getPDB(self):
        """
        Connect to pdb.org and download PDB files using PDBID
        @type self: koala.PDBDownload.PDBDownload
        """
        try:

            pdb_org = "http://www.rcsb.org/pdb/files/"

            pdbs = []  # pdbs id
            i = 0
            pdbsid = self.opts.inputIDs.split('#')
            for pdbid in range(len(pdbsid)):
                if len(pdbsid[pdbid]) > 0:
                    pdbidn = pdbsid[pdbid].strip()
                    pdbs.append(pdbidn)
                    i = i + 1

            path_output, file_output = os.path.split(self.opts.output)

            pdb_files = []
            for i, pdbid in enumerate(pdbs):
                url = "%s%s.pdb" % (pdb_org,  pdbid)
                self.ClassColection.openURL(url, path_output, "%s.pdb" % pdbid)
                pdb_files.append(os.path.join(path_output, "%s.pdb" % pdbid))

            self.ClassColection.sendMultipleOutputs(
                    path_output,
                    pdb_files,
                    self.opts.galaxydir,
                    self.opts.outputID)

        except Exception, e:
            self.ClassColection.ShowErrorMessage(str(e))

if __name__ == '__main__':
    op = optparse.OptionParser()
    op.add_option('-i', '--inputIDs', default=None)
    op.add_option('-o', '--output', default=None)
    op.add_option('-d', '--outputdir', default=None)
    op.add_option('-c', '--outputID', default=None)
    op.add_option('-r', '--galaxyroot', default=None)
    op.add_option('-g', '--galaxydir', default=None)
    opts, args = op.parse_args()

    if not os.path.exists(opts.outputdir):
        os.makedirs(opts.outputdir)

    pdbdown = PDBDownload(opts)

    cProfile.run('pdbdown.getPDB()', 'profileout.txt')
