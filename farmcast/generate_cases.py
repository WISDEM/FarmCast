import numpy as np
import os
from farmcast.write_fastfarm_fsft import generate_fsft
from farmcast.write_turbsim_in import write_turbsim_in
from farmcast.curtailment import set_rosco_curtailment
from farmcast.generate_openfast import generate_openfast

run_dir = os.path.dirname(os.path.realpath(__file__))


def generate_cases(n_turbines=3,
                   model="IEA-3.4-130-RWT",
                   rotor_diameter=130.,
                   hub_height=110.,
                   ws=[6., 8., 10., 12.],
                   TI=[0.06, 0.12],
                   shear=[0.2],
                   spacing=[4., 6.],
                   wind_direction=np.arange(-8., 8., 4.),
                   T1_yaw_misalignment=np.arange(-30., 30., 10.),
                   T2_yaw_misalignment=np.arange(-20., 20., 10.),
                   curtailment_T1T2=np.arange(20., 100., 5.),
                   output_dir=run_dir):

    # Create inflow directory
    inflow_dir = os.path.join(output_dir, "inflows")
    os.makedirs(inflow_dir, exist_ok=True)

    # Create the matrix of cases
    cases = []
    counter = 0
    for ws_i in ws:
        for TI_i in TI:
            for shear_i in shear:
                # Create an inflow directory for each inflow case
                turbsim_filename = os.path.join(inflow_dir, "ws%u_TI%u_shear%u.in"%(ws_i, TI_i, shear_i))
                fst_vt["TurbSim"] = {}
                fst_vt["TurbSim"]["URef"] = ws_i
                fst_vt["TurbSim"]["IECturbc"] = TI_i*100.
                fst_vt["TurbSim"]["PLExp"] = shear_i
                fst_vt["TurbSim"]["RefHt"] = hub_height
                fst_vt["TurbSim"]["HubHt"] = hub_height
                fst_vt["TurbSim"]["GridHeight"] = 1.1*rotor_diameter
                fst_vt["TurbSim"]["GridWidth"] = 1.1*rotor_diameter
                write_turbsim_in(fst_vt, turbsim_filename)
                
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

                                    # Generate .fsft file
                                    WT_X = [
                                        -spacing_i * rotor_diameter * np.cos(np.radians(wd_i)),
                                        0,
                                        spacing_i * rotor_diameter * np.cos(np.radians(wd_i))
                                    ]
                                    WT_Y = [
                                        -spacing_i * rotor_diameter * np.sin(np.radians(wd_i)),
                                        0,
                                        spacing_i * rotor_diameter * np.sin(np.radians(wd_i))
                                    ]
                                    fst_vt = {}
                                    fst_vt["FASTFarm"]["WT_X"] = WT_X
                                    fst_vt["FASTFarm"]["WT_Y"] = WT_Y
                                    fst_vt["FASTFarm"]["WT_Z"] = [0, 0, 0]
                                    fst_vt["FASTFarm"]["WT_FASTInFile"] = ["../openfast/%s/%s_T1.fst"%(model,model),
                                                                "../openfast/%s/%s_T2.fst"%(model,model),
                                                                "../openfast/%s/%s_T3.fst"%(model,model)]
                                    fst_vt["FASTFarm"]["X0_High"] = WT_X-60.
                                    fst_vt["FASTFarm"]["Y0_High"] = WT_Y - 80.
                                    fst_vt["FASTFarm"]["Z0_High"] = [5, 5, 5]
                                    fst_vt["FASTFarm"]["dX_High"] = [5, 5, 5]
                                    fst_vt["FASTFarm"]["dY_High"] = [10, 10, 10]
                                    fst_vt["FASTFarm"]["dZ_High"] = [10, 10, 10]
                                    
                                    os.makedirs(os.path.join(case_dir, "fastfarm"), exist_ok=True)
                                    output_path_fsft = os.path.join(case_dir, "fastfarm", "generated.fstf")
                                    generate_fsft(fst_vt, output_path_fsft)

                                    # Generate OpenFAST input files
                                    output_path_openfast = os.path.join(case_dir, "openfast")
                                    os.makedirs(output_path_openfast, exist_ok=True)
                                    generate_openfast(model, yaw_T1, yaw_T2, curtailment, output_path_openfast)
                                    
                                    # Curtail power in rosco
                                    path2discon = os.path.join(case_dir, "turbines", "IEA-3.4-130-RWT", "IEA-3.4-130-RWT_DISCON.IN")
                                    set_rosco_curtailment(path2discon, curtailment)
                                    
                                    counter += 1





    print("All %d cases generated successfully in the folder %s"%(counter, case_dir))
