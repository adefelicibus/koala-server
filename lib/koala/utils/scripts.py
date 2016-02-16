#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import shutil

from koala.utils.path import get_path_gromacs
from koala.utils import show_error_message, show_message


def rename_atoms(path_execution, path_galaxy):
    """
    Create a subprocess to rename the missing atoms in a PDB file using pdb2gmx
    @type self: koala.CalculateRMSD.CalculateRMSD
    @type path: string
    @type path_gromacs: string
    """

    try:
        cl = [
            '%s/scripts/rename_atoms.py' %
            path_galaxy, path_execution, get_path_gromacs(), '&']

        retProcess = subprocess.Popen(cl, 0, None, None, None, False)
        pvalue = retProcess.wait()

        if pvalue != 0:
            return False

        return True
    except Exception, e:
        show_error_message("Error while renaming atoms.\n%s" % e)


def check_pdb(path_execution, path_galaxy):
    """
    Create a subprocess to check the PDB structure using pdb2gmx
    @type self: koala.CalculateRMSD.CalculateRMSD
    @type path: string
    @type path_gromacs: string
    """

    try:
        cl = [
            '%s/scripts/check_structures_gromacs.py' %
            path_galaxy, path_execution, get_path_gromacs(), '&']

        retProcess = subprocess.Popen(cl, 0, None, None, None, False)
        pvalue = retProcess.wait()

        if pvalue != 0:
            return False

        directory = os.path.join(path_execution, 'no_accepted_by_pdb2gmx')
        if os.path.exists(directory):
            pdbs = os.listdir(directory)
            show_message('These files could not be accepted by Gromacs.\n%s\n\n' % pdbs)

        return True
    except Exception, e:
        show_error_message("Error while checking PDBs:\n%s" % e)


def prepare_pdb(path_execution, path_galaxy):
    try:
        cl = [
            '%s/scripts/prepare_structures.py' %
            path_galaxy, path_execution, '&']

        retProcess = subprocess.Popen(cl, 0, None, None, None, False)
        pvalue = retProcess.wait()

        if pvalue != 0:
            return False

        return True
    except Exception, e:
        show_error_message("Error while preparing PDBs:\n%s" % e)


def residue_renumber(path_execution, path_galaxy):
    try:
        cl = [
            '%s/scripts/residue_renumber_all_pdbs.py' %
            path_galaxy, path_execution, get_path_gromacs(), '&']

        retProcess = subprocess.Popen(cl, 0, None, None, None, False)
        pvalue = retProcess.wait()

        if pvalue != 0:
            return False

        return True
    except Exception, e:
        show_error_message("Error while renumbering PDBs:\n%s" % e)


def minimization(path_execution, path_galaxy, pdbPrefix=''):
    try:
        cl = ['%s/min.sh' % path_execution, path_execution, get_path_gromacs(), pdbPrefix, '&']

        shutil.copy(
            os.path.join(
                '%s/scripts/%s' % (path_galaxy, 'min.sh')),
            path_execution)

        retProcess = subprocess.Popen(cl, 0, None, None, None, False)
        pvalue = retProcess.wait()

        if pvalue != 0:
            return False

        return True
    except Exception, e:
        show_error_message("Error while minimization PDBs:\n%s" % e)
