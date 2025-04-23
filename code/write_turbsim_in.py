from ruamel.yaml import YAML
import os

run_dir = os.path.dirname(os.path.realpath(__file__))
turbsim_schema_path = os.path.join(run_dir, "turbsim_schema.yaml")

def write_turbsim_in(turbsim, output_path):

    yaml = YAML(typ='safe')
    with open(turbsim_schema_path, 'r') as schema_file:
        turbsim_schema = yaml.load(schema_file)

    with open(output_path, 'w') as ts_file:
        ts_file.write("------- TurbSim Input File -------------------------------------------------\n")
        ts_file.write("Sample TurbSim input file\n")
        ts_file.write("--- SIMULATION CONTROL ---\n")
        
        for key, value in turbsim.items():
            default = value.get('default', '')
            if default is False:
                default = "False"
            elif default is True:
                default = "True"
            description = value.get('description', '').split('(')[0].strip()
            if isinstance(default, list):
                default = ', '.join(map(str, default))
            ts_file.write(f"{default:<20} {key:<20} - {description}\n")
            if key == 'ScaleIEC':
                ts_file.write("\n")
                ts_file.write("--------Turbine/Model Specifications-----------------------\n")
            elif key == 'TimeStep':
                ts_file.write("0.5            AnalysisTime    - Length of analysis time series [seconds] (program will add time if necessary: AnalysisTime = MAX(AnalysisTime, UsableTime+GridWidth/MeanHHWS) )\n")
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
