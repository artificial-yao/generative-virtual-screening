import os
import shutil
import json

# reading in the input PDB/SDF/SMILES files as a string to be used for JSON request
def file_to_json_compatible_string(file_path):
    """
    Convert PDB file and sdf file to JSON
    """
    with open(file_path, 'r') as file:
        content_str = file.read()
    return content_str

def update_dataframe_molmim_generated_molecules(molmim_generated, 
                                                starting_molecule_name, 
                                                molmim_generated_csv = '../data/molmim_generated_molecules.csv',
                                                store_dataframe=True):
    import pandas as pd

    df = pd.DataFrame(molmim_generated)
    # Reset the index and make it a column
    df.reset_index(inplace=True)
    df.rename(columns={'smiles':'generated_smiles',
                    'score':'molmim_qed_score',
                    'index':'generated_compound_index'},
                    inplace=True)
    df['starting_molecule'] = starting_molecule_name

    if store_dataframe:
        df.to_csv(molmim_generated_csv, index=False)


# overwrite the output directory
def prepare_output_directory(output):
    """
    Prepare the output directory
    output: str, the output directory
    return: None
    """
    # overwrite the output directory
    # delete the output directory if it exists
    if os.path.exists(output):
        shutil.rmtree(output)
    os.makedirs(output)

# generate subfolders and files for diffdock outputs and dsmbind inputs
def create_diffdock_outputs_dsmbind_inputs(molecule_name,
                                           diffdock_response,
                                           diffdock_output_dir = "../data/diffdock_outputs/",
                                           dsmbind_input_dir = "../data/dsmbind_inputs",
                                           protein_file_path = "../data/protein_input_files/mpro_sarscov2.pdb"):
    for i in range(len(diffdock_response['ligand_positions'])):
        ligand_subfolder_name = molecule_name + "_compound" + str(i)
        ligand_subfolder_in_diffdock = os.path.join(diffdock_output_dir, ligand_subfolder_name)
        prepare_output_directory(ligand_subfolder_in_diffdock)
        with open(f"{diffdock_output_dir}/output.json", "w") as f:
            json.dump(diffdock_response, f)
        
        # save data in DSMBind input format
        ligand_subfolder_in_dsmbind = os.path.join(dsmbind_input_dir, ligand_subfolder_name)
        prepare_output_directory(ligand_subfolder_in_dsmbind)
        # Copy protein file into DSMBind subfolders
        shutil.copy(protein_file_path, ligand_subfolder_in_dsmbind) 

        # save ligand positions
        for j, ligand_geometry in enumerate(diffdock_response["ligand_positions"][i]):
            with open("{}/pose_{}.sdf".format(ligand_subfolder_in_diffdock, j), "w") as f:
                f.write(ligand_geometry)

            if j == 0: # Save the best position for scoring
                with open("{}/pose_{}.sdf".format(ligand_subfolder_in_dsmbind, j), "w") as f:
                    f.write(ligand_geometry)