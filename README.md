# RMB/RAB to FBX Converter

This tool is an extended version of the original plugin created by Theran, from the Xentax forum ([source](https://forum.xentax.com)). I’ve added a convenient wrapper and expanded the functionality to streamline the process of converting `.rmb` (mesh) and `.rab` (animation) files from the game *R2 Reign of Revolution* into FBX format.

## Features
- Blender 2.49 plugin:
  - Import .rmb and .rab
- GUI/CLI tool: 
  - Convert `.rmb` meshes and `.rab` animations to FBX format and also save as `.blend` file.
  - Option to import only the mesh or include animations.
  - Support for importing multiple animations into a single `.blend` file or exporting them individually.
  - Automatically handles the full conversion process through Blender 2.49 and Blender 3.6.

## Requirements

- Blender 2.49b (for reading `.rmb` and `.rab` files and save as `.blend` file)
- Blender 3.6 (for exporting data from `.blend` file to `.fbx`)

## Installation

1. **Download the Release:**
   - Download the release archive from the repository.
   - Extract the contents of the archive to a desired location on your computer.

2. **Choose One of the Following Options:**

    Option 1: Install as a Blender 2.49 Plugin**
      - Install the `rmb_rab_import.py` file as a plugin for Blender 2.49.
      - Open Blender 2.49.
      - Navigate to `File -> Import -> R2 Online Import (.rmb/.rab/.txt)` to import meshes, animations, or configuration text files. The configuration file will load the mesh and all available animations.

    Option 2: Use `converter_cli.exe` for Conversion
      - Use `converter_cli.exe` to convert `.rmb/.rab` files into `.blend` files, and subsequently into `.fbx` files.
      - **Configuration Required:**
        - Set up the `config.ini` file with the paths to Blender 2.49 and Blender 3.6. Here is an example of the configuration:
          ```ini
          [Blender]
          blender_249_path = C:\path\to\blender_2.49b\blender.exe
          blender_36_path = C:\path\to\blender_3.6\blender.exe
          ```

    Option 3: Use `converter_gui.exe` GUI Wrapper
      - Use `converter_gui.exe`, a graphical user interface wrapper for the CLI utility.
      - **Configuration Required:**
        - Similar to Option 2, configure the `config.ini` file with paths to Blender 2.49 and Blender 3.6 as shown above.

3. **Additional Notes:**
   - Ensure that Blender is properly installed and that all paths in the configuration file are correctly set for your environment.

## Usage Instructions for `converter_cli.exe`

To use the `converter_cli.exe` application for converting `.rmb` or `.rab` files, follow the syntax below:

```bash
converter_cli.exe -i "<input_file_path>" -o "<output_directory>"
```

### Animations
If you need a specific animation, you can set it up using the `--anim-types` option:

```bash
--anim-types <animation_type> # idle1, walk, attack1 and etc.
```
You can specify multiple options separated by spaces.
```bash
--anim-types idle dead attack1
```

### Only Mesh
To import only the mesh from a `.rmb` file, use the `--mesh-only` option. This allows you to extract the mesh without any associated animations.

```bash
--mesh-only
```

## Arguments
- ```bash
  -i, --input
  ```
  Path to the .rmb mesh file or .txt configuration file specifying the model and animations.
- ```bash
  -o, --output
  ```
  Directory where the output files (FBX or .blend) will be saved.

## Options
- ```bash
  -a, --all-in-one
  ```
  Import all animations into a single .blend file.
- ```bash
  --rmb2blend
  ```
  Convert the .rmb file into a Blender .blend file.
- ```bash
  --blend2fbx
  ```
  Convert the generated .blend file to FBX format.
- ```bash
  --mesh-only
  ```
  Import only the mesh, without any animations.
- ```bash
  --anim-types
  ```
  Specify which animation type to export (e.g., idle, walk, battle_stand). Default is all.

## Example
To convert an .rmb mesh with animations and export them to FBX:
```bash
converter_cli.exe -i path/to/model.rmb -o path/to/output
```

To import only the mesh into a Blender file:
```bash
converter_cli.exe -i path/to/model.rmb -o path/to/output --mesh-only
```

To export specific animations to FBX:
```bash
converter_cli.exe -i path/to/model.txt -o path/to/output --anim-types walk idle
```


## GNU GENERAL PUBLIC LICENSE
### Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc.  
51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA  
Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.

### Preamble

The GNU General Public License is a free, copyleft license for software and other kinds of works. The licenses for most software are designed to take away your freedom to share and change it. By contrast, the GNU General Public License is intended to guarantee your freedom to share and change all versions of a program— to make sure it remains free software for all its users.


### Full License Text
[Full License Text](https://www.gnu.org/licenses/gpl-3.0.html)