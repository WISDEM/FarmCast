from ruamel.yaml import YAML
import os
from farmcast.validation import DefaultValidatingDraft7Validator

run_dir = os.path.dirname(os.path.realpath(__file__))
turbsim_schema_path = os.path.join(run_dir, "turbsim_schema.yaml")

def write_turbsim_in(fst_vt, output_path):

    yaml = YAML(typ='safe')
    with open(turbsim_schema_path, 'r') as schema_file:
        turbsim_schema = yaml.load(schema_file)
    
    # Validate the input dictionary against the schema
    validator = DefaultValidatingDraft7Validator
    validator(turbsim_schema).validate(fst_vt)

    # Extract key order and descriptions from the schema
    schema_properties = turbsim_schema.get("properties", {}).get('TurbSim', {}).get('properties', {})
    key_order = list(schema_properties.keys())
    descriptions = {key: schema_properties[key].get("description", "") for key in schema_properties}

    ts_vt = fst_vt["TurbSim"]

    with open(output_path, 'w') as ts_file:
        ts_file.write("------- TurbSim Input File -------------------------------------------------\n")
        ts_file.write("Sample TurbSim input file\n")
        ts_file.write("--- SIMULATION CONTROL ---\n")
        
        for key in key_order:
            value = ts_vt[key]
            if value is False:
                value = "False"
            elif value is True:
                value = "True"
            description = descriptions.get(key, "")
            
            if isinstance(value, list):
                value = ', '.join(map(str, value))
            ts_file.write(f"{value:<20} {key:<20} - {description}\n")
            if key == 'ScaleIEC':
                ts_file.write("\n")
                ts_file.write("--------Turbine/Model Specifications-----------------------\n")
            elif key == 'HFlowAng':
                ts_file.write("\n")
                ts_file.write("--------Meteorological Boundary Conditions-------------------\n")
            elif key == 'Z0':
                ts_file.write("\n")
                ts_file.write("--------Non-IEC Meteorological Boundary Conditions------------\n")
            elif key == 'PC_VW':
                ts_file.write("\n")
                ts_file.write("--------Spatial Coherence Parameters----------------------------\n")
            elif key == 'CohExp':
                ts_file.write("\n")
                ts_file.write("--------Coherent Turbulence Scaling Parameters-------------------\n")

    ts_file.close()

    print(f"Generated TurbSim input file at {output_path}")
