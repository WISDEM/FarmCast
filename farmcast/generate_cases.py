import numpy as np
import os
from farmcast.write_fastfarm_fsft import generate_fsft
from farmcast.write_turbsim_in import write_turbsim_in
from farmcast.curtailment import set_rosco_curtailment

run_dir = os.path.dirname(os.path.realpath(__file__))


def generate_cases(n_turbines=3,
                   model="IEA-3.4-130-RWT",
                   diameter=130.,
                   ws=[6., 8., 10., 12.],
                   TI=[0.06, 0.12],
                   shear=[0.2],
                   spacing=[4., 6.],
                   wind_direction=np.arange(-8., 8., 4.),
                   T1_yaw_misalignment=np.arange(-30., 30., 10.),
                   T2_yaw_misalignment=np.arange(-20., 20., 10.),
                   curtailment_T1T2=np.arange(20., 100., 5.),
                   output_dir=run_dir):


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

                                    # Compute WT_X and WT_Y arrays based on spacing and wind direction
                                    WT_X = [
                                        -spacing_i * diameter * np.cos(np.radians(wd_i)),
                                        0,
                                        spacing_i * diameter * np.cos(np.radians(wd_i))
                                    ]
                                    WT_Y = [
                                        -spacing_i * diameter * np.sin(np.radians(wd_i)),
                                        0,
                                        spacing_i * diameter * np.sin(np.radians(wd_i))
                                    ]
                                    fst_vt = {}
                                    fst_vt["FASTFarm"]["WT_X"] = WT_X
                                    fst_vt["FASTFarm"]["WT_Y"] = WT_Y
                                    fst_vt["FASTFarm"]["WT_Z"] = [0, 0, 0]
                                    fst_vt["FASTFarm"]["WT_FASTInFile"] = ["../turbines/%s/%s_T1.fst"%(model,model),
                                                                "../turbines/%s/%s_T2.fst"%(model,model),
                                                                "../turbines/%s/%s_T3.fst"%(model,model)]
                                    fst_vt["FASTFarm"]["X0_High"] = WT_X-60.
                                    fst_vt["FASTFarm"]["Y0_High"] = WT_Y - 80.
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
