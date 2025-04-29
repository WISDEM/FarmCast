import os

def create_slurm_ff_files(n_cases, n_turbines, output_dir, processors_per_node = 104, slurm_email = "username", alloc = "windse"):
    """
    Create SLURM job submission files for each fastfarm case.

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
    n_slumrm_files = max([1, n_cases // n_runs_per_node])
    
    # Create a directory for SLURM files
    slurm_dir = os.path.join(output_dir, "slurm_files", "fastfarm")
    os.makedirs(slurm_dir, exist_ok=True)

    # Create SLURM files for each case
    for i in range(n_slumrm_files):
        slurm_filename = os.path.join(slurm_dir, f"slurm_job_{i}.sh")
        with open(slurm_filename, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"#SBATCH --account={alloc}\n")
            f.write("#SBATCH --time=01:00:00\n")
            f.write("#SBATCH --nodes=1\n")
            f.write(f"#SBATCH --job-name=FF_{i}\n")
            f.write(f"#SBATCH --mail-user {slurm_email}\n")
            f.write("#SBATCH --mail-type BEGIN,END,FAIL\n")
            f.write("######SBATCH --partition=debug\n")
            f.write("######SBATCH --qos=high\n")
            f.write("######SBATCH --mem=1000GB      # RAM in MB\n")
            f.write("#SBATCH --output=job_log.%j.out  # %j will be replaced with the job ID\n")

            f.write("\n")
            f.write("module purge\n")
            f.write("module load tmux intel-oneapi-mkl/2023.2.0-intel mamba\n")
            f.write("\n")
            
            for j in range(n_cases):
                id_case = i*n_cases+j
                f.write(f"fastfarm ../../cases/case_{id_case}/fastfarm/generated.fstf &\n")
            f.close()
    return None

def create_slurm_ts_files(turbsim_files, slurm_dir, processors_per_node = 104, slurm_email = "username", alloc = "windse"):

    n_cases = len(turbsim_files)
    n_slumrm_files = max([1, n_cases // processors_per_node])
    
    os.makedirs(slurm_dir, exist_ok=True)

    # Create SLURM files for each case
    for i in range(n_slumrm_files):
        slurm_filename = os.path.join(slurm_dir, f"slurm_job_{i}.sh")
        with open(slurm_filename, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"#SBATCH --account={alloc}\n")
            f.write("#SBATCH --time=01:00:00\n")
            f.write("#SBATCH --nodes=1\n")
            f.write(f"#SBATCH --job-name=TSLR_{i}\n")
            f.write(f"#SBATCH --mail-user {slurm_email}\n")
            f.write("#SBATCH --mail-type BEGIN,END,FAIL\n")
            f.write("######SBATCH --partition=debug\n")
            f.write("######SBATCH --qos=high\n")
            f.write("######SBATCH --mem=1000GB      # RAM in MB\n")
            f.write("#SBATCH --output=job_log.%j.out  # %j will be replaced with the job ID\n")

            f.write("\n")
            f.write("module purge\n")
            f.write("module load tmux intel-oneapi-mkl/2023.2.0-intel mamba\n")
            f.write("\n")
            
            for j in range(n_cases):
                id_case = i*n_cases+j
                f.write(f"turbsim {turbsim_files[id_case]} &\n")
            f.close()
    return None