from farmcast.generate_cases import generate_cases
from farmcast.generate_slurm_files import create_slurm_ff_files, create_slurm_ts_files
import os
import numpy as np

run_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(run_dir)

# Set the username for Kestrel
hpc_email = 'pbortolo@nrel.gov'
path2turbsim = '/projects/windse/cbay/solvers/turbsim'
path2fastfarm = '/projects/windse/cbay/solvers/FAST.Farm'
path2controller = '/home/pbortolo/ROSCO/ROSCO_v2p9p7d/rosco/controller/build/libdiscon.so'

# Set the output directory for the generated files
output_dir = os.path.join(os.path.dirname(base_dir), "FarmCast_runs")
# output_dir = "/scratch/pbortolo/FarmCast_runs"

# Turbines in the farm
n_turbines = 3
model = "IEA-3.4-130-RWT"
rotor_diameter = 130.0
hub_height = 110.0
# Array of wind speeds in m/s
ws = [10.]
# Number of seeds
n_seeds = 1
 # Array of turbulence intensities
TI = [0.1]
# Array of shear coefficients
shear = [0.1]
# Array of turbine spacing in rotor diameters
spacing = [4.]
# Array of wind directions in degrees
wind_direction = np.arange(-8., 16., 8.)
# Array of yaw misalignments for the upstream turbine (T1) in degrees
T1_yaw_misalignment = np.arange(-30., 60., 30.)
# Array of yaw misalignments for the middle turbine (T2) in degrees
T2_yaw_misalignment = np.arange(-20., 40., 20.)
# Array of curtailment values for T1 and T2 in percentage
curtailment_T1T2 = np.arange(60., 140., 40.)
# Wake model
Mod_Wake = 2 # Curled, 1 Polar, 3 Cartesian

# Estimate the total number of cases
n_cases = len(ws) * n_seeds * len(TI) * len(shear) * len(spacing) * len(wind_direction) * len(T1_yaw_misalignment) * len(T2_yaw_misalignment) * len(curtailment_T1T2)
print(f"Total number of cases: {n_cases}")

# Generate the cases
turbsim_lr, turbsim_hr = generate_cases(
    n_turbines=n_turbines,
    model=model,
    rotor_diameter=rotor_diameter,
    hub_height=hub_height,
    ws=ws,
    n_seeds=n_seeds,
    TI=TI,
    shear=shear,
    spacing=spacing,
    wind_direction=wind_direction,
    T1_yaw_misalignment=T1_yaw_misalignment,
    T2_yaw_misalignment=T2_yaw_misalignment,
    curtailment_T1T2=curtailment_T1T2,
    output_dir=output_dir,
    Mod_Wake = Mod_Wake,
    path2controller=path2controller,
)

# Create the slurm files for low res turbsim
slurm_dir = os.path.join(output_dir, "slurm_files", "turbsim_lr")
create_slurm_ts_files(turbsim_lr, slurm_dir, slurm_email = hpc_email, path2turbsim = path2turbsim)
slurm_dir = os.path.join(output_dir, "slurm_files", "turbsim_hr")
create_slurm_ts_files(turbsim_hr, slurm_dir, slurm_email = hpc_email, path2turbsim = path2turbsim)

# Create the slurm files for each case
create_slurm_ff_files(n_cases, n_turbines, output_dir, slurm_email = hpc_email, path2fastfarm = path2fastfarm)

print(f"All {n_cases} successfully generated in {output_dir}.")