import hou

def createRedshiftRop(hou_parent):
    # Code for /out/Redshift_ROP1
    hou_node = hou_parent.createNode("Redshift_ROP", "Redshift_ROP1", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-1.6944, 0.8942))
    hou_node.bypass(False)
    hou_node.hide(False)
    hou_node.setLocked(False)
    hou_node.setSelected(False)
    
    # Code for /out/Redshift_ROP1/trange parm 
    if locals().get("hou_node") is None:
        hou_node = hou.node("/out/Redshift_ROP1")
    hou_parm = hou_node.parm("trange")
    hou_parm.set("normal")
    
    
    # Code for /out/Redshift_ROP1/f parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node("/out/Redshift_ROP1")
    hou_parm_tuple = hou_node.parmTuple("f")
    
    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)
    
    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)
    
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)
    
    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)
    
    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)
    
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)
    
    
    # Code for /out/Redshift_ROP1/RS_mainSwitcher1 parm 
    if locals().get("hou_node") is None:
        hou_node = hou.node("/out/Redshift_ROP1")
    hou_parm = hou_node.parm("RS_mainSwitcher1")
    hou_parm.set(1)
    
    
    # Code for /out/Redshift_ROP1/RS_settingsSwitcher1 parm 
    if locals().get("hou_node") is None:
        hou_node = hou.node("/out/Redshift_ROP1")
    hou_parm = hou_node.parm("RS_settingsSwitcher1")
    hou_parm.set(2)
    
    
    # Code for /out/Redshift_ROP1/UnifiedMinSamples parm 
    if locals().get("hou_node") is None:
        hou_node = hou.node("/out/Redshift_ROP1")
    hou_parm = hou_node.parm("UnifiedMinSamples")
    hou_parm.set(16)
    
    
    # Code for /out/Redshift_ROP1/RS_iprOverrideCameraRes parm 
    if locals().get("hou_node") is None:
        hou_node = hou.node("/out/Redshift_ROP1")
    hou_parm = hou_node.parm("RS_iprOverrideCameraRes")
    hou_parm.set(0)
    
    
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)
    
    hou_node.setUserData("___Version___", "16.0.736")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("16.0.736")
    return hou_node
    
def createRedshiftIPR(hou_parent):
    # Code for /out/Redshift_IPR1
    hou_node = hou_parent.createNode("Redshift_IPR", "Redshift_IPR1", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0, 0))
    hou_node.bypass(False)
    hou_node.hide(False)
    hou_node.setLocked(False)
    hou_node.setSelected(False)
    
    # Code for /out/Redshift_IPR1/f parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node("/out/Redshift_IPR1")
    hou_parm_tuple = hou_node.parmTuple("f")
    
    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)
    
    # Code for last keyframe.
# Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)
    
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)
    
    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)
    
    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)
    
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)
    
    
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)
    
    hou_node.setUserData("___Version___", "")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    return hou_node
    

