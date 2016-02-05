# -*- coding: utf-8 -*-

import data
import logging
from galaxy.datatypes.sniff import *
import commands

log = logging.getLogger(__name__)


class GenericMolFile(data.Text):
    file_ext = "mol2/sdf/drf"

    def check_filetype(self, filename):
        self.no_mols = commands.getstatusoutput("grep -c \\$\\$\\$\\$ "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            self.file_ext = "sdf"
            return True
        self.no_mols = commands.getstatusoutput("grep -c @\<TRIPOS\>MOLECULE "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            self.file_ext = "mol2"
            return True
        self.no_mols = commands.getstatusoutput("grep -c \"ligand id\" "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            self.file_ext = "drf"
            return True
        self.no_mols = commands.getstatusoutput("grep -c HEADER "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            self.file_ext = "pdb"
            return True
        self.no_mols = commands.getstatusoutput("grep -c COMPND "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            self.file_ext = "pdbqt"
            return True
        self.no_mols = commands.getstatusoutput("grep -c # DOI 10.1002/jcc.21334"+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            self.file_ext = "log"
            return True
        return False

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            if(self.check_filetype(dataset.file_name)):
                if (self.no_mols[1] == '1'):
                    dataset.blurb = "1 molecule"
                else:
                    dataset.blurb = "%s molecules" % self.no_mols[1]
            dataset.peek = data.get_file_peek(dataset.file_name, is_multi_byte=is_multi_byte)
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def get_mime(self):
        return 'text/plain'


class GenericMultiMolFile(GenericMolFile):
    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            self.sniff(dataset.file_name)
            if (self.no_mols[1] == '1'):
                dataset.blurb = "1 molecule"
            else:
                dataset.blurb = "%s molecules" % self.no_mols[1]
            dataset.peek = data.get_file_peek(dataset.file_name, is_multi_byte=is_multi_byte)
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'


class SDF(GenericMultiMolFile):
    file_ext = "sdf"

    def sniff(self, filename):
        self.no_mols = commands.getstatusoutput("grep -c \\$\\$\\$\\$ "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            return True
        else:
            return False


class MOL2(GenericMultiMolFile):
    file_ext = "mol2"

    def sniff(self, filename):
        self.no_mols = commands.getstatusoutput("grep -c @\<TRIPOS\>MOLECULE "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            return True
        else:
            return False


class DRF(GenericMultiMolFile):
    file_ext = "drf"

    def sniff(self, filename):
        self.no_mols = commands.getstatusoutput("grep -c \"ligand id\" "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            return True
        else:
            return False

class PDBQT(GenericMolFile):
    file_ext = "pdbqt"

    def sniff(self, filename):
        self.no_mols = commands.getstatusoutput("grep -c COMPND "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            return True
        else:
            self.no_mols = commands.getstatusoutput("grep -c REMARK "+filename)
            if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
                return True
            else:
                self.no_mols = commands.getstatusoutput("grep -c ATOM "+filename)
                if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
                    return True


    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            self.sniff(dataset.file_name)
            dataset.blurb = "protein structure file used by autodock vina"
        else:
            dataset.peek = "file does not exist"
            dataset.blurb = "file purged from disk"


class LOG(GenericMolFile):
    file_ext = "log"

    def sniff(self, filename):
        self.no_mols = commands.getstatusoutput("grep -c # DOI 10.1002/jcc.21334 "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            return True
        else:
            return False

class PDB(GenericMolFile):
    file_ext = "pdb"

    def sniff(self, filename):
        self.no_mols = commands.getstatusoutput("grep -c HEADER "+filename)
        if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
            return True
        else:
            self.no_mols = commands.getstatusoutput("grep -c ATOM "+filename)
            if (self.no_mols[0] == 0) & (self.no_mols[1] > 0):
                return True
            else:
                return False

    def set_peek(self, dataset, is_multi_byte=False):

        if not dataset.dataset.purged:
            # res = commands.getstatusoutput(
            #         "lib/galaxy/datatypes/countResidues.sh " + dataset.file_name)
            # dataset.peek = res[1]
            self.sniff(dataset.file_name)
            dataset.blurb = "protein structure file"
            # if (self.no_mols[1] == '1'):
            #     dataset.blurb = "1 protein structure"
            # else:
            #     dataset.blurb = "%s protein structures" % self.no_mols[1]
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'


class grd (data.Text):
    file_ext = "grd"

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            dataset.blurb = "score-grids for docking"
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'


class grdtgz (data.Text):
    file_ext = "grd.tgz"

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            dataset.blurb = "compressed score-grids for docking"
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'
