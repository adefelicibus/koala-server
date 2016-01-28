#!/usr/bin/env python
# -*- coding: utf-8 -*-

from koala.ordered_dict.default import DefaultOrderedDict

general_parametersMEAMT = [
        ('num_geracoes', '0'),
        ('tam_population', '400'),
        ('pop_vdw', '25'),
        ('pop_charge', '25'),
        ('pop_solv', '25'),
        ('pop_hbond', '25'),
        ('pop_nondom', '25'),
        ('pop_pond1', '25'),
        ('pop_pond2', '25'),
        ('pop_pond3', '25'),
        ('pop_pond4', '25'),
        ('pop_pond5', '25'),
        ('pop_pond6', '25'),
        ('pop_pond7', '25'),
        ('pop_pond8', '25'),
        ('pop_pond9', '25'),
        ('pop_pond10', '25'),
        ('pop_pond11', '25'),
        ('unknown1', '0'),
        ('unknown2', '0'),
        ('vdw_w', '1'),
        ('charge_w', '0.5'),
        ('unknown3', '0'),
        ('unknown4', '0'),
        ('unknown5', '0'),
        ('unknown6', '0'),
        ('unknown7', '0'),
        ('solv_w', '0.5'),
        ('hbond_w', '0.5'),
        ('inputfasta', 'fasta.txt'),
        ('resultTxt', 'result_1vii.txt'),
        ('inputPop', 'pop_meamt.txt'),
        ('inputPDB', '1vii.pdb'),
        ('saida1', 'saida1.txt'),
        ('angles', 'angles.txt'),
        ('unknown8', '0'),
        ('meat', '1vii_meat.txt'),
    ]

meamt_param = DefaultOrderedDict(list)
for k, v in general_parametersMEAMT:
    meamt_param[k].append(v)

general_parameters = {
    'gromacs_energy_min': 'ener_implicit',
    'NumberProcessor': '8',
    'NumberObjective': '1',
    'NumberGeration': '1',
    'SizePopulation': '1',
    'MonteCarloSteps': '50',
    'FrequencyMC': '5',
    'TemperatureMC': '370',
    'Fitness_Energy': 'Potential',
    'NativeProtein': '/home/faccioli/Execute/1VII_teste_1_1/1VII.pdb',
    'SequenceAminoAcidsPathFileName':
        '/home/faccioli/Execute/1VII_teste_1_1/1VII.fasta.txt',
    'NameExecutation': '1VII_teste_1',
    'Local_Execute': '/home/faccioli/Execute/1VII_teste_1_1/',
    'Database':
        '/home/faccioli/workspace/2pg_build_conformation/Database/',
    'rotamer_library': 'cad_tuffery',
    'top_file': 'top_protein.top',
    'IniPopFileName': 'pop_0.pdb',
    'Started_Generation': '-1',
    'z_matrix_fileName': 'z_matrix',
    'Path_Gromacs_Programs':
        '/home/faccioli/programs/gmx-4.6.5/no_mpi/bin/',
    'Computed_Energies_Gromacs_File':
        'file_energy_computed.ener.edr',
    'Energy_File_xvg': 'energy.xvg',
    'Computed_Areas_g_sas_File': 'file_g_sas_areas.xvg',
    'Computed_Energy_Value_File': 'energy_computed.xvg',
    'Computed_Radius_g_gyrate_File': 'file_g_gyrate_radius.xvg',
    'Computed_g_hbond_File': 'file_g_hbond.xvg',
    'How_Many_Rotation': '1',
    'min_angle_mutation_phi': '-10',
    'max_angle_mutation_phi': '10',
    'min_angle_mutation_psi': '-10',
    'max_angle_mutation_psi': '10',
    'min_angle_mutation_omega': '-10',
    'max_angle_mutation_omega': '10',
    'min_angle_mutation_side_chain': '-10',
    'max_angle_mutation_side_chain': '10',
    'apply_crossover': 'yes',
    'Individual_Mutation_Rate': '0.60',
    'mdp_file_min': 'energy_minimization_implicit.mdp',
    'mdp_file_name': 'compute_energy_implicit.mdp',
    'c_terminal_charge': 'none',
    'n_terminal_charge': 'none',
    'force_field': 'amber99sb-ildn',
    'objective_analisys': 'none',
    'objective_analisys_dimo_source':
        '/home/faccioli/workspace/dimo/DIMO2',
    'Program_Run_GreedyTreeGenerator2PG':
        '/2pg_cartesian/scripts/dimo/call_GreedyTreeGenerator2PG.sh',
    '1_point_cros_Rate': '0.80',
    'StepNumber': '100',
}

general_parameters_eda = [
                ('[Config]', ''),
                ('SaveOutput', 'yes'),
                ('RandomSeed', '0'),
                ('PrintDetails', 'no'),
                ('RedirectToNull', 'no'),
                ('RunMode', 'CreateRun'),
                ('OptimMethod', 'eda'),
                ('OutputFolder', 'out'),
                ('Threshold', '0.0001'),
                ('MaxEval', '1000000'),
                ('Fitness', 'psp'),
                ('SaveData', 'no'),
                ('OverwriteData', 'no'),
                ('PopFile', 'null'),
                ('ExpsMode', 'no'),
                ('SetsNumber', '4'),
                ('[Optimization]', ''),
                ('CellList', 'yes'),
                ('CLOpenMP', 'no'),
                ('SASAGPU', 'no'),
                ('[FitnessPSP]', ''),
                ('VanderWaals', '1.0'),
                ('SASA', '0.0'),
                ('Coulomb', '0.0'),
                ('Solvatation', '0.0'),
                ('HydrogenBond', '0.0'),
                ('Torsion', '0.0'),
                ('SequenceFile', 'fasta.txt'),
                ('UseAngleDB', 'no'),
                ('AminoAcidL', 'yes'),
                ('SideChainMulti', 'no'),
                ('SinglePDB', 'no'),
                ('ChiDB', 'no'),
                ]

protpred_eda_param = DefaultOrderedDict(list)
for k, v in general_parameters_eda:
    protpred_eda_param[k].append(v)

l_rw_param = [
            ('[RandomWalk]', ''),
            ('PopSize', '500'),
            ]

rw_param = DefaultOrderedDict(list)
for k, v in l_rw_param:
    rw_param[k].append(v)

l_mcm_param = [
            ('[MonteCarloMetropolis]', ''),
            ('PopSize', '5000'),
            ('Step', '0.02'),
            ('Boltzmann', '0.259'),
            ]

mcm_param = DefaultOrderedDict(list)
for k, v in l_mcm_param:
    mcm_param[k].append(v)

l_ga_param = [
            ('[GeneticAlgorithm]', ''),
            ('PopSize', '3000'),
            ('OffSize', '3000'),
            ('CrossoverRate', '0.3'),
            ('MutationRate', '0.05'),
            ('MutationFactor', '0.1'),
            ('[SelectionConfig]', ''),
            ('SelSize', '5000'),
            ('SelMethod', 'tournament'),
            ('TouSize', '2'),
            ]

ga_param = DefaultOrderedDict(list)
for k, v in l_ga_param:
    ga_param[k].append(v)

l_rboa_param = [
                ('[rBOA]', ''),
                ('PopSize', '5000'),
                ('SelSize', '2500'),
                ('MaxParents', '1'),
                ('MixtureComponents', '2')
                ]

rboa_param = DefaultOrderedDict(list)
for k, v in l_rboa_param:
    rboa_param[k].append(v)

l_de_param = [
            ('[DE]', ''),
            ('PopSize', '3000'),
            ('OffSize', '3000'),
            ('CrossoverRate', '0.4'),
            ('FRate', '0.2'),
            ('[SelectionConfig]', ''),
            ('SelSize', '5000'),
            ('SelMethod', 'tournament'),
            ('TouSize', '2'),
            ]

de_param = DefaultOrderedDict(list)
for k, v in l_de_param:
    de_param[k].append(v)

l_eda_param = [
            ('[EDA]', ''),
            ('PopSize', '500'),
            ('OffSize', '500'),
            ('SamplingMode', 'univariate'),
            ('Noise', '2'),
            ('Objective', 'mono'),
            ('Hierarchical', 'no'),
            ('[SelectionConfig]', ''),
            ('SelSize', '500'),
            ('SelMethod', 'tournament'),
            ('TouSize', '2'),
            ]

eda_param = DefaultOrderedDict(list)
for k, v in l_eda_param:
    eda_param[k].append(v)

l_ceda_param = [
            ('[CEDA]', ''),
            ('MaxEval1', '500000'),
            ('MaxEval2', '500000'),
            ('Overlap', '0'),
            ('SamplingMode', 'univariate'),
            ('[SelectionConfig]', ''),
            ('SelSize', '5000'),
            ('SelMethod', 'tournament'),
            ('TouSize', '2'),
            ]

ceda_param = DefaultOrderedDict(list)
for k, v in l_ceda_param:
    ceda_param[k].append(v)

l_fgm_param = [
            ('[FGM]', ''),
            ('MixtureComponents', '2'),
            ('Dimensionality', '2'),
            ('Threshold', '1.5'),
            ('Lambda', '0.9'),
            ('Partitions', '150'),
            ('FullMatrix', 'no'),
            ('GlobalSigma', 'no'),
            ('UseJointPDF', 'no'),
            ('[Hierarchical]', ''),
            ('ClusterMethod', 'euclidian'),
            ('AgglomerationM', 'complete'),
            ('CutTree', '2'),
            ('ClusteringType', 'dihedral'),
            ]

fgm_param = DefaultOrderedDict(list)
for k, v in l_fgm_param:
    fgm_param[k].append(v)


def getParameters():
        return self.general_parameters


def setParameter(key, value):
        try:
            if(self.framework == '2PG'):
                if key in self.general_parameters:
                    self.general_parameters[key] = value
                else:
                    raise "There is no key %s in the parameters list. \
                                Please, use a valid key.\n" % key
            elif(self.framework == 'ProtPred-EDA'):
                if key in self.protpred_eda_param:
                    self.protpred_eda_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'rw'):
                    self.rw_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'mcm'):
                    self.mcm_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'eda'):
                    if key in self.eda_param:
                        self.eda_param[key] = value
                    elif self.\
                            getParameterValue("SamplingMode", "eda") == 'fgm':
                        if key in self.fgm_param:
                            self.fgm_param[key] = value
                        else:
                            raise "There is no key %s in the parameters list. \
                                    Please, use a valid key.\n" % key
                    else:
                        raise "There is no key %s in the parameters list. \
                                Please, use a valid key.\n" % key
                elif(self.getParameterValue("OptimMethod") == 'rboa'):
                    self.rboa_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'ga'):
                    self.ga_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'de'):
                    self.de_param[key] = value
                elif(self.getParameterValue("OptimMethod") == 'ceda'):
                    if key in self.ceda_param:
                        self.ceda_param[key] = value
                    elif self.\
                            getParameterValue("SamplingMode", "ceda") == 'fgm':
                        if key in self.fgm_param:
                            self.fgm_param[key] = value
                        else:
                            raise "There is no key %s in the parameters list [SamplingMode](%s)(%s). \
                                    Please, use a valid key.\n" % (
                                        key,
                                        self.getParameterValue("OptimMethod"),
                                        self.getParameterValue("SamplingMode"),
                                        )
                    else:
                        raise "There is no key %s in the parameters list[OptimMethod](%s)(%s). \
                                Please, use a valid key.\n" % (
                                    key,
                                    self.getParameterValue("OptimMethod"),
                                    self.getParameterValue("SamplingMode"),
                                    )
                else:
                    raise "There is no key %s in the parameters list. \
                            Please, use a valid key.\n" % key
            elif(self.framework == 'MEAMT'):
                if key in self.meamt_param:
                    self.meamt_param[key] = value
                else:
                    raise "There is no key %s in the parameters list. \
                                Please, use a valid key.\n" % key
            else:
                raise Exception("There is no defined framework.\n")
        except Exception, e:
            self.ShowErrorMessage("Error when setParameter\n%s" % e)
            # raise Exception("Error while setting parameter: \n%s" % e)


def getParameterValue(key, optMethod=None):
    try:
        if(self.framework == '2PG'):
            if key in self.general_parameters:
                return self.general_parameters[key]
        elif(self.framework == 'ProtPred-EDA'):
            if key in self.protpred_eda_param:
                return self.protpred_eda_param[key]
            elif key in self.rw_param:
                return self.rw_param[key]
            elif key in self.mcm_param:
                return self.mcm_param[key]
            elif key in self.eda_param and optMethod == "eda":
                return self.eda_param[key]
            elif key in self.fgm_param:
                return self.fgm_param[key]
            elif key in self.ga_param:
                return self.ga_param[key]
            elif key in self.rboa_param:
                return self.rboa_param[key]
            elif key in self.de_param:
                return self.de_param[key]
            elif key in self.ceda_param and optMethod == "ceda":
                return self.ceda_param[key]
            else:
                raise Exception(
                        "There is no key %s in the parameters list"
                        "Please, use a valid key.\n" % key)
        elif(self.framework == 'MEAMT'):
            if key in self.meamt_param:
                return self.meamt_param[key]
        else:
            raise Exception("There is no defined framework.\n")
    except Exception, e:
        self.ShowErrorMessage("Error when getParameterValue\n%s" % e)
        # raise Exception("Error while getting parameter value: %s" % e)
