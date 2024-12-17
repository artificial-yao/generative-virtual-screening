import requests
import os
import shutil
import json
import pandas as pd
import yaml

import utils, request_models


######## File paths ########
with open("../configs/self-driving-demo.yaml", "r") as f:
    config = yaml.safe_load(f)

protein_file_path = config['paths']['protein_file_path']
diffdock_output_dir = config['paths']['diffdock_output_dir']
dsmbind_input_dir = config['paths']['diffdock_output_dir']

starting_molecule_csv = config['paths']['starting_molecule_csv']
molmim_generated_csv = config['paths']['molmim_generated_csv']
dsmbind_predictions_csv = config['paths']['dsmbind_predictions_csv']

utils.prepare_output_directory(diffdock_output_dir)
utils.prepare_output_directory(dsmbind_input_dir)

# Get folded protein
folded_protein = utils.file_to_json_compatible_string(protein_file_path)

# Get starting molecules
df_starting_molecules = pd.read_csv(starting_molecule_csv)

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

binding_affinity_threshold = config['binding_affinity_threshold']
if len(df_joined[df_joined['DSMBind_predictions'] < binding_affinity_threshold]) < 5:
    print("yes")

