import requests

#AF2_HOST = 'http://localhost:8081'
DIFFDOCK_HOST = 'http://localhost:8082'
MOLMIM_HOST = 'http://localhost:8083'

def call_molmim(molecule):
    molmim_response = requests.post(
        f'{MOLMIM_HOST}/generate',
        json={
            'smi': molecule,
            'num_molecules': 5,
            'algorithm': 'CMA-ES',
            'property_name': 'QED',
            'min_similarity': 0.7, # Ignored if algorithm is not "CMA-ES".
            'iterations': 10,
        }).json()
    return molmim_response

def call_diffdock(folded_protein, generated_ligands, ligand_file_type='txt'):
    diffdock_response = requests.post(
        f'{DIFFDOCK_HOST}/molecular-docking/diffdock/generate',
        json={
            'protein': folded_protein,
            'ligand': generated_ligands,
            'ligand_file_type': ligand_file_type,
            'num_poses': 10,
            'time_divisions': 20,
            'num_steps': 18,
        }).json()
    return diffdock_response
