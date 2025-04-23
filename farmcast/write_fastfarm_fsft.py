from ruamel.yaml import YAML
import os
from validation import DefaultValidatingDraft7Validator

run_dir = os.path.dirname(os.path.realpath(__file__))
fastfarm_schema_path = os.path.join(run_dir, "fastfarm_schema.yaml")

def generate_fsft(fst_vt, output_path):
    """
    Generate a FAST.Farm input file based on the provided fst_vt dictionary.
    Args:
        fst_vt (dict): Dictionary containing the FAST.Farm input parameters.
        output_path (str): Path to the output FAST.Farm input file.
    """
    # Check if the output path is valid
    if not output_path.endswith('.fstf'):
        raise ValueError("Output path must end with '.fstf'")
    
    yaml = YAML(typ='safe')
    with open(fastfarm_schema_path, 'r') as schema_file:
        fastfarm_schema = yaml.load(schema_file)

    # Validate the input dictionary against the schema
    validator = DefaultValidatingDraft7Validator
    validator(fastfarm_schema).validate(fst_vt)

    # Extract key order and descriptions from the schema
    schema_properties = fastfarm_schema.get("properties", {}).get('FASTFarm', {}).get('properties', {})
    key_order = list(schema_properties.keys())
    descriptions = {key: schema_properties[key].get("description", "") for key in schema_properties}

    fsft_vt = fst_vt["FASTFarm"]

    with open(output_path, 'w') as fsft_file:
        fsft_file.write("------- FAST.Farm for OpenFAST INPUT FILE -------------------------------------------------\n")
        fsft_file.write("Sample FAST.Farm input file\n")
        fsft_file.write("--- SIMULATION CONTROL ---\n")
        
        for key in key_order:
            if key in fsft_vt and key not in ["NumTurbines", "WT_X", "WT_Y", "WT_Z", "WT_FASTInFile", "X0_High", "Y0_High", "Z0_High", "dX_High", "dY_High", "dZ_High"]:
                value = fsft_vt[key]
                if isinstance(value, list):
                    value = ', '.join(map(str, value))
                elif value is False:
                    value = "False"
                elif value is True:
                    value = "True"
                elif isinstance(value, str):
                    value = f"\"{value}\""
                description = descriptions.get(key, "")
                fsft_file.write(f"{str(value):<20} {key:<20} {description}\n")
                
                # Add section headers based on specific keys
                if key == "Mod_SharedMooring":
                    fsft_file.write("--- SUPER CONTROLLER --- [used only for UseSC=True]\n")
                elif key == "SC_FileName":
                    fsft_file.write("--- SHARED MOORING SYSTEM --- [used only for Mod_SharedMoor>0]\n")
                elif key == "WrMooringVis":
                    fsft_file.write("--- AMBIENT WIND: PRECURSOR IN VTK FORMAT --- [used only for Mod_AmbWind=1]\n")
                elif key == "ChkWndFiles":
                    fsft_file.write("--- AMBIENT WIND: INFLOWWIND MODULE --- [used only for Mod_AmbWind=2 or 3]\n")
                elif key == "InflowFile":
                    fsft_file.write("--- WIND TURBINES ---\n")
                    fsft_file.write("%d                  NumTurbines        - Number of wind turbines (-) [>=1]  [last 6 columns below used only for Mod_AmbWind=2 or 3]\n" % len(fsft_vt["WT_X"]))
                    fsft_file.write("WT_X    WT_Y   WT_Z    WT_FASTInFile\n")
                    fsft_file.write("(m)      (m)    (m)    (string)\n")
                    for i in range(len(fsft_vt["WT_X"])):
                        fsft_file.write(f"{fsft_vt['WT_X'][i]:<8} {fsft_vt['WT_Y'][i]:<8} {fsft_vt['WT_Z'][i]:<8} \"{fsft_vt['WT_FASTInFile'][i]}\" {fsft_vt['X0_High'][i]:<8} {fsft_vt['Y0_High'][i]:<8} {fsft_vt['Z0_High'][i]:<8} {fsft_vt['dX_High'][i]:<8} {fsft_vt['dY_High'][i]:<8} {fsft_vt['dZ_High'][i]:<8}\n")
                    fsft_file.write("--- WAKE DYNAMICS ---\n")
                elif key == "C_Meander":
                    fsft_file.write("--- CURLED-WAKE PARAMETERS [only used if Mod_Wake=2 or 3] ---\n")
                elif key == "Mod_Projection":
                    fsft_file.write("--- WAKE-ADDED TURBULENCE ---\n")
                elif key == "WAT_k_Grad":
                    fsft_file.write("--- VISUALIZATION ---\n")
                elif key == "WrDisDT":
                    fsft_file.write("--- OUTPUT ---\n")
            
            if key not in fsft_vt:
                raise Exception(f"Key '{key}' is not a valid FASTFarm input parameter.")
        
        fsft_file.write('END of input file (the word "END" must appear in the first 3 columns of this last OutList line)\n')
        fsft_file.close()

    print(f"FAST.Farm input file generated at {output_path}")

    return None
