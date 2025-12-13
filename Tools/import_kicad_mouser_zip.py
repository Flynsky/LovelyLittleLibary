from pathlib import Path
from kiutils.symbol import SymbolLib # https://kiutils.readthedocs.io/en/latest/module/kiutils.html#kiutils.footprint.Footprint.position
from kiutils.footprint import Footprint# https://kiutils.readthedocs.io/en/latest/module/kiutils.html#kiutils.footprint.Footprint.position
from kiutils.items.common import Position
import sys
import re
import zipfile
import shutil
from colored_terminal import *

if __name__ == '__main__':
    print_magenta("<Kicad Tool to import shematic, footprint and 3D Model from mouser to libary>\n\n")
    
    # handles argvs
    if len(sys.argv) != 3:
        print_yellow(f"  too little arguments: ({len(sys.argv)})\n")
        print_yellow("  start this tool with these arguments:\n")
        print_yellow("  [path_zip] [path_libary_folder]\n")
        sys.exit()
    
    PATH_ZIP = Path(sys.argv[1]) # path to zip where symbols to copy are
    PATH_LIBRARY_DIR = Path(sys.argv[2]) # path to libary where footprint should go
    PATH_LIBRARY_SYMBOLS = Path() # path to simbol libary
    PATH_LIBARY_PRETTY = Path() #path to footprint.pretty in libary
    PATH_TEMP_DIR = PATH_LIBRARY_DIR / "temporary" # temporaty folder to export ZIP to
    PATH_SYMBOL_2COPY = Path() # path to symbols which y wanna copy
    
    print_magenta(f'>extracting zip\n')
    # Extract zip contents to temporary directory
    with zipfile.ZipFile(PATH_ZIP, "r") as zip_ref:
        zip_ref.extractall(PATH_TEMP_DIR)
    print("\n",end='')
    
    print_magenta(f'>searching for target symbol/footprints\n')
    # search for a kicad symbol libary
    sym_dirs = list(PATH_LIBRARY_DIR.rglob("*.kicad_sym"))
    print_cyan(f' target symbol libary:')
    if len(sym_dirs):
        PATH_LIBRARY_SYMBOLS = sym_dirs[0]
        print_white(f'"{sym_dirs[0]}"\n')
    else:
        if PATH_TEMP_DIR.exists() and PATH_TEMP_DIR.is_dir():
            shutil.rmtree(PATH_TEMP_DIR)
        raise Exception("ERROR: Not found")
    
    # search for a footprint folder
    pretty_dirs = [
        p for p in PATH_LIBRARY_DIR.rglob("*") if p.is_dir() and p.name.endswith(".pretty")
    ]
    print_cyan(f' target footprints:')
    if len(pretty_dirs):
        # found footprint folder
        print_white(f' "{pretty_dirs[0]}"\n')
        PATH_LIBARY_PRETTY = pretty_dirs[0]
    else:
        # creates footprint folder
        PATH_LIBARY_PRETTY = PATH_LIBRARY_DIR / (PATH_SYMBOL_2COPY.stem + ".pretty")
        PATH_LIBARY_PRETTY.mkdir(parents=True, exist_ok=True)
        print_white(f'created "{PATH_LIBARY_PRETTY}"\n')

    # search for a source kicad symbol libary in Source
    sym_dirs = list(PATH_TEMP_DIR.rglob("*.kicad_sym"))
    print_cyan(f' source symbol libary:')
    if len(sym_dirs):
        PATH_SYMBOL_2COPY = sym_dirs[0]
        print_white(f'"{sym_dirs[0]}"\n')
    else:
        if PATH_TEMP_DIR.exists() and PATH_TEMP_DIR.is_dir():
            shutil.rmtree(PATH_TEMP_DIR)
        raise Exception("Nothing found\n")
    print("\n",end='')
    
    print_magenta(f'>copying symbol libary\n')
    # copys Symbol to libary
    # print(PATH_SYMBOL_2COPY)
    symbolLibrary = SymbolLib.from_file(PATH_LIBRARY_SYMBOLS)
    symbolToCopy = SymbolLib.from_file(PATH_SYMBOL_2COPY)
            
    print_cyan(f" length target symbol libary: {len(symbolLibrary.symbols)}\n")
        
    for symbol in symbolToCopy.symbols:
        print_cyan(f' found symbol to insert: ')
        print_white(f'"{symbol.entryName}"\n')
        if any(s.entryName == symbol.entryName for s in symbolLibrary.symbols):
            print_yellow("-> already in the library. Skipping.\n")
        else:
            print("-> writes symbol to libary")
            symbolLibrary.symbols.append(symbolToCopy.symbols[0])
        
    # overwrites existing libary
    print_cyan(f' new length of target libary: {len(symbolLibrary.symbols)}\n')
    symbolLibrary.to_file(PATH_LIBRARY_SYMBOLS)
    print("\n",end='')

    print_magenta(f'>Copying footprint\n')
    # copys Footprint
    print_cyan(f' copies footprint:')
    for model_file in PATH_TEMP_DIR.rglob("*.kicad_mod"):
        print(f'"{model_file.name}"')
        fp = Footprint.from_file(model_file)  # load from source
        for model in fp.models:
            print_white(f'  -adjusted 3D model path')
            print_white(f' from "{model.path}" | ')
            model.path = "${KIPRJMOD}/libary/3D/" + model.path
            print_white(f'to "{model.path}"')
        dest_path = PATH_LIBARY_PRETTY / model_file.name
        fp.to_file(dest_path) 
    print("\n",end='')
    print("\n",end='')
    
    print_magenta(f'>Copying 3D files\n')
    PATH_LIBARY_3D_DIR = PATH_LIBRARY_DIR / "3D"
    PATH_LIBARY_3D_DIR.mkdir(parents=True, exist_ok=True)
    foundOne = False
    print_cyan(f' copies 3D_model:')
    # print_yellow(f'path: "{PATH_TEMP_DIR}"\n')
    for model_file in PATH_TEMP_DIR.rglob("*.stp"):
        print(f'"{model_file.name}"',end='')
        shutil.copy2(model_file, PATH_LIBARY_3D_DIR / model_file.name)
        foundOne = True
    if not foundOne:
        print_red(f' didn t found a 3D model')
    print("\n",end='')
    print("\n",end='')

    # deletes temp
    print_magenta("<delete temp\n")
    if PATH_TEMP_DIR.exists() and PATH_TEMP_DIR.is_dir():
        shutil.rmtree(PATH_TEMP_DIR)
    print("\n",end='')
    
    print_magenta("<finished\n")
    
