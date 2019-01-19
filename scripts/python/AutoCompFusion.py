import subprocess
import os
from os.path import expanduser
import sys
import time
import hou
import shutil

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

## ======================================
## TODO
## ======================================
## Modify nuke auto-comp script to work for fusion??
## no luck so far

def run():
    floc = os.path.dirname(os.path.abspath(__file__))
    scriptLoc = floc
    templateLoc = floc
    template = templateLoc + "/template.comp"
    # FUSION = "C:\Program Files\Blackmagic Design\Fusion 9\Fusion.exe"
    FUSION = "/opt/BlackmagicDesign/Fusion9/Fusion"


    newcomp = hou.expandString("$HIP") + "/comp/" + hou.expandString("$HIPNAME") + "_autocomp.comp"
    if not os.path.exists(os.path.dirname(newcomp)):
        os.makedirs(os.path.dirname(newcomp))
    shutil.copy2(template, newcomp)

    # set the save path for the autocomp and part of the path for its write nodes
    compwritepath = hou.expandString("$HIP") + "/comp/render/" + hou.expandString("$HIPNAME") + "_"
 
 
 
    subprocess.Popen([FUSION, newcomp])

run()