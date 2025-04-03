def rename_well(old: str):
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

    if "BL" in newname:
        newname = newname.replace("BL", "BL-")

    if "Z13PB600-02_2" == newname:
        newname = "Z13PB600_2"

    if "Z13PB600-02_1" == newname:
        newname = "Z13PB600_1"

    return newname
