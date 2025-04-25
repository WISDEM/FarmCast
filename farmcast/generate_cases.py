import numpy as np
import os
from farmcast.write_fastfarm_fsft import generate_fsft
from farmcast.write_turbsim_in import write_turbsim_in
from farmcast.generate_openfast import generate_openfast

run_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(run_dir)

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
    fst_vt = {}
    fst_vt["TurbSim"] = {}
    fst_vt["FASTFarm"] = {}
    for ws_i in ws:
        for TI_i in TI:
            for shear_i in shear:
                # Create an inflow directory for each inflow case
                turbsim_filename = os.path.join(inflow_dir, "ws%.2f_TI%.2f_shear%.2f.in" % (ws_i, TI_i, shear_i))
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
                                    case_dir = os.path.join(output_dir, "cases", f"case_{counter}")
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

    return None

def create_slurm_files(n_cases, n_turbines, output_dir, processors_per_node = 104, slurm_email = "username", alloc = "windse"):
    """
    Create SLURM job submission files for each case.

    Parameters
    ----------
    n_cases : int
        The total number of cases.
    n_turbines : int
        The number of turbines in the farm.
    output_dir : str
        The directory where the SLURM files will be created.
    processors_per_node : int, optional
        The number of processors per node. Default is 104 (DOE's HPC Kestrel).
    slurm_email : str, optional
        The email address for SLURM notifications. Default is "username".
    alloc : str, optional
        The SLURM allocation name. Default is "windse".
    Returns
    -------
    None
    """

    n_runs_per_node = processors_per_node // n_turbines
    n_slumrm_files = min([1, n_cases // n_runs_per_node])
    
    # Create a directory for SLURM files
    slurm_dir = os.path.join(output_dir, "slurm_files")
    os.makedirs(slurm_dir, exist_ok=True)

    # Create SLURM files for each case
    for i in range(n_slumrm_files):
        slurm_filename = os.path.join(slurm_dir, f"slurm_job_{i}.sh")
        with open(slurm_filename, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"#SBATCH --account={alloc}\n")
            f.write("#SBATCH --time=01:00:00\n")
            f.write("#SBATCH --nodes=1\n")
            f.write(f"#SBATCH --job-name=FarmCast_{i}\n")
            f.write(f"#SBATCH --mail-user {slurm_email}\n")
            f.write("#SBATCH --mail-type BEGIN,END,FAIL\n")
            f.write("######SBATCH --partition=debug\n")
            f.write("######SBATCH --qos=high\n")
            f.write("######SBATCH --mem=1000GB      # RAM in MB\n")
            f.write("#SBATCH --output=job_log.%j.out  # %j will be replaced with the job ID\n")

            f.write("\n")
            f.write("module purge\n")
            f.write("module load tmux intel-oneapi-mkl/2023.2.0-intel mamba\n")
            f.write("cd $SLURM_SUBMIT_DIR\n")
            for j in range(n_runs_per_node):
                id_case = i*n_runs_per_node+j
                f.write(f"fastfarm ../cases/case_{id_case}/fastfarm/generated.fstf\n")
            f.close()
    return None