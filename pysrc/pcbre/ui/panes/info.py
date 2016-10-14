from pcbre.qt_compat import QtCore, QtGui, QtWidgets


__author__ = 'davidc'


class InfoWidget(QtWidgets.QDockWidget):

    def __init__(self, project):
        super(InfoWidget, self).__init__("Object Information")
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                             QtCore.Qt.RightDockWidgetArea)
