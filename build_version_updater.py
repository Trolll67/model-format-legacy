import re
import sys


def update_version_in_file(filepath, new_version, pattern):
    try:
        with open(filepath, 'r') as f:
            content = f.read()

            match = re.search(pattern, content)
            if match:
                old_version = match.group(1)
                content = content.replace(old_version, new_version)

                with open(filepath, 'w') as f:
                    f.write(content)

                print(f"Version updated from {old_version} to {new_version} in {filepath}")
                return 0
            else:
                print(f"Version not found in {filepath}")
                return 1
    except Exception as e:
        print(f"Error updating version in {filepath}: {e}")
        return 1


if len(sys.argv) < 2:
    print("No version provided")
    sys.exit(1)
else:
    version = sys.argv[1]
    if version.startswith('v'):
        version = version[1:]

    print(f"Version: {version}")

    exit_code = update_version_in_file('src/rmb_rab_import.py', version, r"__version__ = '(\d+\.\d+)'")
    if exit_code != 0:
        sys.exit(exit_code)
    exit_code = update_version_in_file('src/converter.py', version, r"Version (\d+\.\d+)")
    if exit_code != 0:
        sys.exit(exit_code)
    exit_code = update_version_in_file('src/converter_gui.py', version, r"GUI Tool v(\d+\.\d+)")
    sys.exit(exit_code)