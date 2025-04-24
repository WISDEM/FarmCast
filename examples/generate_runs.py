from farmcast.write_fastfarm_fsft import generate_fsft
from farmcast.write_turbsim_in import write_turbsim_in
from farmcast.curtailment import set_rosco_curtailment
import os
import numpy as np

run_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(run_dir)

n_turbines = 3
wind_speed = [6., 8., 10., 12.]
TI = [0.06, 0.12]
shear = [0.2]
spacing_D = [4., 6.]
wind_direction = np.arange(-8., 8., 4.)
T1_yaw_misalignment = np.arange(-30., 30., 10.)
T2_yaw_misalignment = np.arange(-20., 20., 10.)
curtailment_T1T2 = np.arange(20., 100., 5.)


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

# Curtail power in rosco
path2discon = os.path.join(base_dir, "turbines", "IEA-3.4-130-RWT", "IEA-3.4-130-RWT_DISCON.IN")
pc_curtailment = 80.0
set_rosco_curtailment(path2discon, pc_curtailment)