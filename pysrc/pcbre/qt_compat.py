import os

default_binding = "pyqt5"

requested_binding = os.environ.get("QT_API", "").lower()
if requested_binding not in ("pyqt5",):
    requested_binding = default_binding

if requested_binding == "pyqt5":
    from PyQt5 import QtGui, QtCore, QtOpenGL, QtWidgets

    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

    def QGLContext(f):
        return QtOpenGL.QGLContext(f)

    def QtLoadUI(f):
        from pcbre.qt_compat import QtUiTools

        loader = QtUiTools.QUiLoader()
        return loader.load(f)

    def getOpenFileName(*args, **kwargs):
        return QtWidgets.QFileDialog.getOpenFileName(*args, **kwargs)

    def getSaveFileName(*args, **kwargs):
        return QtWidgets.QFileDialog.getSaveFileName(*args, **kwargs)


__all__ = ["QtGui", "QtCore", "QtOpenGL", "QtLoadUI", "QGLContext"]
