# This file is only used to generate the list of fonts for the fonts package.
# This is not used by anything else. Just a standalone script.
# The list of Literals it generates is put in the __init__.py file
# of rich_pyfiglet.pyfiglet.fonts

import os
from rich_pyfiglet.pyfiglet import fonts

ext_fonts_pkg = os.path.dirname(fonts.__file__)

all_files: list[str] = []
for root, dirs, files in os.walk(ext_fonts_pkg):
    for file in files:
        # Create relative path from package root
        rel_path = os.path.relpath(os.path.join(root, file), ext_fonts_pkg)
        all_files.append(rel_path)

all_files = sorted(all_files)

# write all_files out to a file:
with open("src/rich_pyfiglet/pyfiglet/fonts/__init__.py", "w") as f:
    f.write('"Fonts module for rich_pyfiglet."\n\n' "from typing import Literal \n\n")
    f.write("ALL_FONTS = Literal[\n")
    for file in all_files:
        if file.endswith(".flf") or file.endswith(".tlf"):
            # remove the .txt extension
            font_name = file[:-4]
            f.write(f'"{font_name}",\n')
    f.write("]\n")
