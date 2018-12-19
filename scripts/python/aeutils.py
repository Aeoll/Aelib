import hou
import autoNode

import glob
import os
import re

def init_RS():
    # Create RS ROPs
    out = hou.node("/out")
    rop = autoNode.createRedshiftRop(out)
    rop.setParms({"RS_renderCamera":"cam_1080"})
    autoNode.createRedshiftIPR(out)

    # Default camera
    obj = hou.node("/obj")
    cam = obj.createNode("cam", "cam_1080")
    cam.setParms({"resx": 1920, "resy": 1080})
    
    # Default Light
    dome = obj.createNode("rslightdome", "Dome")
    dome.move(hou.Vector2(0, 1))

    # does this work form a shelf?
    hou.hscript('Redshift_objectSpareParameters')
    hou.hscript('Redshift_cameraSpareParameters')