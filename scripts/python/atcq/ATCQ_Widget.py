from __future__ import print_function

import sys, os
try:
    from pathlib import Path
    import urllib.request as url
except:
    from pathlib2 import Path
    import urllib2 as url

try:
    import hou
    import toolutils
except:
    pass

from PIL import Image
import json

import numpy as np

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtCore
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebChannel import QWebChannel

# Can we use the houdini embedded browser at all? https://www.sidefx.com/docs/houdini/hom/browserpython.html

'''
TODO
Cache the quantize result so we can change the target colours without redoing
improve button layout
add this stuff to palette manager base
'''

class ATCQ_Dialog(QDialog):
    def __init__(self, node=None):
        super(ATCQ_Dialog, self).__init__()
        self.SCRIPT_PATH = Path(os.path.realpath(__file__)).parent
        self.node = node
        self.initUI()

    def initUI(self):
        QtCore.qInstallMessageHandler(self.handler) # ignore warnings

        vbox = QVBoxLayout(self)
        self.webEngineView = QWebEngineView()

        self.channel = QWebChannel()
        self.channel.registerObject("atcq", self)
        self.webEngineView.page().setWebChannel(self.channel)
        self.webEngineView.loadFinished.connect(self.on_load_finished)
        self.load_page()

        vbox.addWidget(self.webEngineView)
        self.setLayout(vbox)
        self.setGeometry(100, 100, 650, 250)
        self.setWindowTitle('ATCQ')
        self.show()

    def handler(self, msg_type, msg_log_context, msg_string):
        pass

    def load_page(self):
        # SETHTML DO NOT USE! This will not initialise the working directory and so you cannot load external js, css etc
        # MUST use setURL with the correct local URL for imports to work
        file = str(self.SCRIPT_PATH.joinpath("web/index.html"))
        self.webEngineView.setUrl(QtCore.QUrl.fromLocalFile(file))

    @QtCore.Slot()
    def on_load_finished(self):
        p = str(self.SCRIPT_PATH.joinpath("atcq_image.png"))
        pp = p.replace("\\", "/")
        self.webEngineView.page().runJavaScript("window.setImagePath('{}');".format(pp))

    @QtCore.Slot(str)
    def resize(self, file):
        try:
            im = Image.open(file)
            print("file image resized")
        except:
            im = Image.open(url.urlopen(file))
            print("url image resized")
        sc = im.resize((350,350))
        write_path = str(self.SCRIPT_PATH.joinpath("atcq_image.png"))
        sc.save(write_path, format="PNG")
        print("resized image")
        self.webEngineView.page().runJavaScript('window.setStatus("Image processed. Quantization will follow...");')

    # https://stackoverflow.com/questions/58210400/how-to-receive-data-from-python-to-js-using-qwebchannel
    # @QtCore.Slot(str) @QtCore.Slot(QJsonValue) @QtCore.Slot("QJsonObject") @QtCore.Slot(list)
    @QtCore.Slot(str, str) # generic json str which we parse
    def send_palette(self, palette, weights):
        self.palette = json.loads(palette)
        self.weights = json.loads(weights)
        self.setPaletteManagerRamp()

    @QtCore.Slot(str)
    def print(self, t):
        print(t)

    @QtCore.Slot(float)
    def exit(self, a):
        sys.exit()

    '''
    Setting Ramp on the Palette Manager
    '''

    def colourConvert(self, col):
        c = col
        if (sum(col) / float(len(col)) > 1.0):
            c = [a / 255.0 for a in col]
        return tuple(c)

    # process these in the palette manager
    def setPaletteManagerRamp(self):
        ramp = self.node.parm("ramp")
        nodes = len(self.palette)

        wts = self.weights
        wts.insert(0, 0) # prepend 0 so cumsum gives us the correct positions
        placements = np.cumsum(wts)

        ramp.set(nodes)
        for i in range(nodes):
            posParm = self.node.parm(ramp.name() + str(i + 1) + "pos")
            posParm.set(placements[i])

            # set colours, check if hex or rgb triplet
            v = self.palette[i % len(self.palette)]
            clrParm = self.node.parmTuple(ramp.name() + str(i + 1) + "c")
            clrParm.set(self.colourConvert(v))

            # set basis to constant
            basisParm = self.node.parm(ramp.name() + str(i + 1) + "interp")
            basisParm.set(0)

def main():
    app = QApplication(sys.argv)
    ex = ATCQ_Dialog()
    ex.show()
    app.exec_()
    # sys.exit(app.exec_())

if __name__ == '__main__':
    main()

# note on returning values to js without calling js function explicitly?
# https://stackoverflow.com/questions/58210400/how-to-receive-data-from-python-to-js-using-qwebchannel
# In C++ so that a method can return a value it must be declared as Q_INVOKABLE and the equivalent in PyQt is to use result in the @pyqtSlot decorator:
# @QtCore.pyqtSlot(int, result=int)
# def getRef(self, x):
#     print("inside getRef", x)
#     return x + 5