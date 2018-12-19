import os
import sys
import time

def AutoComp():
    INSCRIPT = sys.argv[1] # template file
    OUTSCRIPT = sys.argv[2] # new save location
    OUTSCRIPTDIR = os.path.split(OUTSCRIPT)[0]
    if not os.path.exists(OUTSCRIPTDIR):
        os.makedirs(OUTSCRIPTDIR)
    READPATH = sys.argv[3] # frames to read
    WRITEPATH = sys.argv[4] # writepath
    FPS = sys.argv[5] # hipfile framerate
    FRAMERANGE = sys.argv[6:8] # hipfile framerate
    IMAGERES = sys.argv[8:10] # hipfile framerate
    AOVS = sys.argv[10:]

    nuke.scriptOpen( INSCRIPT )
    ROOT = nuke.toNode("root")

    ## ====================================
    # Set framerate and frame ranges
    ## ====================================
    ROOT['fps'].setValue(float(FPS))
    newFirst = int(FRAMERANGE[0])
    newLast = int(FRAMERANGE[1])
    ROOT['first_frame'].setValue(newFirst)
    ROOT['last_frame'].setValue(newLast)
    for n in nuke.allNodes('Read'):
        n['first'].setValue(newFirst)
        n['last'].setValue(newLast)
    for n in nuke.allNodes('Write'):
        n['first'].setValue(newFirst)
        n['last'].setValue(newLast)
    # set frame range on the background solid. Maybe we should try setting this on any node?
    try:
        bg = nuke.toNode( "BACKGROUND_SOLID" )
        bg["first"].setValue(newFirst)
        bg["last"].setValue(newLast)
    except:
        print "no background solid node found"

    # Set ROOT format from rendered
    restr = " ".join(IMAGERES)
    Format_AutoComp = restr + " 0 0 " + restr + " 1 Format_AutoComp"
    nuke.addFormat(Format_AutoComp)
    ROOT['format'].setValue('Format_AutoComp')

    readMain = nuke.toNode( "Read1" )
    writeMain = nuke.toNode( "Write1" )
    readMain['file'].setValue( READPATH )
    readMain.forceValidate()

    # # # reconstruct outpath from vars TODO or just feed in from hou..
    writeMain['file'].setValue( WRITEPATH + writeMain.name() + "_####.exr" )

    # create shuffles
    shuffleNodes = []
    beautyNodes = []
    if AOVS:
        beauty_layers = ["diffuse", "reflection", "specular", "sss", "refraction", "emission", "gi", "volume"]
        beauty_layersC4D = ["DiffuseLighting", "Reflections", "SpecularLighting", "SubSurfaceScatter", "Refractions", "Emission", "GlobalIllumination", "VolumeLighting"]
        beauty_layers += beauty_layersC4D
        beau = [a for a in AOVS if a in beauty_layers]
        for aov in AOVS:
            if aov == "end":
                pass #ignore the extra sysarg which seemed to be necessary if no aovs are present..?
            shuf = nuke.nodes.Shuffle()
            shuf.setName("shuffle_"+aov)
            shuf.setInput(0, readMain)
            shuf['in'].setValue(str(aov))
            shuffleNodes.append(shuf)
        beautyNodes = [nuke.toNode("shuffle_"+l) for l in beau]

    if beautyNodes:
        # m = nuke.nodes.Merge(inputs=beautyNodes)
        m = nuke.createNode('Merge2')
        beautyNodes.insert(2, None) # prevent mask being created...
        for i, b in enumerate(beautyNodes):
            m.setInput(i, b)
        m['operation'].setValue("plus")

    cropNode = nuke.toNode("Crop1")
    cropNode["box"].setR(int(IMAGERES[0]))
    cropNode["box"].setT(int(IMAGERES[1]))
    cropNode["reset"].execute()

    # time.sleep(8)
    nuke.scriptSave( OUTSCRIPT )

AutoComp()