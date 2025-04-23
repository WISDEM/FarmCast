import os

def set_rosco_curtailment(path2discon, pc_curtailment):
    """
    Set the power curtailment in the ROSCO DISCON file by 
    curtailing the rotor speed. The alternative is to curtail torque, or both.
    """


    speed_curtailment = pc_curtailment / 100.0
    
    if not os.path.isfile(path2discon):
         raise FileNotFoundError(f"The file at {path2discon} does not exist.")

    with open(path2discon, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if "PRC_R_Speed" in line:
            parts = line.split()
            if len(parts) > 1:
                parts[0] = str(speed_curtailment)
                lines[i] = " ".join(parts) + "\n"
            break
    else:
        raise ValueError("The keyword 'PRC_R_Speed' was not found in the file.")

    with open(path2discon, 'w') as file:
        file.writelines(lines)