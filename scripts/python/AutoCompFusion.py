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
## Spawn dialog if the comp already exists, asking to just open it instead?

# def addNukeToPath():
#     path = os.environ['PATH']
#     path_values = path.split(";")
#     nuke_install = "C:\\Program Files\\Nuke11.1v3"
#     if nuke_install in path_values:
#         pass
#     else:
#         os.environ["PATH"] += os.pathsep + nuke_install

# def makeEnv():
#     my_env = os.environ.copy()
#     home = expanduser("~")
#     h = os.path.split(home)[0] + "\\.nuke"
#     my_env["NUKE_PATH"] = "Z:\\_MvsM_Resource\\_Nuke_Global_Setup" + ";" + h
#     return my_env

# get output image file resolution
# def extractImageResolution(rsrop):
#     CAMRES = [1920, 1080]
#     cam = rsrop.evalParm("RS_renderCamera")
#     camnode = hou.node(cam)
#     override = rsrop.evalParm("RS_overrideCameraRes")
#     if override:
#         overscale = rsrop.evalParm("RS_overrideResScale")
#         if overscale == 7:
#             CAMRES = list(rsrop.evalParmTuple("RS_overrideRes"))
#         else:
#             try:
#                 origres = list(camnode.evalParmTuple("res"))
#             except:
#                 origres = CAMRES
#             scaledict = { 0:0.1, 1:0.2, 2:0.25, 3:0.33333333, 4:0.5, 5:0.6666667, 6:0.75 }
#             CAMRES = [int(x * scaledict.get(overscale)) for x in origres]
#     else:
#         try:
#             CAMRES = camnode.evalParmTuple("res")
#         except:
#             print "no camera found.. maybe using a switcher?"
#     return CAMRES

# call nuke command line (no-gui mode with -t) with the AutoComp script, passing in required sys.argv arguments
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

    # # if the comp already exists, check for overwrite
    # if os.path.exists(newcomp):
    #     diag = QDialog()
    #     diag.setStyleSheet(hou.ui.qtStyleSheet())
    #     qm = QMessageBox()
    #     ret = qm.question(diag, '', "Comp already exists - Are you sure you want to overwrite?", qm.Yes | qm.No | qm.Cancel)
    #     if ret == qm.No:
    #         my_env = makeEnv()
    #         subprocess.Popen([FUSION, newcomp], env=my_env)
    #         sys.exit()
    #     if ret == qm.Cancel:
    #         sys.exit()

    # # get ROP output path to set the read node
    # node_type = hou.nodeType(hou.ropNodeTypeCategory(), "Redshift_ROP")
    # inst = node_type.instances()
    # n = inst[0]
    # # Use Selected node if its a Redshift_ROP
    # sel = hou.selectedNodes()
    # if sel and sel[0].type() == hou.nodeType(hou.ropNodeTypeCategory(), "Redshift_ROP"):
    #     n = sel[0]
    # framerange = str(int(n.evalParm("f1"))) +" "+ str(int(n.evalParm("f2")))

    # # get output image file resolution
    # res = extractImageResolution(n)
    # imageResolution = " ".join([str(x) for x in res])
    # OUT_PATH = n.parm('RS_outputFileNamePrefix').unexpandedString()
    # OUT_PATH = OUT_PATH.replace("$F4", "####")
    # OUT_PATH = OUT_PATH.replace("${OS}", n.name())
    # OUT_PATH = hou.expandString(OUT_PATH)

    # # get image planes from RS ROP and pass to the command line. arbitrary length
    # aovs = []
    # if n is not None:
    #     aov_off = n.evalParm('RS_aovAllAOVsDisabled')
    #     num_aov = n.evalParm('RS_aov')
    #     if num_aov > 0 and not aov_off:
    #         for a in xrange(num_aov):
    #             # aov_type = n.parm("RS_aovID_1") # we may need this to tweak some aovs (depth.Z rather than Z etc?)
    #             aov_name = n.evalParm("RS_aovSuffix_"+str(a+1))
    #             aovs.append(aov_name)
    # if len(aovs) > 0:
    #     aovstr = " ".join(aovs)
    # else:
    #     aovstr = None

    # fps = str(hou.expandString("$FPS"))
    # if aovstr:
    #     cmd = [FUSION, '-t', scriptLoc + "AutoComp.py", template, newcomp, OUT_PATH, compwritepath, fps, framerange, imageResolution, aovstr, 'end']
    # else:
    #     cmd = [FUSION, '-t', scriptLoc + "AutoComp.py", template, newcomp, OUT_PATH, compwritepath, fps, framerange, imageResolution, 'end']
    # strcmd = " ".join(cmd)
    # #time.sleep(4)
    # p1 = subprocess.Popen(strcmd)
    # p1.wait()

    # Open the file with the correct environment
    # my_env = makeEnv()
    subprocess.Popen([FUSION, newcomp])

run()