from ruamel.yaml import YAML

def generate_fsft(fsft_vt, output_path):

    with open(output_path, 'w') as fsft_file:
        fsft_file.write("------- FAST.Farm for OpenFAST INPUT FILE -------------------------------------------------\n")
        fsft_file.write("Sample FAST.Farm input file\n")
        fsft_file.write("--- SIMULATION CONTROL ---\n")
        
        for key, value in fsft_vt.items():
            if 'default' in value:
                default = value.get('default', '')
                description = value.get('description', '').split('(')[0].strip()
                if isinstance(default, list):
                    default = ', '.join(map(str, default))
                if default is False:
                    default = "False"
                fsft_file.write(f"{str(default):<20} {key:<20} - {description}\n")
                if key == "Mod_SharedMooring":
                    fsft_file.write("--- SUPER CONTROLLER --- [used only for UseSC=True]\n")
                elif key == "SC_FileName":
                    fsft_file.write("--- SHARED MOORING SYSTEM --- [used only for Mod_SharedMoor>0]\n")
                elif key == "WrMooringVis":
                    fsft_file.write("--- AMBIENT WIND: PRECURSOR IN VTK FORMAT --- [used only for Mod_AmbWind=1]\n")
                elif key == "ChkWndFiles":
                    fsft_file.write("--- AMBIENT WIND: INFLOWWIND MODULE --- [used only for Mod_AmbWind=2 or 3]\n")
                elif key == "InflowFile":
                    fsft_file.write("--- WIND TURBINES ---\n")
                    fsft_file.write("%d                  NumTurbines        - Number of wind turbines (-) [>=1]  [last 6 columns below used only for Mod_AmbWind=2 or 3]\n"%len(fsft_vt["WT_X"]))
                    fsft_file.write("WT_X    WT_Y   WT_Z    WT_FASTInFile\n")
                    fsft_file.write("(m)      (m)    (m)    (string)\n")
                    for i in range(len(fsft_vt["WT_X"])):
                        fsft_file.write(f"{fsft_vt['WT_X'][i]:<8} {fsft_vt['WT_Y'][i]:<8} {fsft_vt['WT_Z'][i]:<8} \"{fsft_vt['WT_FASTInFile'][i]}\" {fsft_vt['X0_High'][i]:<8} {fsft_vt['Y0_High'][i]:<8} {fsft_vt['Z0_High'][i]:<8} {fsft_vt['dX_High'][i]:<8} {fsft_vt['dY_High'][i]:<8} {fsft_vt['dZ_High'][i]:<8}\n")
                    fsft_file.write("--- WAKE DYNAMICS ---\n")

                elif key == "C_Meander":
                    fsft_file.write("--- CURLED-WAKE PARAMETERS [only used if Mod_Wake=2 or 3] ---\n")
                elif key == "Mod_Projection":
                    fsft_file.write("--- WAKE-ADDED TURBULENCE ---\n")
                elif key == "WAT_k_Grad":
                    fsft_file.write("--- VISUALIZATION ---\n")
                elif key == "WrDisDT":
                    fsft_file.write("--- OUTPUT ---\n")
        fsft_file.write('END of input file (the word "END" must appear in the first 3 columns of this last OutList line)\n')
        fsft_file.close()

if __name__ == "__main__":
    schema_path = "/Users/pbortolo/work/3_projects/30_HolisticSE/FarmCast/code/fast_farm_schema.yaml"

    yaml = YAML(typ='safe')
    with open(schema_path, 'r') as schema_file:
        schema = yaml.load(schema_file)

    fsft_vt = schema.get('properties', {}).get('FASTFarm', {}).get('properties', {})
    fsft_vt["WT_X"] = [-780, 0, 780]
    fsft_vt["WT_Y"] = [0, 0, 0]
    fsft_vt["WT_Z"] = [0, 0, 0]
    fsft_vt["WT_FASTInFile"] = ["../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T1.fst",
                                "../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T2.fst",
                                "../turbines/IEA-3.4-130-RWT/IEA-3.4-130-RWT_T3.fst"]
    fsft_vt["X0_High"] = [-820, -40, 740]
    fsft_vt["Y0_High"] = [-80, -80, -80]
    fsft_vt["Z0_High"] = [5, 5, 5]
    fsft_vt["dX_High"] = [5, 5, 5]
    fsft_vt["dY_High"] = [10, 10, 10]
    fsft_vt["dZ_High"] = [10, 10, 10]



    output_path = "/Users/pbortolo/work/3_projects/30_HolisticSE/FarmCast/fastfarm/generated.FarmIEA3p4.fstf"
    generate_fsft(fsft_vt, output_path)
    print(f"Generated .fsft file at {output_path}")
