from kiutils.symbol import SymbolLib # https://kiutils.readthedocs.io/en/latest/module/kiutils.html#kiutils.footprint.Footprint.position
from kiutils.items.common import Position
import sys
import re
from colored_terminal import *

SPACE_BETWEEN_PIN_X = 1.27*20
SPACE_BETWEEN_PIN_Y = 1.27*2
    
if __name__ == "__main__":
    print_yellow("<Kicad Tool to group symbol pins>\n")
    if len(sys.argv) != 3:
        if not (len((sys.argv)) >= 3 and int(sys.argv[2]) == -1):
            print(f"too little arguments: ({len(sys.argv)})")
            print("start this tool with these arguments:")
            print("[libary_path] [nr_symbol]")
            print("- filepath to libary")
            print(
                "- choose [number] wich simbols pins y wanna regroup. Set to -1 to just show the list"
            )
            sys.exit()

    # Load the symbol library
    filepath = sys.argv[1]
    lib = SymbolLib.from_file(filepath)

    print_cyan("Found Symbols:\n")
    # Print available symbols
    for nr, symbol in enumerate(lib.symbols):
        print(f"  [{nr}] Symbol name: {symbol.entryName}")

    # select symbol from libary
    number = sys.argv[2]
    if not number.isnumeric():
        print("please enter number")
        sys.exit()
    if int(number) == -1:
        sys.exit()
    selectedIc = lib.symbols[int(number)]

    print_cyan("Selected IC:\n")
    print(f"Symbol name: {selectedIc.entryName}")
    print(f"Amount of pins: {len(selectedIc.pins)}")
    if len(selectedIc.pins) == 0:
        print_red(
f'Error:\n\
  go to {filepath}\n\
  find {selectedIc.entryName}\n\
  go to pin section\n\
  delete (above pins) the complete line "(symbol "{selectedIc.entryName} (in_bom yes) (on_board yes)"\n\
  as well as the matching brackets at the end.\n'
        )
        sys.exit()
        sys.exit()
    print("Properties:")
    for prop in selectedIc.properties:
        print(f"  {prop.key} = {prop.value}")

    # groups pins
    PinDictory = {}
    for pin in selectedIc.pins:
        groupName = pin.name[:3]  # grouping logic
        if groupName not in PinDictory:
            PinDictory[groupName] = []
        PinDictory[groupName].append(pin)

    # sort groups
    def natural_key(pin):
        # extract prefix letters and numeric suffix for sorting
        match = re.match(r"([a-zA-Z]+)(\d+)", pin.name)
        if match:
            prefix, num = match.groups()
            return (prefix, int(num))
        else:
            return (pin.name, 0)  # fallback

    sortedPinDictionary = {}
    for groupName, pinList in PinDictory.items():
        pinList.sort(key=natural_key)
        sortedPinDictionary[groupName] = pinList
    PinDictory = sortedPinDictionary

    # # changes coordinates from these pins
    for x, (groupName, pinList) in enumerate(PinDictory.items()):
        # try:
        for y, pin in enumerate(pinList):
            pin.position.X = x * SPACE_BETWEEN_PIN_X
            pin.position.Y = -y * SPACE_BETWEEN_PIN_Y - SPACE_BETWEEN_PIN_Y
            pin.position.angle = 0
            
    # saved modified file
    filepath = sys.argv[1]
    lib.to_file(filepath)

    print_yellow("conversion succesful\n")
