from PyQt4 import QtGui, QtCore
from popUpNew_ui import popUpNewUI
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

class popUpNew(popUpNewUI):

    def __init__(self):
        self.parentFolder = './'
        self.casename = 'newCase'
        popUpNewUI.__init__(self)
        self.lineEdit_parent.setText(self.parentFolder)
        self.lineEdit_case.setText(self.casename)

    def chooseFolder(self):
        self.parentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Parent Folder', self.parentFolder);
        self.lineEdit_parent.setText(self.parentFolder)

    def getData(self):
        return [self.lineEdit_case.text(), self.lineEdit_parent.text()]
    #    print "se acepta"
        

