# this script is used to move diverdata files from the DiverOffice folder to the project folder
# and to rename the files according to the naming convention used in the project folder.

import shutil
from pathlib import Path


def rename(old: str):

    if "Y3747" in old:
        core = old.split("_")[0] + "_" + old.split("_")[1]
    else:
        core = old.split("_")[0]

    if "Freatisch" in core:
        newname = core.replace(" - Freatisch", "_1")
    elif "Freat" in core:
        newname = core.replace(" - Freat", "_1")
    elif "WVP1" in core:
        if "B28" in core:
            core = core.replace("B28", "B27")
        newname = core.replace(" - WVP1", "_2")
    elif "WVP2" in core:
        if "B25A" in core:
            newname = core.replace(" - WVP2", "_3")
        else:
            newname = core.replace(" - WVP2", "_3")
    elif "TD" in core:
        newname = core.replace(" - TD-diver", "_TD")
    elif "KNMI 240 Schiphol" in core:
        newname = "KNMI 240 Schiphol"

    if "BL" in newname:
        newname = newname.replace("BL", "BL-")

    if "Z13PB600-02_2" == newname:
        newname = "Z13PB600_2"

    if "Z13PB600-02_1" == newname:
        newname = "Z13PB600_1"

    return newname + ".csv"


dir_diver_office = Path(r"C:/Users/melman/AppData/Roaming/DiverOffice/IJmuiden/CSV")
project_dir = Path(
    r"N:/Projects/11207500/11207510/B. Measurements and calculations/03_divers/diverdata"
)

failed = []
for old_path in dir_diver_office.glob("*.csv"):
    print(old_path)

    try:
        old_name = old_path.stem
        new_name = rename(old_name)
        new_path = project_dir / new_name

        print(old_name, new_name)
        shutil.move(old_path, new_path)
    except (KeyError, OSError, shutil.Error):
        failed.append(old_name)

print(failed)
