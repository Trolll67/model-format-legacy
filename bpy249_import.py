import sys
import Blender
import os
from rmb_rab_import import rmb_rab_import
from collections import defaultdict

def importer(output, rmb_file, rab_files):
    rmb_rab_import(rmb_file)

    rmb_filename = os.path.basename(rmb_file)
    output_filepath = os.path.join(output, rmb_filename.replace('.rmb', ''))
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    rmb_blend_path = os.path.join(output_filepath, rmb_filename.replace('.rmb', '.blend'))

    Blender.Save(rmb_blend_path, 1)
    print("Mesh file {0} imported.".format(rmb_blend_path))

    for rab_file in rab_files:
        rmb_rab_import(rab_file)

        rab_filename = os.path.basename(rab_file)
        rab_blend_path = os.path.join(output_filepath, rab_filename.replace('.rab', '.blend'))

        Blender.Save(rab_blend_path, 1)
        print("Action file {0} imported.".format(rab_blend_path))

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