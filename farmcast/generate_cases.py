import numpy as np
import os, shutil
from farmcast.write_fastfarm_fsft import generate_fsft
from farmcast.write_turbsim_in import write_turbsim_in
from farmcast.generate_openfast import generate_openfast
from farmcast.turbsim import set_turbsim
from farmcast.generate_turbsim_timesr import generateTimeSeriesFile, read_turbsim_bts
from farmcast.utils import getMultipleOf

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
                   domain_edge_LR = [1., 1.],
                   domain_edge_HR = [0.3, 0.3], # extra spacing along x (left and right) and y (top and bottom ) in D
                   cmax = 5.,
                   Mod_Wake = 2,  # 1: Polar, 2: Curled, 3: Cartesian
                   desired_OF_timestep=0.25,
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
    NumGrid_Z_LR, NumGrid_Y_LR, GridHeight_LR, GridWidth_LR, AnalysisTime_LR, \
    TimeStep_LR, HubHt_for_TS_LR = set_turbsim(
        n_turbines, rotor_diameter, hub_height, ws, spacing, wind_direction, 
        domain_edge=domain_edge_LR, dy=10., dz=10., res='low', TimeStep_HR=desired_OF_timestep,
    )

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
                    fst_vt["TurbSim"]["NumGrid_Z"] = NumGrid_Z_LR
                    fst_vt["TurbSim"]["NumGrid_Y"] = NumGrid_Y_LR
                    fst_vt["TurbSim"]["URef"] = ws_i
                    fst_vt["TurbSim"]["IECturbc"] = TI_i*100.
                    fst_vt["TurbSim"]["PLExp"] = shear_i
                    fst_vt["TurbSim"]["RefHt"] = hub_height
                    fst_vt["TurbSim"]["HubHt"] = HubHt_for_TS_LR
                    fst_vt["TurbSim"]["GridHeight"] = GridHeight_LR 
                    fst_vt["TurbSim"]["GridWidth"] = GridWidth_LR
                    fst_vt["TurbSim"]["TimeStep"] = TimeStep_LR
                    fst_vt["TurbSim"]["AnalysisTime"] = AnalysisTime_LR
                    fst_vt["TurbSim"]["TurbModel"] = "IECKAI"
                    fst_vt["TurbSim"]["UserFile"] = "unused"
                    turbsim_lr.append(ts_lr_filename)
                    write_turbsim_in(fst_vt, ts_lr_filename)

                    bts_low = ts_lr_filename[:-3] + ".bts"
                    meanU_Low = 1.
                    if os.path.exists(bts_low):
                        bts_data_low = read_turbsim_bts(bts_low)
                        iz = np.argmin(abs(bts_data_low['z'] - hub_height))
                        meanU_Low = np.mean(bts_data_low['u'][0,:,0,iz])

                    for spacing_i in spacing:
                        for wd_i in wind_direction:
                            # Get the turbine coordinates
                            WT_X = [
                                0,
                                spacing_i * rotor_diameter * np.cos(np.radians(wd_i)),
                                2 * spacing_i * rotor_diameter * np.cos(np.radians(wd_i))
                            ]
                            WT_Y = [
                                0,
                                spacing_i * rotor_diameter * np.sin(np.radians(wd_i)),
                                2 * spacing_i * rotor_diameter * np.sin(np.radians(wd_i))
                            ]
                            
                            # Now do turbsim high res for each turbine
                            for T in range(1, n_turbines + 1):
                                # If .bts files exist, generate the time series file
                                ts_lr_bts = ts_lr_filename[:-3] + ".bts"
                                TimeStep_HR = desired_OF_timestep
                                
                                if os.path.exists(ts_lr_bts):
                                    # Generate the time series file at the locations x and y
                                    x = WT_X[T-1] - domain_edge_LR[0] * rotor_diameter
                                    y = WT_Y[T-1]
                                    z = hub_height
                                    ymid = y
                                    zmid = 1. + 0.5*GridHeight_LR
                                    AnalysisTime_HR = generateTimeSeriesFile(ts_lr_bts, x, y, z, ymid, zmid, TimeStep_HR, AnalysisTime_LR, T)
                                else:
                                    AnalysisTime_HR = AnalysisTime_LR
                                

                                NumGrid_Z_HR, NumGrid_Y_HR, GridHeight_HR, GridWidth_HR, \
                                _, _, HubHt_for_TS_HR = set_turbsim(
                                    n_turbines, rotor_diameter, hub_height, ws, spacing, 
                                    wind_direction, domain_edge=domain_edge_HR, dy=5., dz=5., res='high'
                                )
                                
                                ts_hr_filename = os.path.join(inflow_dir, "ws%.2f_s%u_TI%.2f_shear%.2f_T%u.in" % (ws_i, seed, TI_i, shear_i, T))
                                fst_vt["TurbSim"]["RandSeed1"] = seedValues[seed]
                                fst_vt["TurbSim"]["NumGrid_Z"] = NumGrid_Z_HR
                                fst_vt["TurbSim"]["NumGrid_Y"] = NumGrid_Y_HR
                                fst_vt["TurbSim"]["URef"] = ws_i
                                fst_vt["TurbSim"]["IECturbc"] = TI_i*100.
                                fst_vt["TurbSim"]["PLExp"] = shear_i
                                fst_vt["TurbSim"]["RefHt"] = hub_height
                                fst_vt["TurbSim"]["HubHt"] = HubHt_for_TS_HR
                                # GridHeight_HR = GridHeight_LR
                                fst_vt["TurbSim"]["GridHeight"] = GridHeight_HR
                                # GridWidth_HR = GridHeight_HR # (1. + domain_edge_HR[1]) * rotor_diameter
                                fst_vt["TurbSim"]["GridWidth"] = GridWidth_HR 
                                fst_vt["TurbSim"]["TimeStep"] = TimeStep_HR
                                fst_vt["TurbSim"]["AnalysisTime"] = AnalysisTime_HR
                                fst_vt["TurbSim"]["TurbModel"] = "TIMESR"
                                UserFile = "\"" + ts_hr_filename[:-3] + ".txt" + "\""
                                fst_vt["TurbSim"]["UserFile"] = UserFile
                                turbsim_hr.append(ts_hr_filename)
                                write_turbsim_in(fst_vt, ts_hr_filename)



                            # Set ambient wind parameters
                            # Low res first
                            dT_High = TimeStep_HR
                            dt_low_desired = 1.
                            dT_Low = getMultipleOf(dt_low_desired, multipleof=dT_High)


                            bts_high = ts_hr_filename[:-3] + ".bts"
                            meanU_High = 1.
                            if os.path.exists(bts_high):
                                bts_data_high = read_turbsim_bts(bts_high)
                                iz = np.argmin(abs(bts_data_high['z'] - hub_height))
                                meanU_High = np.mean(bts_data_high['u'][0,:,0,iz])

                            dX_High = meanU_High*dT_High
                            dX_High = round(cmax/dX_High) * dX_High
                            dX_Low = getMultipleOf(meanU_Low*dT_Low, multipleof=dX_High)
                            if dX_Low == 0.:
                                dX_Low = dX_High
                            NY_Low = NumGrid_Y_LR
                            NZ_Low = NumGrid_Z_LR
                            
                            dY_Low = GridWidth_LR / (NY_Low - 1)
                            dZ_Low = GridHeight_LR / (NZ_Low - 1)
                        
                            X0_Low = getMultipleOf(np.min(WT_X) - domain_edge_LR[0] * rotor_diameter, multipleof=dX_Low)
                            Y0_Low = - GridWidth_LR * 0.5
                            Z0_Low = 1.
                        
                            XMax_Low = getMultipleOf(np.max(WT_X) + domain_edge_LR[0] * rotor_diameter, multipleof=dX_Low)
                            LX_Low = XMax_Low-X0_Low
                        
                            NX_Low = int(np.ceil(LX_Low/dX_Low)+1)                


                            # Now high res

                            LX_High = (1.+ domain_edge_HR[0]) * rotor_diameter
                            LY_High = GridWidth_HR
                            LZ_High = GridHeight_HR 
                                                    
                            
                            NX_High = int(np.ceil(LX_High/dX_High) + 1)
                            dX_High = [dX_High, dX_High, dX_High]
                            NY_High = fst_vt["TurbSim"]["NumGrid_Y"]
                            NZ_High = fst_vt["TurbSim"]["NumGrid_Z"]

                            dY_High_f = LY_High / (NY_High - 1)
                            dZ_High_f = LZ_High / (NZ_High - 1)
                            dY_High = [dY_High_f, dY_High_f, dY_High_f]
                            dZ_High = [dZ_High_f, dZ_High_f, dZ_High_f]
                        
                        
                            # --- High-res location per turbine
                            X0_desired = np.asarray(WT_X)-LX_High/2  # high-res is centered on turbine location
                            Y0_desired = np.asarray(WT_Y)-LY_High/2   # high-res is centered on turbine location
                            X0_High = (X0_Low + np.floor((X0_desired-X0_Low)/dX_High)*dX_High).tolist()
                            Y0_High = Y0_desired.tolist() # (Y0_Low + np.floor((Y0_desired-Y0_Low)/dY_High)*dY_High).tolist()
                            Z0_High = [Z0_Low, Z0_Low, Z0_Low]


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
                                        fst_vt["FASTFarm"]["DT_Low"] = TimeStep_LR
                                        fst_vt["FASTFarm"]["DT_High"] = TimeStep_HR
                                        fst_vt["FASTFarm"]["NX_Low"] = NX_Low
                                        fst_vt["FASTFarm"]["NY_Low"] = NY_Low
                                        fst_vt["FASTFarm"]["NZ_Low"] = NZ_Low
                                        fst_vt["FASTFarm"]["X0_Low"] = X0_Low
                                        fst_vt["FASTFarm"]["Y0_Low"] = Y0_Low
                                        fst_vt["FASTFarm"]["Z0_Low"] = Z0_Low
                                        fst_vt["FASTFarm"]["dX_Low"] = dX_Low
                                        fst_vt["FASTFarm"]["dY_Low"] = dY_Low
                                        fst_vt["FASTFarm"]["dZ_Low"] = dZ_Low
                                        fst_vt["FASTFarm"]["NX_High"] = NX_High
                                        fst_vt["FASTFarm"]["NY_High"] = NY_High
                                        fst_vt["FASTFarm"]["NZ_High"] = NZ_High
                                        fst_vt["FASTFarm"]["WT_X"] = WT_X
                                        fst_vt["FASTFarm"]["WT_Y"] = WT_Y
                                        fst_vt["FASTFarm"]["WT_Z"] = [0, 0, 0]
                                        output_path_openfast = os.path.join(case_dir, "openfast")
                                        fst_vt["FASTFarm"]["InflowFile"] = os.path.join(output_path_openfast, model + "_InflowFile.dat")
                                        fst_vt["FASTFarm"]["WT_FASTInFile"] = ["../openfast/%s_T1.fst"%(model),
                                                                    "../openfast/%s_T2.fst"%(model),
                                                                    "../openfast/%s_T3.fst"%(model)]
                                        fst_vt["FASTFarm"]["X0_High"] = X0_High
                                        fst_vt["FASTFarm"]["Y0_High"] = Y0_High
                                        fst_vt["FASTFarm"]["Z0_High"] = Z0_High
                                        fst_vt["FASTFarm"]["dX_High"] = dX_High
                                        fst_vt["FASTFarm"]["dY_High"] = dY_High
                                        fst_vt["FASTFarm"]["dZ_High"] = dZ_High
                                        fst_vt["FASTFarm"]["WrDisDT"] = TimeStep_LR

                                        fst_vt["FASTFarm"]["Mod_Wake"] = Mod_Wake
                                        if fst_vt["FASTFarm"]["Mod_Wake"] == 1: # Polar model
                                            dr = 5.
                                        else: # Curled; Cartesian
                                            dr = round(rotor_diameter/15)
                                        fst_vt["FASTFarm"]['dr'] = dr
                                        fst_vt["FASTFarm"]['NumRadii']  = int(np.ceil(3*rotor_diameter/(2*dr) + 1))
                                        fst_vt["FASTFarm"]['NumPlanes'] = int(np.ceil(20*rotor_diameter/(TimeStep_LR*ws_i*(1-1/6))))
                                        fst_vt["FASTFarm"]['f_c'] = 1.28*ws_i/rotor_diameter

                                        
                                        os.makedirs(os.path.join(case_dir, "fastfarm"), exist_ok=True)
                                        output_path_fsft = os.path.join(case_dir, "fastfarm", "generated.fstf")
                                        generate_fsft(fst_vt, output_path_fsft)

                                        # Generate OpenFAST input files
                                        os.makedirs(output_path_openfast, exist_ok=True)
                                        generate_openfast(model, yaw_T1, yaw_T2, curtailment, output_path_openfast, ts_lr_filename)
                                        
                                        # Create n_turbines copies of the rosco .so file
                                        rosco_dir = os.path.join(case_dir, "rosco")
                                        os.makedirs(rosco_dir, exist_ok=True)
                                        for i in range(1, n_turbines + 1):
                                            src = os.path.join(base_dir, "turbines", "rosco", "libdiscon.so")
                                            dst = os.path.join(rosco_dir, f"libdiscon_T{i}.so")
                                            if os.path.exists(src):
                                                os.system(f"cp {src} {dst}")
                                        
                                        # Rename the .bts files to Low and High
                                        case_inflow_dir = os.path.join(case_dir, "inflow")
                                        os.makedirs(case_inflow_dir, exist_ok=True)
                                        bts_file_lr = ts_lr_filename[:-3] + ".bts"
                                        symlink_lr = os.path.join(case_inflow_dir, "Low.bts")
                                        if os.path.exists(bts_file_lr) and not os.path.exists(symlink_lr):
                                            os.symlink(bts_file_lr, symlink_lr)
                                        for T in range(1, n_turbines + 1):
                                            bts_file_hr = ts_hr_filename[:-4] + f"{T}.bts"
                                            symlink_hr = os.path.join(case_inflow_dir, f"HighT{T}.bts")
                                            if os.path.exists(bts_file_hr) and not os.path.exists(symlink_hr):
                                                os.symlink(bts_file_hr, symlink_hr)


                                        # Print the case information to a yaml file
                                        case_info_filename = os.path.join(case_dir, "case_info.yaml")
                                        with open(case_info_filename, "w") as f:
                                            f.write("# Case information\n")
                                            for key, value in case.items():
                                                f.write(f"{key}: {value}\n")

                                        counter += 1

    return turbsim_lr, turbsim_hr