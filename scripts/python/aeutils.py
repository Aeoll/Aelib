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

    # Default materials with AE Gallery application?
    # shop = hou.node("/shop")
    # mat = shop.createNode("RS_Material", "Base")
    # entries = hou.galleries.galleryEntries(node_type=hou.nodeType(hou.shopNodeTypeCategory(), "RS_Material"))
    # if entries:
    #     for entry in entries:
    #         entry.applyToNode(mat)

    # inc = shop.createNode("rs_incandescent", "Solid")
    # inc.move(hou.Vector2(0, 1))
    # entries = hou.galleries.galleryEntries(node_type=hou.nodeType(hou.shopNodeTypeCategory(), "rs_incandescent"))
    # if entries:
    #     for entry in entries:
    #         entry.applyToNode(inc)

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