import os, shutil

run_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(run_dir)

def generate_openfast(model, yaw_T1, yaw_T2, curtailment, output_path_openfast, ts_lr_filename):

    """
    Generate OpenFAST input files for the given turbine model and yaw misalignment.

    Parameters
    ----------
    model : str
        The turbine model name.
    yaw_T1 : float
        The yaw misalignment for the first turbine in degrees.
    yaw_T2 : float
        The yaw misalignment for the second turbine in degrees.
    curtailment : float
        The curtailment value for the first and second turbines in percentage.
    output_path_openfast : str
        The path to the output directory for OpenFAST files.
    ts_lr_filename : str
        The filename of the low-resolution TurbSim file.
    Returns
    -------
    None
    """

    # Set source directory for OpenFAST input files
    source_dir = os.path.join(base_dir, "turbines", model)
    # Copy all files from source_dir to output_path_openfast
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist.")

    for file_name in os.listdir(source_dir):
        full_file_name = os.path.join(source_dir, file_name)
        if os.path.isfile(full_file_name):
            destination_file = os.path.join(output_path_openfast, file_name)
            with open(full_file_name, 'rb') as src, open(destination_file, 'wb') as dst:
                dst.write(src.read())

    # Create modified copies of the .fst file for T1, T2, and T3
    original_fst_file = os.path.join(output_path_openfast, f"{model}.fst")
    if not os.path.exists(original_fst_file):
        raise FileNotFoundError(f"Original .fst file '{original_fst_file}' does not exist.")
    # Create modified copies of the ElastoDyn file for T1, T2, and T3
    original_elastodyn_file = os.path.join(output_path_openfast, f"{model}_ElastoDyn.dat")
    if not os.path.exists(original_elastodyn_file):
        raise FileNotFoundError(f"Original .dat file '{original_elastodyn_file}' does not exist.")
    # InflowFile
    original_inflow_file = os.path.join(output_path_openfast, f"{model}_InflowFile.dat")
    modified_inflow_file = os.path.join(output_path_openfast, f"{model}_InflowFile_t.dat")
    with open(original_inflow_file, 'r') as src, open(modified_inflow_file, 'w') as ifst:
        for line in src:
            if "FileName_BTS" in line and "\"none\"" in line:
                line = line.replace("\"none\"", "../inflow/")
            ifst.write(line)
        ifst.close()
    shutil.move(modified_inflow_file, original_inflow_file)
    # Create modified copies of the ServoDyn file for T1, T2, and T3
    original_servodyn_file = os.path.join(output_path_openfast, f"{model}_ServoDyn.dat")
    if not os.path.exists(original_servodyn_file):
        raise FileNotFoundError(f"Original .dat file '{original_servodyn_file}' does not exist.")
    # Create modified copies of the DISCON file for T1, T2, and T3
    original_discon_file = os.path.join(output_path_openfast, f"{model}_DISCON.IN")
    if not os.path.exists(original_discon_file):
        raise FileNotFoundError(f"Original DISCON file '{original_discon_file}' does not exist.")
    # Create the three OpenFAST files for T1, T2, and T3
    for turbine_id in ["T1", "T2", "T3"]:
        # .fst
        modified_fst_file = os.path.join(output_path_openfast, f"{model}_{turbine_id}.fst")
        with open(original_fst_file, 'r') as src, open(modified_fst_file, 'w') as fst:
            for line in src:
                if "ElastoDyn.dat" in line:
                    line = line.replace("IEA-3.4-130-RWT_ElastoDyn.dat", f"IEA-3.4-130-RWT_ElastoDyn_{turbine_id}.dat")
                if "InflowFile.dat" in line:
                    line = line.replace("IEA-3.4-130-RWT_InflowFile.dat", f"IEA-3.4-130-RWT_InflowFile_{turbine_id}.dat")
                if "ServoDyn.dat" in line:
                    line = line.replace("IEA-3.4-130-RWT_ServoDyn.dat", f"IEA-3.4-130-RWT_ServoDyn_{turbine_id}.dat")
                
                fst.write(line.replace(f"{model}.fst", f"{model}_{turbine_id}.fst"))
            fst.close()
        # ElastoDyn
        modified_elastodyn_file = os.path.join(output_path_openfast, f"{model}_ElastoDyn_{turbine_id}.dat")
        with open(original_elastodyn_file, 'r') as src, open(modified_elastodyn_file, 'w') as edst:
            for line in src:
                if "NacYaw" in line:
                    if turbine_id == "T1":
                        line = line.replace("0.0                    NacYaw", f"{yaw_T1}                    NacYaw")
                    elif turbine_id == "T2":
                        line = line.replace("0.0                    NacYaw", f"{yaw_T2}                    NacYaw")
                    else:
                        line = line.replace("0.0                    NacYaw", "0.0                    NacYaw")
                edst.write(line.replace(f"{model}_ElastoDyn.dat", f"{model}_ElastoDyn_{turbine_id}.dat"))
            edst.close()
        # ServoDyn
        modified_servodyn_file = os.path.join(output_path_openfast, f"{model}_ServoDyn_{turbine_id}.dat")
        with open(original_servodyn_file, 'r') as src, open(modified_servodyn_file, 'w') as sdst:
            for line in src:
                if "DLL_FileName" in line:
                    line = line.replace("../rosco/libdiscon.so", f"../rosco/libdiscon_{turbine_id}.so")
                sdst.write(line.replace(f"{model}_ServoDyn.dat", f"{model}_ServoDyn_{turbine_id}.dat"))
            sdst.close()
        # DISCON
        modified_discon_file = os.path.join(output_path_openfast, f"{model}_DISCON_{turbine_id}.IN")
        with open(original_discon_file, 'r') as src, open(modified_discon_file, 'w') as dsrc:
            for line in src:
                if "PRC_R_Speed" in line:
                    if turbine_id == "T1" or turbine_id == "T2":
                        line = line.replace("1.00000", str(curtailment / 100.))
                dsrc.write(line.replace(f"{model}_DISCON.IN", f"{model}_DISCON_{turbine_id}.IN"))
            dsrc.close()