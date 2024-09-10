import argparse
import subprocess
import os
import sys
import xml.etree.ElementTree as ET


blender_249_path = "D:\\Programs\\Blender2.49\\blender.exe"
blender_36_path = "D:\\Programs\\Blender 3.6\\blender.exe"


def progress_bar(iteration, total, bar_length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(bar_length * progress))
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write(f'\r[{arrow}{spaces}] {int(progress * 100)}% ({iteration}/{total})')
    sys.stdout.flush()

def import_model(output, rmb_file, rab_files):
    rab_formatted = ' '.join([f'--rab "{rab_file}"' for rab_file in rab_files])
    command_249 = f"{blender_249_path} -b -P ./bpy249_import.py -- --out {output} --rmb {rmb_file} {rab_formatted}"

    process = subprocess.run(command_249, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        print(f"Error while executing Blender 2.49: {process.stderr}")
    else:
        print("Succesfully save in .blend file.")

def export_blend_to_fbx(blend_file, output, rmb_file):
    command = f'{blender_36_path} -b {blend_file} --python ./bpy36_export.py -- --out {output} --rmb {rmb_file}'
    process = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # process = subprocess.run(command)
    if process.returncode != 0:
        print(f"\nError while executing Blender 3.6: {process.stderr}\n")

def parse_txt_file(input_file) -> tuple[str, list[str]]:
    with open(input_file, 'r') as file:
        content = file.read()

        root = ET.fromstring(content)

        mesh_file = root.find('.//Mesh/FileName').text

        rab_files = set()
        for action in root.findall('.//Animation/Action/FileName'):
            rab_files.add(action.text)

        rab_files = sorted(rab_files)

        print("Mesh FileName (.rmb):", mesh_file)
        print("Unique Action FileName (.rab) files:", rab_files)

        return mesh_file, rab_files


def main():
    parser = argparse.ArgumentParser(description="Convert RMB/RAB to FBX")
    parser.add_argument('-i', '--input', type=str, help='Path to the model .txt file')
    parser.add_argument('-o', '--output', type=str, help='Path to the folder where the FBX files will be saved')
    
    args = parser.parse_args()

    # check if the input file exists
    if not os.path.exists(args.input):
        print(f"File {args.input} does not exist.")
        return
    
    # check if the output folder exists
    if not os.path.exists(args.output):
        print(f"Folder {args.output} does not exist.")
        return


    output = args.output
    rmb_file, rab_files = parse_txt_file(args.input)
    rmb_file = os.path.join(os.path.dirname(args.input), rmb_file)
    rab_files = [os.path.join(os.path.dirname(args.input), rab_file) for rab_file in rab_files]

    # import model and save in .blend file
    import_model(output, rmb_file, rab_files)

    # check if the .blend file exists
    rmb_filename = os.path.basename(rmb_file).replace('.rmb', '')
    blend_file = os.path.join(output, rmb_filename, f"{rmb_filename}.blend")
    if not os.path.exists(blend_file):
        print(f"Blend file {blend_file} does not exist.")
        return
    
    # open the rmb .blend file and export to FBX
    print(f"\nExporting {rmb_filename} to FBX")
    export_blend_to_fbx(blend_file, os.path.join(output, rmb_filename), rmb_file)
    # export all actions to FBX
    print(f"\nExporting actions to FBX")
    total = len(rab_files)
    for i, rab_file in enumerate(rab_files):
        blend_file = os.path.join(output, rmb_filename, f"{os.path.basename(rab_file).replace('.rab', '')}.blend")
        export_blend_to_fbx(blend_file, os.path.join(output, rmb_filename), rmb_file)
        progress_bar(i+1, total)

if __name__ == '__main__':
    main()