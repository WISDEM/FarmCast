import numpy as np
import os
from farmcast.write_fastfarm_fsft import generate_fsft
from farmcast.write_turbsim_in import write_turbsim_in
from farmcast.generate_openfast import generate_openfast
from farmcast.low_res_turbsim import set_low_res_turbsim
from farmcast.generate_turbsim_timesr import generateTimeSeriesFile


run_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(run_dir)

seedValues = [2318573, 122299, 123456, 389432, -432443, 9849898, 432425, 894832, 849324, 678095,
                1235456, 435342, 897023, 423800, -898881, 2988900, 798911, 482391, 892111, 899190,
                7693202, 587924, 890090, 435646, -454899, -785138, -78564, -17944, -99021, 389432]


def generate_cases(n_turbines=3,
                   model="IEA-3.4-130-RWT",
                   rotor_diameter=130.,
                   hub_height=110.,
                   ws=[6., 8., 10., 12.],
                   n_seeds = 6,
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
    fst_vt = {}
    fst_vt["TurbSim"] = {}
    fst_vt["FASTFarm"] = {}

    # Set the parameters for the low resolution TurbSim grid
    GridHeight_LR , GridWidth_LR, AnalysisTime_LR, TimeStep_LR = set_low_res_turbsim(n_turbines, rotor_diameter, ws, spacing, wind_direction)

    turbsim_lr = []
    turbsim_hr = []

    for ws_i in ws:
        for seed in range(n_seeds):
            for TI_i in TI:
                for shear_i in shear:
                    # Create an inflow directory for each inflow case
                    # Start with low resolution
                    ts_lr_filename = os.path.join(inflow_dir, "ws%.2f_s%u_TI%.2f_shear%.2f.in" % (ws_i, seed, TI_i, shear_i))
                    fst_vt["TurbSim"]["RandSeed1"] = seedValues[seed]
                    fst_vt["TurbSim"]["URef"] = ws_i
                    fst_vt["TurbSim"]["IECturbc"] = TI_i*100.
                    fst_vt["TurbSim"]["PLExp"] = shear_i
                    fst_vt["TurbSim"]["RefHt"] = hub_height
                    fst_vt["TurbSim"]["HubHt"] = hub_height
                    fst_vt["TurbSim"]["GridHeight"] = GridHeight_LR 
                    fst_vt["TurbSim"]["GridWidth"] = GridWidth_LR
                    fst_vt["TurbSim"]["TimeStep"] = TimeStep_LR
                    fst_vt["TurbSim"]["AnalysisTime"] = AnalysisTime_LR
                    turbsim_lr.append(ts_lr_filename)
                    write_turbsim_in(fst_vt, ts_lr_filename)
                    
                    for spacing_i in spacing:
                        for wd_i in wind_direction:
                            # Get the turbine coordinates
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
                            
                            # Now do turbsim high res for each turbine
                            for T in range(1, n_turbines + 1):
                                ts_hr_filename = os.path.join(inflow_dir, "ws%.2f_s%u_TI%.2f_shear%.2f_T%u.in" % (ws_i, seed, TI_i, shear_i, T))
                                fst_vt["TurbSim"]["RandSeed1"] = seedValues[seed]
                                fst_vt["TurbSim"]["URef"] = ws_i
                                fst_vt["TurbSim"]["IECturbc"] = TI_i*100.
                                fst_vt["TurbSim"]["PLExp"] = shear_i
                                fst_vt["TurbSim"]["RefHt"] = hub_height
                                fst_vt["TurbSim"]["HubHt"] = hub_height
                                fst_vt["TurbSim"]["GridHeight"] = 1.1 * rotor_diameter 
                                fst_vt["TurbSim"]["GridWidth"] = 1.1 * rotor_diameter
                                fst_vt["TurbSim"]["AnalysisTime"] = np.round(np.min([0.05, TimeStep_LR / 10]),2)
                                fst_vt["TurbSim"]["TurbModel"] = "TIMESR"
                                fst_vt["TurbSim"]["UserFile"] = ts_hr_filename[:-3] + "T%u.txt" % T
                                turbsim_hr.append(ts_hr_filename)
                                write_turbsim_in(fst_vt, ts_hr_filename)

                                # If .bts files exist, generate the time series file
                                if os.path.exists(ts_lr_filename[:-3] + ".bts"):
                                    # Generate the time series file
                                    generateTimeSeriesFile(ts_lr_filename, WT_X[T-1], WT_Y[T-1], hub_height, T)


                            for yaw_T1 in T1_yaw_misalignment:
                                for yaw_T2 in T2_yaw_misalignment:
                                    for curtailment in curtailment_T1T2:
                                        case = {
                                            "wind_speed": ws_i,
                                            "seed": seed,
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
                                        case_dir = os.path.join(output_dir, "cases", f"case_{counter}")
                                        os.makedirs(case_dir, exist_ok=True)

                                        # Generate .fsft file
                                        fst_vt["FASTFarm"]["WT_X"] = WT_X
                                        fst_vt["FASTFarm"]["WT_Y"] = WT_Y
                                        fst_vt["FASTFarm"]["WT_Z"] = [0, 0, 0]
                                        fst_vt["FASTFarm"]["WT_FASTInFile"] = ["../openfast/%s/%s_T1.fst"%(model,model),
                                                                    "../openfast/%s/%s_T2.fst"%(model,model),
                                                                    "../openfast/%s/%s_T3.fst"%(model,model)]
                                        fst_vt["FASTFarm"]["X0_High"] = [x - 60. for x in WT_X]
                                        fst_vt["FASTFarm"]["Y0_High"] = [x - 80. for x in WT_Y]
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
                                        
                                        # Create n_turbines copies of the rosco .so file
                                        rosco_dir = os.path.join(case_dir, "rosco")
                                        os.makedirs(rosco_dir, exist_ok=True)
                                        for i in range(1, n_turbines + 1):
                                            src = os.path.join(base_dir, "turbines", "rosco", "libdiscon.so")
                                            dst = os.path.join(rosco_dir, f"libdiscon_T{i}.so")
                                            if os.path.exists(src):
                                                os.system(f"cp {src} {dst}")
                                        
                                        # Print the case information to a yaml file
                                        case_info_filename = os.path.join(case_dir, "case_info.yaml")
                                        with open(case_info_filename, "w") as f:
                                            f.write("# Case information\n")
                                            for key, value in case.items():
                                                f.write(f"{key}: {value}\n")

                                        counter += 1

    return turbsim_lr, turbsim_hr