from write_fastfarm_fsft import generate_fsft
from write_turbsim_in import write_turbsim_in
import os

run_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(run_dir)

fst_vt = {}
fst_vt["FASTFarm"] = {}
fst_vt["FASTFarm"]["WT_X"] = [-780, 0, 780]
fst_vt["FASTFarm"]["WT_Y"] = [0, 0, 0]
fst_vt["FASTFarm"]["WT_Z"] = [0, 0, 0]
fst_vt["FASTFarm"]["WT_FASTInFile"] = ["../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T1.fst",
                            "../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T2.fst",
                            "../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T3.fst"]
fst_vt["FASTFarm"]["X0_High"] = [-820, -40, 740]
fst_vt["FASTFarm"]["Y0_High"] = [-80, -80, -80]
fst_vt["FASTFarm"]["Z0_High"] = [5, 5, 5]
fst_vt["FASTFarm"]["dX_High"] = [5, 5, 5]
fst_vt["FASTFarm"]["dY_High"] = [10, 10, 10]
fst_vt["FASTFarm"]["dZ_High"] = [10, 10, 10]

output_path_fsft = os.path.join(base_dir, "fastfarm", "generated.FarmIEA3p4.fstf")
generate_fsft(fst_vt, output_path_fsft)

# Generate a TurbSim input file based on the provided ts_vt dictionary.
output_path_tsin = os.path.join(base_dir, "inflow", "inflow_T1.in")
fst_vt["TurbSim"] = {}
write_turbsim_in(fst_vt, output_path_tsin)