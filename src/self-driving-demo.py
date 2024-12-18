import requests
import os
import shutil
import json
import pandas as pd
import yaml

import utils, request_models

# TODO: to clean up later: the datasets and the files grow as self-driving loop continues. Currently, the models use all files and data instead of 
# the newly added ones for each iteration. It does unnecessary model inferences. I will clean this up later. 

################### FILE PATHS ###################
with open("../configs/self-driving-demo.yaml", "r") as f:
    config = yaml.safe_load(f)

protein_file_path = config['paths']['protein_file_path']
diffdock_output_dir = config['paths']['diffdock_output_dir']
dsmbind_input_dir = config['paths']['dsmbind_input_dir']

starting_molecule_csv = config['paths']['starting_molecule_csv']
molmim_generated_csv = config['paths']['molmim_generated_csv']
dsmbind_predictions_csv = config['paths']['dsmbind_predictions_csv']
results_csv = config['paths']['results_csv']

################### PREPARE FILES ###################
utils.prepare_output_directory(diffdock_output_dir)
utils.prepare_output_directory(dsmbind_input_dir)
utils.delete_folders_in_folder(diffdock_output_dir)
utils.delete_folders_in_folder(dsmbind_input_dir)

utils.delete_datasets(molmim_generated_csv)
utils.delete_datasets(dsmbind_predictions_csv)
utils.delete_datasets(results_csv)

# Get folded protein
folded_protein = utils.file_to_json_compatible_string(protein_file_path)

# Get starting molecules
df_starting_molecules = pd.read_csv(starting_molecule_csv)


################### BASIC RUN: ROUND 0 ###################
# Round 0
print("Round 0")
molecule_name = df_starting_molecules['Molecules'][0]
molecule = df_starting_molecules['Smiles'][0]

# Molecular Generation with MolMIM
molmim_response = request_models.call_molmim(molecule)
generated_ligands = '\n'.join([v['smiles'] for v in molmim_response['generated']])
utils.update_dataframe_molmim_generated_molecules(molmim_response['generated'], molecule_name)

# Protein-Ligand Docking with DiffDock
diffdock_response = request_models.call_diffdock(folded_protein, generated_ligands)
utils.create_diffdock_outputs_dsmbind_inputs(molecule_name, diffdock_response)

# Binding Affinity with DSMBind
os.system("python /workspace/bionemo/examples/molecule/dsmbind/infer.py")

df_molmim = pd.read_csv(molmim_generated_csv) 
df_dsmbind = pd.read_csv(dsmbind_predictions_csv)
df_joined = pd.concat([df_molmim, df_dsmbind], axis=1)

df_joined.to_csv('../data/results.csv')

threshold_binding_affinity = config['threshold_binding_affinity']
threshold_for_number_of_selected_molecules = config['threshold_for_number_of_selected_molecules']

################### SELF-DRIVING LOOP STARTING ###################
rd = 0
while len(df_joined[df_joined['DSMBind_predictions'] < threshold_binding_affinity]) < threshold_for_number_of_selected_molecules:
    rd = rd + 1
    print(f"Round {rd}")

    molecule_name = df_starting_molecules['Molecules'][rd]
    molecule = df_starting_molecules['Smiles'][rd]

    # Molecular Generation with MolMIM
    print("MolMIM...")
    molmim_response = request_models.call_molmim(molecule)
    generated_ligands = '\n'.join([v['smiles'] for v in molmim_response['generated']])
    utils.update_dataframe_molmim_generated_molecules(molmim_response['generated'], molecule_name)

    # Protein-Ligand Docking with DiffDock
    print("DiffDock...")
    diffdock_response = request_models.call_diffdock(folded_protein, generated_ligands)
    utils.create_diffdock_outputs_dsmbind_inputs(molecule_name, diffdock_response)

    # Binding Affinity with DSMBind
    print("DSMBind...")
    os.system("python /workspace/bionemo/examples/molecule/dsmbind/infer.py")

    df_molmim = pd.read_csv(molmim_generated_csv) 
    df_dsmbind = pd.read_csv(dsmbind_predictions_csv)
    df_joined = pd.concat([df_molmim, df_dsmbind], axis=1)

    df_joined.to_csv('../data/results.csv')

