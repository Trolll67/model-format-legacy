# Author: Trolll, https://github.com/Trolll67, https://vk.com/trolll67
# Date: 2024-10-23
# Description: CLI tool to convert RMB/RAB files to FBX and BLEND files using Blender 2.49 and 3.6
#
# License: GNU General Public License v3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import argparse
import configparser
import subprocess
import os
import sys
import xml.etree.ElementTree as ET
import zipfile
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


CLI = False

def setup_logging():
    logger = logging.getLogger("ConvertLogger")
    logger.setLevel(logging.DEBUG)

    # Create handlers: one for logging to console and one for logging to a file
    # console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("app.log")

    # Set logging levels for handlers
    # console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    # logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()

# Read configuration file
config_path = 'config.ini'
config = configparser.ConfigParser()

if not os.path.exists(config_path):
    config['Blender'] = {
        'blender_249_path': '',
        'blender_36_path': ''
    }

    with open(config_path, 'w') as configfile:
        config.write(configfile)

config.read('config.ini')
blender_249_path = config.get('Blender', 'blender_249_path')
blender_36_path = config.get('Blender', 'blender_36_path')


def downloading_progress_bar(current, total, bar_length=40):
    percent = current / total
    arrow = '█' * int(percent * bar_length - 1)
    spaces = ' ' * (bar_length - len(arrow) - 1)

    current_mb = current / 1024 / 1024
    total_mb = total / 1024 / 1024

    # ANSI escape code for green text
    green_color = '\033[92m'
    reset_color = '\033[0m'

    percent *= 100
    sys.stdout.write(f'\r[{green_color}{arrow}{spaces}{reset_color}] {percent:.2f}% ({current_mb:.2f} MB / {total_mb:.2f} MB)')
    sys.stdout.flush()

def download_file(url, destination, download_status):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response, open(destination, 'wb') as out_file:
            total_size = response.length
            bytes_downloaded = 0
            
            while True:
                # Read the response in chunks
                data = response.read(1024)  # Read 1KB at a time
                if not data:
                    break  # End of file

                out_file.write(data)  # Write to the output file
                bytes_downloaded += len(data)  # Update the downloaded bytes
                
                # Update the download status
                if download_status:
                    download_status(bytes_downloaded, total_size)

        # break line after progress bar in CLI
        if CLI:
            print()
        return True
    except HTTPError as e:
        logger.error(f"HTTP error occurred: {e.code} - {e.reason}")
        print(f"HTTP error occurred: {e.code} - {e.reason}")
        return False
    except URLError as e:
        logger.error(f"Failed to reach the server: {e.reason}")
        print(f"Failed to reach the server: {e.reason}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
        return False

def cli_download_status(count, total_size):
    if count == 0:
        logger.info(f"Downloading...")
        print(f"Downloading...")

    if CLI:
        downloading_progress_bar(count, total_size)

def extract_zip(zip_file, extract_to):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            return True
    except zipfile.BadZipFile:
        logger.error("Error: Bad Zip file. Extraction failed.")
        print("Error: Bad Zip file. Extraction failed.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during extraction: {e}")
        print(f"An unexpected error occurred during extraction: {e}")
        return False

def update_config(section, option, value):
    config.set(section, option, value)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    print(f"Config updated: [{section}] {option}={value}")

    if section == 'Blender' and option == 'blender_249_path':
        global blender_249_path
        blender_249_path = value
    elif section == 'Blender' and option == 'blender_36_path':
        global blender_36_path
        blender_36_path = value
        

def download_blender249(download_status):
    zip_file_name = "blender-2.49b-windows.zip"
    extract_dir = "blender_2.49b"

    logger.info("Downloading Blender 2.49...")
    print("Downloading Blender 2.49...")
    result = download_file('https://download.blender.org/release/Blender2.49b/blender-2.49b-windows.zip', zip_file_name, download_status)
    if not result:
        return False

    logger.info(f"Extracting {zip_file_name}...")
    print(f"Extracting {zip_file_name}...")
    result = extract_zip(zip_file_name, extract_dir)
    if not result:
        return False

    update_config('Blender', 'blender_249_path', os.path.join(os.getcwd(), extract_dir, os.path.splitext(zip_file_name)[0], 'blender.exe'))
    logger.info("Blender 2.49 downloaded and extracted successfully.")
    print("Blender 2.49 downloaded and extracted successfully.")

def ask_to_download_blender249():
    user_input = input("Do you want to download Blender 2.49? (y/n): ").strip().lower()

    if user_input == 'y':
        download_blender249(cli_download_status)
        return True
    elif user_input == 'n':
        logger.error("Blender 2.49 will not be downloaded. Exiting...")
        print("Blender 2.49 will not be downloaded. Exiting...")
        return False
    else:
        logger.warning("Invalid input. Please enter 'y' or 'n'.")
        print("Invalid input. Please enter 'y' or 'n'.")
        ask_to_download_blender249()

def download_blender36(download_status):
    zip_file_name = "blender-3.6.17-windows-x64.zip"
    extract_dir = "blender_3.6"

    logger.info("Downloading Blender 3.6...")
    print("Downloading Blender 3.6...")
    # result = download_file('https://www.blender.org/download/release/Blender3.6/blender-3.6.17-windows-x64.zip', zip_file_name, download_status)
    result = download_file('https://mirror.freedif.org/blender/release/Blender3.6/blender-3.6.17-windows-x64.zip', zip_file_name, download_status)
    if not result:
        return False

    logger.info(f"Extracting {zip_file_name}...")
    print(f"Extracting {zip_file_name}...")
    result = extract_zip(zip_file_name, extract_dir)
    if not result:
        return False

    update_config('Blender', 'blender_36_path', os.path.join(os.getcwd(), extract_dir, os.path.splitext(zip_file_name)[0], 'blender.exe'))
    logger.info("Blender 3.6 downloaded and extracted successfully.")
    print("Blender 3.6 downloaded and extracted successfully.")

def ask_to_download_blender36():
    user_input = input("Do you want to download Blender 3.6? (y/n): ").strip().lower()

    if user_input == 'y':
        download_blender36(cli_download_status)
        return True
    elif user_input == 'n':
        logger.error("Blender 3.6 will not be downloaded. Exiting...")
        print("Blender 3.6 will not be downloaded. Exiting...")
        return False
    else:
        logger.warning("Invalid input. Please enter 'y' or 'n'.")
        print("Invalid input. Please enter 'y' or 'n'.")
        ask_to_download_blender36()

def progress_bar(iteration, total, bar_length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(bar_length * progress))
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write(f'\r[{arrow}{spaces}] {int(progress * 100)}% ({iteration}/{total})')
    sys.stdout.flush()

def import_model(output, rmb_file, rab_files, all_in_one, mesh_only):
    if all_in_one:
        # import mesh and all actions in the same .blend file
        logger.info("Importing mesh and all actions in the same .blend file...")
        print("Importing mesh and all actions in the same .blend file...")
        rab_formatted = ' '.join([f'--rab "{rab_file}"' for rab_file in rab_files]) if not mesh_only else ''
        command_249 = f"{blender_249_path} -b -P ./bpy249_import.py -- --out {output} --rmb {rmb_file} {rab_formatted}"

        process = subprocess.run(command_249, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if process.returncode != 0:
            logger.error(f"Error while executing Blender 2.49: {process.stderr}")
            print(f"Error while executing Blender 2.49: {process.stderr}")
            return False
        elif 'error' in process.stdout.lower():
            logger.info(process.stdout)
            print(process.stdout)
    else:
        # import mesh
        logger.info("Importing RMB mesh...")
        print("Importing RMB mesh...")
        command_249 = f"{blender_249_path} -b -P ./bpy249_import.py -- --out {output} --rmb {rmb_file}"
        # process = subprocess.run(command_249, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process = subprocess.run(command_249, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if process.returncode != 0:
            logger.error(f"Error while executing Blender 2.49: {process.stderr}")
            print(f"Error while executing Blender 2.49: {process.stderr}")
            return False
        elif 'error' in process.stdout.lower():
            logger.info(process.stdout)
            print(process.stdout)

        if mesh_only:
            return True
        
        if len(rab_files) == 0:
            return True

        # import actions separately
        logger.info(f"Importing {len(rab_files)} RAB actions...")
        print(f"Importing {len(rab_files)} RAB actions...")
        total = len(rab_files)
        for i, rab_file in enumerate(rab_files):
            command_249 = f"{blender_249_path} -b -P ./bpy249_import.py -- --out {output} --rmb {rmb_file} --rab {rab_file}"
            process = subprocess.run(command_249, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if process.returncode != 0:
                logger.error(f"\nError while executing Blender 2.49: {process.stderr}\n")
                print(f"\nError while executing Blender 2.49: {process.stderr}\n")
                return False
            elif 'error' in process.stdout.lower():
                logger.info(process.stdout)
                print(process.stdout)

            if CLI:
                progress_bar(i+1, total)

        # break line after progress bar in CLI
        if CLI:
            print()

    return True

def export_blend_to_fbx(blend_file, output, rmb_file):
    command = f'{blender_36_path} -b {blend_file} --python ./bpy36_export.py -- --out {output} --rmb {rmb_file}'
    process = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        logger.error(f"\nError while executing Blender 3.6. Code: {process.returncode}, Error: {process.stderr}\n")
        print(f"\nError while executing Blender 3.6. Code: {process.returncode}, Error: {process.stderr}\n")
    # elif 'error' in process.stdout.lower():
    #     logger.info(process.stdout)
    #     print(process.stdout)

def parse_txt_file(input_file, mesh_only, anim_types) -> tuple[str, list[str]]:
    with open(input_file, 'r') as file:
        content = file.read()

        root = ET.fromstring(content)

        mesh_file = root.find('.//Mesh/FileName').text
        logger.info(f"Mesh FileName (.rmb): {mesh_file}")
        print(f"Mesh FileName (.rmb): {mesh_file}")

        if mesh_only:
            return mesh_file, []

        rab_files = set()

        def is_anim_type(anim_name):
            for anim_type in anim_types:
                atype = anim_type.lower() if anim_type.lower().startswith('a_') else f'A_{anim_type}'.lower()
                if anim_name.lower() == atype:
                    return True
                
            return False

        if len(anim_types) == 1 and anim_types[0] == 'all':
            for action in root.findall('.//Animation/Action/FileName'):
                rab_files.add(action.text)
        else:
            for action in root.findall('.//Animation/Action'):
                if is_anim_type(action.get('Name')):
                    rab_files.add(action.find('.//FileName').text)

        rab_files = sorted(rab_files)

        logger.info(f"Found {len(rab_files)} (.rab) files:")
        print(f"Found {len(rab_files)} (.rab) files:")
        for rab_file in rab_files:
            logger.info(f'\t{rab_file}')
            print(f'\t{rab_file}')

        return mesh_file, rab_files

def parse_rmb_file(input_file, mesh_only, anim_types) -> tuple[str, list[str]]:
    config_filename = os.path.basename(input_file).replace('.rmb', '.txt')
    config_file = os.path.join(os.path.dirname(input_file), config_filename)
    if not os.path.exists(config_file):
        return input_file, []
    
    return parse_txt_file(config_file, mesh_only, anim_types)

def process(input_file, output_dir, all_in_one, rmb2blend, blend2fbx, mesh_only, anim_types, download_blender):
    # download Blender 2.49 and 3.6
    if download_blender:
        if not CLI:
            return "Error: --download-blender can only be used with CLI and as a single flag."

        if input_file or output_dir or all_in_one or rmb2blend or blend2fbx or mesh_only or anim_types:
            return "Error: --download-blender can only be used as a single flag."

        ask_to_download_blender249()
        ask_to_download_blender36()
        return

    if not os.path.exists(blender_249_path):
        return f"Error: Blender 2.49 path does not exist.\nPath: {blender_249_path}"

    if not os.path.exists(blender_36_path):
        return f"Error: Blender 3.6 path does not exist.\nPath: {blender_36_path}"

    # check if the input file exists
    if not os.path.exists(input_file) or not os.path.exists(output_dir):
        return f"Error: Both input file and output directory are required.\nUsage: converter_cli.exe -i <input_file> -o <output_dir>"
    
    # check if only blend2fbx is set and anim-type
    if not rmb2blend and blend2fbx and anim_types:
        return "Error: --anim-types can only be used with --rmb2blend"
    
    # if --rmb2blend and --blend2fbx are not set, set both
    if not rmb2blend and not blend2fbx:
        rmb2blend = True
        blend2fbx = True

    output = output_dir
    ext = os.path.splitext(input_file)[1]
    if ext != '.txt' and ext != '.rmb':
        return f"Error: Invalid file extension: {ext}"
    
    # create output directory
    filename_without_ext = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(output, filename_without_ext)
    os.makedirs(output_dir, exist_ok=True)

    # Parse the input file
    rmb_file, rab_files = parse_txt_file(input_file, mesh_only, anim_types) if ext == '.txt' else parse_rmb_file(input_file, mesh_only, anim_types)
    rmb_file = os.path.join(os.path.dirname(input_file), rmb_file)
    rab_files = [os.path.join(os.path.dirname(input_file), rab_file) for rab_file in rab_files]

    # Import model and save in .blend file
    if rmb2blend:
        result = import_model(output, rmb_file, rab_files, all_in_one, mesh_only)
        if not result:
            return "Error: Failed to import model to Blender 2.49."

    # Export mesh to FBX
    if blend2fbx:
        rmb_filename = os.path.basename(rmb_file).replace('.rmb', '')
        logger.info(f"Exporting Mesh {rmb_filename} to FBX...")
        print(f"Exporting Mesh {rmb_filename} to FBX...")

        # check if the .blend file exists
        blend_file = os.path.join(output, rmb_filename, f"{rmb_filename}.blend")
        if not os.path.exists(blend_file):
            return f"Error: Blend file {blend_file} does not exist."
    
        export_blend_to_fbx(blend_file, os.path.join(output, rmb_filename), rmb_file)

        # return the output directory if mesh_only is set
        if mesh_only:
            return output_dir

        # Export all in one actions to FBX
        if all_in_one:
            logger.info(f"Exporting all actions to one FBX")
            print(f"Exporting all actions to one FBX")
            actions_blend_file = os.path.splitext(blend_file)[0] + '_all' + os.path.splitext(blend_file)[1]
            export_blend_to_fbx(actions_blend_file, os.path.join(output, rmb_filename), rmb_file)
            return output_dir

        # Export actions to FBX
        total = len(rab_files)
        logger.info(f"Exporting {total} actions to FBX...")
        print(f"Exporting {total} actions to FBX...")
        for i, rab_file in enumerate(rab_files):
            blend_file = os.path.join(output, rmb_filename, f"{os.path.basename(rab_file).replace('.rab', '')}.blend")
            export_blend_to_fbx(blend_file, os.path.join(output, rmb_filename), rmb_file)
            
            if CLI:
                progress_bar(i+1, total)

    # return the output directory
    return output_dir

def print_intro():
    """Print application intro and author details."""
    print("=======================================")
    print("  RMB/RAB to FBX Converter CLI Tool")
    print("  Version 1.0")
    print("  Author: Trolll")
    print("=======================================")
    print()
    print("This tool allows you to convert .rmb and .rab files to .fbx and .blend files.")
    print("Usage: converter_cli.exe -i m0001.txt -o /path/to/fbxs --rmb2blend --blend2fbx")
    print()
    print("By providing a .txt model configuration file, you can convert a .rmb mesh and\nall .rab animations to .fbx files in one go.")
    print("You can convert a single .rmb mesh without animations by using the --mesh-only flag.")
    print("You can also convert only specific animations by specifying the type with the --anim-type flag.")
    print()
    print()

def main():
    # details about the tool
    print_intro()

    parser = argparse.ArgumentParser(description="Convert RMB/RAB to FBX CLI Tool. Created by Trolll")
    parser.add_argument('-i', '--input', type=str, default='', help='Path to the model .rmb mesh file or .txt config file')
    parser.add_argument('-o', '--output', type=str, default='', help='Path to the folder where the output files will be saved')
    parser.add_argument('-a', '--all-in-one', action='store_true', default=False, help='Import all actions in the same .blend file')
    parser.add_argument('--rmb2blend', action='store_true', default=False, help='Import the RMB model to Blender and save in .blend file')
    parser.add_argument('--blend2fbx', action='store_true', default=False, help='Export the .blend file to FBX')
    parser.add_argument('--mesh-only', action='store_true', default=False, help='Import only the .rmb mesh')
    parser.add_argument('--anim-types', type=str, nargs='+', help='Animation type(s) to export (e.g., idle, idle1, walk)')
    parser.add_argument('--download-blender' , action='store_true', default=False, help='Download Blender 2.49 and 3.6')
    
    args = parser.parse_args()
    anim_types = args.anim_types if isinstance(args.anim_types, list) else [args.anim_types] if args.anim_types else []

    global blender_249_path, blender_36_path

    if not os.path.exists(blender_249_path):
        logger.info(f"Blender 2.49 path {blender_249_path} does not exist.")
        print(f"Blender 2.49 path {blender_249_path} does not exist.")
        ask_to_download_blender249()
        print("Blender 2.49 path: ", blender_249_path)
        # wait use input to close the window
        if (os.path.exists(blender_249_path)):
            logger.info("Blender 2.49 downloaded successfully. Close the window and run the script again to continue.")
            print("Blender 2.49 downloaded successfully. Close the window and run the script again to continue.")
            print("Press Enter to exit...")
        else:
            logger.info("Blender 2.49 download failed. Press Enter to exit...")
            print("Blender 2.49 download failed. Press Enter to exit...")
        
        input()
        sys.exit()

    if not os.path.exists(blender_36_path):
        logger.info(f"Blender 3.6 path {blender_36_path} does not exist.")
        print(f"Blender 3.6 path {blender_36_path} does not exist.")
        ask_to_download_blender36()
        # wait use input to close the window
        if (os.path.exists(blender_36_path)):
            logger.info("Blender 3.6 downloaded successfully. Close the window and run the script again to continue.")
            print("Blender 3.6 downloaded successfully. Close the window and run the script again to continue.")
            print("Press Enter to exit...")
        else:
            logger.info("Blender 3.6 download failed. Press Enter to exit...")
            print("Blender 3.6 download failed. Press Enter to exit...")

        input()
        sys.exit()

    result = process(args.input, args.output, args.all_in_one, args.rmb2blend, args.blend2fbx, args.mesh_only, anim_types, args.download_blender)
    # check if the result is a error message
    if result and result.startswith("Error:"):
        logger.error(result)
        print(result)
        print("\nPress Enter to exit...")
        input()
        sys.exit()
    

if __name__ == '__main__':
    CLI = True
    try:
        main()
    except Exception as e:
        print(f"MAIN ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        input("Press Enter to exit...")


# Command to run the script:
# python .\converter.py -i model.txt -o output_folder --all-in-one --rmb2blend --blend2fbx
# python .\converter.py -i "E:\map_zone\models\m00583.rmb" -o E:\map_zone\output_models --anim-type "dead"

# Command to build exe:
# pyinstaller --onefile --windowed --hidden-import=tkinter --hidden-import=subprocess --hidden-import=converter --hidden-import=bpy249_import --hidden-import=bpy36_export  .\converter_gui.py
# pyinstaller --onefile --console --hidden-import=subprocess --hidden-import=bpy249_import --hidden-import=bpy36_export --name=converter_cli  .\converter.py