import os
import shutil
import json
import yaml

######## File paths ########
with open("../configs/self-driving-demo.yaml", "r") as f:
    config = yaml.safe_load(f)

protein_file_path = config['paths']['protein_file_path']
diffdock_output_dir = config['paths']['diffdock_output_dir']
dsmbind_input_dir = config['paths']['dsmbind_input_dir']

starting_molecule_csv = config['paths']['starting_molecule_csv']
molmim_generated_csv = config['paths']['molmim_generated_csv']
dsmbind_predictions_csv = config['paths']['dsmbind_predictions_csv']

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
                                                molmim_generated_csv = molmim_generated_csv):
    import pandas as pd

    df = pd.DataFrame(molmim_generated)
    # Reset the index and make it a column
    df.reset_index(inplace=True)
    df.rename(columns={'smiles':'generated_smiles',
                    'score':'molmim_qed_score',
                    'index':'generated_compound_index'},
                    inplace=True)
    df['starting_molecule'] = starting_molecule_name

    if os.path.exists(molmim_generated_csv):
        print("The CSV file exists.")
        df_old = pd.read_csv(molmim_generated_csv)
        df_merged = pd.concat([df_old, df], ignore_index=True)

        df_merged.to_csv(molmim_generated_csv, index=False)
    else:
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

# delete datasets
def delete_datasets(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    else:
        print(f"File '{file_path}' does not exist.")

# delete folders in folder
def delete_folders_in_folder(path):
    """Deletes all folders within the specified directory."""
    for entry in os.scandir(path):
        if entry.is_dir():
            shutil.rmtree(entry.path)

# generate subfolders and files for diffdock outputs and dsmbind inputs
def create_diffdock_outputs_dsmbind_inputs(molecule_name,
                                           diffdock_response,
                                           diffdock_output_dir = diffdock_output_dir,
                                           dsmbind_input_dir = dsmbind_input_dir,
                                           protein_file_path = protein_file_path):
    for i in range(len(diffdock_response['ligand_positions'])):
        ligand_subfolder_name = molecule_name + "_compound" + str(i)
        print("ligand subfolders are ", ligand_subfolder_name)
        # DiffDock subfolders
        ligand_subfolder_in_diffdock = os.path.join(diffdock_output_dir, ligand_subfolder_name)
        prepare_output_directory(ligand_subfolder_in_diffdock)
        with open(f"{diffdock_output_dir}/output.json", "w") as f:
            json.dump(diffdock_response, f)
        
        # DSMBind subfolders
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