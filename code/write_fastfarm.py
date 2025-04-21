from ruamel.yaml import YAML

def generate_fsft(schema_path, output_path):
    yaml = YAML(typ='safe')
    with open(schema_path, 'r') as schema_file:
        schema = yaml.load(schema_file)

    fastfarm = schema.get('properties', {}).get('FASTFarm', {}).get('properties', {})
    with open(output_path, 'w') as fsft_file:
        fsft_file.write("------- FAST.Farm for OpenFAST INPUT FILE -------------------------------------------------\n")
        fsft_file.write("Sample FAST.Farm input file\n")
        fsft_file.write("--- SIMULATION CONTROL ---\n")
        
        for key, value in fastfarm.items():
            default = value.get('default', '')
            description = value.get('description', '').split('(')[0].strip()
            if isinstance(default, list):
                default = ', '.join(map(str, default))
            fsft_file.write(f"{default:<20} {key:<20} - {description}\n")
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
    output_path = "/Users/pbortolo/work/3_projects/30_HolisticSE/FarmCast/fastfarm/generated.FarmIEA3p4.fstf"
    generate_fsft(schema_path, output_path)
    print(f"Generated .fsft file at {output_path}")
