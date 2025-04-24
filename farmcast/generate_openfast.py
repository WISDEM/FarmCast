import os

def generate_openfast(model, yaw_T1, yaw_T2, curtailment, output_path_openfast):

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
        The curtailment value for the turbines in percentage.
    output_path_openfast : str
        The path to the output directory for OpenFAST files.

    Returns
    -------
    None
    """

    run_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.dirname(run_dir)
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

    for turbine_id in ["T1", "T2", "T3"]:
        modified_fst_file = os.path.join(output_path_openfast, f"{model}_{turbine_id}.fst")
        with open(original_fst_file, 'r') as src, open(modified_fst_file, 'w') as dst:
            for line in src:
                if "ElastoDyn.dat" in line:
                    line = line.replace("IEA-3.4-130-RWT_ElastoDyn.dat", f"IEA-3.4-130-RWT_ElastoDyn_{turbine_id}.dat")
                    if turbine_id == "T1":
                        with open(os.path.join(output_path_openfast, f"IEA-3.4-130-RWT_ElastoDyn_{turbine_id}.dat"), 'r+') as elastodyn_file:
                            content = elastodyn_file.readlines()
                            for i, content_line in enumerate(content):
                                if "NacYaw" in content_line:
                                    content[i] = content_line.replace("0.0", str(yaw_T1))
                            elastodyn_file.seek(0)
                            elastodyn_file.writelines(content)
                    elif turbine_id == "T2":
                        with open(os.path.join(output_path_openfast, f"IEA-3.4-130-RWT_ElastoDyn_{turbine_id}.dat"), 'r+') as elastodyn_file:
                            content = elastodyn_file.readlines()
                            for i, content_line in enumerate(content):
                                if "NacYaw" in content_line:
                                    content[i] = content_line.replace("0.0", str(yaw_T2))
                            elastodyn_file.seek(0)
                            elastodyn_file.writelines(content)
                if "ServoDyn.dat" in line:
                    line = line.replace("IEA-3.4-130-RWT_ServoDyn.dat", f"IEA-3.4-130-RWT_ServoDyn_{turbine_id}.dat")
                    servo_dyn_file = os.path.join(output_path_openfast, f"IEA-3.4-130-RWT_ServoDyn_{turbine_id}.dat")
                    with open(servo_dyn_file, 'r+') as servo_file:
                        content = servo_file.readlines()
                        for i, content_line in enumerate(content):
                            if "DLL_FileName" in content_line:
                                content[i] = content_line.replace("../rosco/libdiscon.so", f"../rosco/libdiscon_{turbine_id}.so")
                        servo_file.seek(0)
                        servo_file.writelines(content)
                dst.write(line)
    
        # Modify the IEA-3.4-130-RWT_DISCON.IN file for each turbine
        discon_file = os.path.join(output_path_openfast, f"IEA-3.4-130-RWT_DISCON_{turbine_id}.IN")
        if not os.path.exists(discon_file):
            raise FileNotFoundError(f"DISCON file '{discon_file}' does not exist for turbine {turbine_id}.")
        
        with open(discon_file, 'r+') as discon:
            content = discon.readlines()
            for i, content_line in enumerate(content):
                if "PRC_R_Speed" in content_line:
                    parts = content_line.split()
                    if len(parts) > 1:
                        if turbine_id == "T1" or  turbine_id == "T2":
                            parts[1] = str(curtailment / 100.)
                        else:
                            parts[1] = str(1.0)
                        content[i] = " ".join(parts) + "\n"
            discon.seek(0)
            discon.writelines(content)
    