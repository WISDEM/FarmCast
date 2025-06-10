#!/bin/bash
#SBATCH --account=windse
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --job-name=FC_Ex
#SBATCH --mail-user pbortolo@nrel.gov
#SBATCH --mail-type BEGIN,END,FAIL
#####SBATCH --partition=debug
####SBATCH --qos=high
######SBATCH --mem=1000GB      # RAM in MB
#SBATCH --output=job_log.%j.out  # %j will be replaced with the job ID

module purge
module load tmux intel-oneapi-mkl/2023.2.0-intel mamba

conda activate farmcast-env

python create_surrogate_torque2024.py
