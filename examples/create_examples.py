from pathlib import Path
import sys, os, shutil

def create_hips():
    ROOT = Path(os.path.dirname(os.path.realpath(__file__))).parent

    hda_dir = ROOT.joinpath("otls")
    hdas = list(hda_dir.glob("*.hda"))
    template = ROOT.joinpath("examples/BASE.hip")

    for h in hdas:
        dst = ROOT.joinpath("examples")
        dst = dst.joinpath(h.stem + ".hip")
        if not os.path.exists(dst):
            shutil.copy(template, dst)

create_hips()
