from ruamel.yaml import YAML
from write_fastfarm_fsft import generate_fsft
from write_turbsim_in import write_turbsim_in
import os

run_dir = os.path.dirname(os.path.realpath(__file__))
fastfarm_schema_path = os.path.join(run_dir, "fastfarm_schema.yaml")
turbsim_schema_path = os.path.join(run_dir, "turbsim_schema.yaml")

yaml = YAML(typ='safe')
with open(fastfarm_schema_path, 'r') as schema_file:
    fastfarm_schema = yaml.load(schema_file)

fsft_vt = fastfarm_schema.get('properties', {}).get('FASTFarm', {}).get('properties', {})
fsft_vt["WT_X"] = [-780, 0, 780]
fsft_vt["WT_Y"] = [0, 0, 0]
fsft_vt["WT_Z"] = [0, 0, 0]
fsft_vt["WT_FASTInFile"] = ["../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T1.fst",
                            "../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T2.fst",
                            "../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T3.fst"]
fsft_vt["X0_High"] = [-820, -40, 740]
fsft_vt["Y0_High"] = [-80, -80, -80]
fsft_vt["Z0_High"] = [5, 5, 5]
fsft_vt["dX_High"] = [5, 5, 5]
fsft_vt["dY_High"] = [10, 10, 10]
fsft_vt["dZ_High"] = [10, 10, 10]

output_path_fsft = "/Users/pbortolo/work/3_projects/30_HolisticSE/FarmCast/fastfarm/generated.FarmIEA3p4.fstf"
generate_fsft(fsft_vt, output_path_fsft)


# Generate a TurbSim input file based on the provided fsft_vt dictionary.
output_path_tsin = os.path.join(run_dir, "inflow_T1.in")
yaml = YAML(typ='safe')
with open(turbsim_schema_path, 'r') as schema_file:
    turbsim_schema = yaml.load(schema_file)
turbsim_data = turbsim_schema.get('properties', {}).get('TurbSim', {}).get('properties', {})

write_turbsim_in(turbsim_data, output_path_tsin)

# # Run TurbSim in sequence
# wrapper = Turbsim_wrapper()
# wrapper.run_dir = wind_directory
# #run_dir = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ) ) ) + os.sep
# turbsim_exe = shutil.which('turbsim')
# wrapper.turbsim_exe = turbsim_exe
# wrapper.turbsim_input = output_path_tsin
# wrapper.execute()