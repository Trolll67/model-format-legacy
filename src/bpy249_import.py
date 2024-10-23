# Author: Trolll, https://github.com/Trolll67, https://vk.com/trolll67
# Date: 2024-10-23
# Description: Python script to import RMB and RAB files into Blender 2.49b
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


from math import degrees, radians
import sys
import Blender
import os
from rmb_rab_import import rmb_rab_import
from collections import defaultdict
import logging


def setup_logging():
    logger = logging.getLogger("Blender249_ConvertLogger")
    logger.setLevel(logging.DEBUG)

    # Create handlers: one for logging to console and one for logging to a file
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("converter_blender249.log")

    # Set logging levels for handlers
    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()


def fix_transforms(obj):
    # rotate 90 degrees on X axis
    obj.RotX = radians(90)
    # scale by 100
    obj.SizeX *= 0.01
    obj.SizeY *= 0.01
    obj.SizeZ *= 0.01

def importer(output, rmb_file, rab_files):
    rmb_rab_import(rmb_file)

    rmb_filename = os.path.basename(rmb_file)
    rmb_filename_no_ext = rmb_filename.replace('.rmb', '')
    output_filepath = os.path.join(output, rmb_filename_no_ext)
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    rmb_blend_path = os.path.join(output_filepath, rmb_filename.replace('.rmb', '.blend'))
    logger.info("Mesh file {0} imported.".format(rmb_blend_path))

    last_action_path = None
    for rab_file in rab_files:
        rmb_rab_import(rab_file)

        rab_filename = os.path.basename(rab_file)
        rab_blend_path = os.path.join(output_filepath, rab_filename.replace('.rab', '.blend'))

        last_action_path = rab_blend_path
        logger.info("Action file {0} imported.".format(rab_blend_path))

    output_filepath = rmb_blend_path if rab_files is None or len(rab_files) == 0 or len(rab_files) > 1 else last_action_path
    if len(rab_files) > 1:
        output_filepath = rmb_blend_path.split('.')[0] + '_all' + rmb_blend_path.split('.')[1]
    
    # find the mesh object by name
    mesh_obj = None
    for obj in Blender.Object.Get():
        if obj.getName().startswith(rmb_filename_no_ext):
            mesh_obj = obj
            break

    # fix transforms
    if mesh_obj:
        fix_transforms(mesh_obj)
        logger.info("Transforms fixed for {0}".format(mesh_obj.getName()))
    else:
        logger.error("Mesh object not found for {0}".format(rmb_filename_no_ext))

    Blender.Save(output_filepath, 1)
    Blender.Quit()

def parse_arguments():
    parsed_args = defaultdict(list)
    args = sys.argv[1:]

    if '--' in args:
        start_index = args.index('--') + 1
    else:
        start_index = len(args)

    i = start_index
    while i < len(args):
        if args[i].startswith('-'):
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                parsed_args[args[i]].append(args[i + 1])
                i += 2
            else:
                parsed_args[args[i]].append(None)
                i += 1
        else:
            i += 1
    
    return parsed_args['--out'][0], parsed_args['--rmb'][0], parsed_args['--rab']

def main():
    output, rmb, rabs = parse_arguments()
    importer(output, rmb, rabs)

if __name__ == '__main__':
    main()