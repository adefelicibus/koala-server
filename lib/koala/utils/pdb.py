#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


def parse_PDB(path, pdb_file, maxNumber=None, newName=None):
    try:
        pdb = file(pdb_file, 'r')
        path_f, name_f = os.path.split(pdb_file)
        name_f = name_f.split('.')[0]
        name_f = name_f.replace('_', '-')
        hearder = []
        new_pdbs = []
        for i, line in enumerate(open(pdb_file)):
            if len(new_pdbs) == maxNumber:
                break
            if i < 3:  # mudar, um arquivo pdb pode ter mais de 3 linhas de header
                hearder.append(line)
            if line.startswith("MODEL"):
                l = line.split(" ")
                if newName is None:
                    new_pdb = os.path.join(path, '%s-M%s.pdb' % (name_f, str(l[8].strip())))
                else:
                    new_pdb = os.path.join(path, '%s-M%s.pdb' % (newName, str(l[8].strip())))

                new_pdb_f = file(new_pdb, 'wr')

                new_pdbs.append('%s-M%s.pdb' % (name_f, str(l[8].strip())))

                if int(str(l[8].strip())) > 1:  # se o model for diferente de 1, coloca o header
                    for head in hearder:
                        new_pdb_f.write(head)

                while not line.startswith("ENDMDL"):
                    line = pdb.readline()
                    new_pdb_f.write(line)

                new_pdb_f.close()

        return new_pdbs

    except Exception, e:
        self.ShowErrorMessage("Error when parsePDB:\n%s" % e)


def mergePDB(path, pdbs):
    try:
        if not pdbs:
            self.ShowErrorMessage("There is no PDB file to merge.")

        new_pdb = []
        header = []

        for idx, pdb_file in enumerate(pdbs):
            pdb = open(os.path.join(path, pdb_file), 'r')

            for line in pdb:
                if idx == 0:  # primeiro arquivo, copia o cabeçalho
                    if not line.startswith("ATOM") and \
                        not line.startswith("MODEL") and \
                            not line.startswith("TER") and not line.startswith("ENDMDL"):
                        header.append(line)
                    elif not line.startswith("ATOM"):
                        continue
                    else:
                        new_pdb.append(line)
                else:
                    if not line.startswith("ATOM"):
                        continue
                    else:
                        new_pdb.append(line)
            new_pdb.append("TER\n")
            new_pdb.append("ENDMDL\n")
            if (idx + 2) <= len(pdbs):
                new_pdb.append("MODEL        %s\n" % (idx + 2))

        pdbf = os.path.join(path, 'MergedPDB.pdb')
        new_pdb_f = file(pdbf, 'wr')
        new_pdb_f.write(''.join(header))
        new_pdb_f.write(''.join('MODEL        1\n'))
        new_pdb_f.write(''.join(new_pdb))
        new_pdb_f.write('\n')
        new_pdb_f.close()

        return pdbf

    except Exception, e:
        self.ShowErrorMessage("Error when mergePDB:\n%s" % e)
