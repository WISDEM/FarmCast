from farmcast.write_fastfarm_fsft import generate_fsft
from farmcast.write_turbsim_in import write_turbsim_in
from farmcast.curtailment import set_rosco_curtailment
import os
import numpy as np

run_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(run_dir)

# Set the output directory for the generated files
output_dir = os.path.join(os.path.dirname(base_dir), "FarmCast_runs")

# Turbines in the farm
n_turbines = 3
model = "IEA-3.4-130-RWT"
# Array of wind speeds in m/s
ws = [6., 8., 10., 12.]
 # Array of turbulence intensities
TI = [0.06, 0.12]
# Array of shear coefficients
shear = [0.2]
# Array of turbine spacing in rotor diameters
spacing = [4., 6.]
# Array of wind directions in degrees
wind_direction = np.arange(-8., 8., 4.)
# Array of yaw misalignments for the upstream turbine (T1) in degrees
T1_yaw_misalignment = np.arange(-30., 30., 10.)
# Array of yaw misalignments for the middle turbine (T2) in degrees
T2_yaw_misalignment = np.arange(-20., 20., 10.)
# Array of curtailment values for T1 and T2 in percentage
curtailment_T1T2 = np.arange(20., 100., 5.)

# Create the matrix of cases
cases = []
counter = 0
for ws_i in ws:
    for TI_i in TI:
        for shear_i in shear:
            for spacing_i in spacing:
                for wd_i in wind_direction:
                    for yaw_T1 in T1_yaw_misalignment:
                        for yaw_T2 in T2_yaw_misalignment:
                            for curtailment in curtailment_T1T2:
                                case = {
                                    "wind_speed": ws_i,
                                    "turbulence_intensity": TI_i,
                                    "shear": shear_i,
                                    "spacing": spacing_i,
                                    "wind_direction": wd_i,
                                    "T1_yaw_misalignment": yaw_T1,
                                    "T2_yaw_misalignment": yaw_T2,
                                    "curtailment_T1T2": curtailment,
                                    "counter": counter
                                }
                                cases.append(case)
                                # Create a directory for each case
                                case_dir = os.path.join(output_dir, f"case_{counter}")
                                os.makedirs(case_dir, exist_ok=True)

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
                                
                                
                                counter += 1

                                # Generate a TurbSim input file based on the provided ts_vt dictionary.
                                output_path_tsin = os.path.join(base_dir, "inflow", "inflow_T1.in")
                                fst_vt["TurbSim"] = {}
                                write_turbsim_in(fst_vt, output_path_tsin)

                                # Curtail power in rosco
                                path2discon = os.path.join(base_dir, "turbines", "IEA-3.4-130-RWT", "IEA-3.4-130-RWT_DISCON.IN")
                                set_rosco_curtailment(path2discon, curtailment)


print("All %d cases generated successfully in the folder %s"%(counter, case_dir))