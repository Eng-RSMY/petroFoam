from PyQt4 import QtGui, QtCore
from petroFoam_ui import petroFoamUI
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class petroFoam(petroFoamUI):
    def __init__(self):
        petroFoamUI.__init__(self)
        self.currentFolder = './'
    	#self.comboBoxMesh.currentIndexChanged[str].connect(self.updateMeshPanel)

    def updateMeshPanel(self):
        QtGui.QMessageBox.about(self, "ERROR", "Primero se debe calcular!")

    def importMesh(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select Mesh to Import', './', 'Mesh Files (*.msh)');
        print fileName

    def openCase(self):
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Open Folder', './');

    def saveAsCase(self):
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './');

    def saveCase(self):
        print('Se guarda como %s',self.currentFolder)

    def openTerminal(self):
        os.system('gnome-terminal &')
        #os.system('$TERM . &')

    def openBrowse(self):
        os.system('nautilus . &')

    def closeEvent(self, evnt):
        print "se intenta cerrar"
        #evnt.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = petroFoam()
    window.show()
    sys.exit(app.exec_())
