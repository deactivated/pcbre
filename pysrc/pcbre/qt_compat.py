import os

default_binding = "pyqt5"

requested_binding = os.environ.get('QT_API', '').lower()
if requested_binding not in ("pyqt4", "pyside", "pyqt5"):
    requested_binding = default_binding

if requested_binding == "pyqt4":
    from PyQt4 import QtGui, QtCore, QtOpenGL

    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

    def QGLContext(f):
        return QtOpenGL.QGLContext(f, None)

    def QtLoadUI(f):
        from pcbre.qt_compat import QtUiTools
        loader = QtUiTools.QUiLoader()
        return loader.load(f)

    def getOpenFileName(*args, **kwargs):
        return QtGui.QFileDialog.getOpenFileName(*args, **kwargs)

    def getSaveFileName(*args, **kwargs):
        return QtGui.QFileDialog.getSaveFileName(*args, **kwargs)

elif requested_binding == "pyside":
    from PySide import QtGui, QtCore, QtOpenGL

    def QGLContext(f):
        return QtOpenGL.QGLContext(f)

    def QtLoadUI(f):
        from PySide import uic
        return uic.loadUi(f)

    def getOpenFileName(*args):
        fn, _ = QtGui.QFileDialog.getOpenFileName(*args)
        return fn

    def getSaveFileName(*args, **kwargs):
        fn, _ = QtGui.QFileDialog.getSaveFileName(*args, **kwargs)
        return fn

elif requested_binding == "pyqt5":
    from PyQt5 import QtGui, QtCore, QtOpenGL, QtWidgets

    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

    def QGLContext(f):
        return QtOpenGL.QGLContext(f, None)

    def QtLoadUI(f):
        from pcbre.qt_compat import QtUiTools
        loader = QtUiTools.QUiLoader()
        return loader.load(f)

    def getOpenFileName(*args, **kwargs):
        return QtWidgets.QFileDialog.getOpenFileName(*args, **kwargs)

    def getSaveFileName(*args, **kwargs):
        return QtWidgets.QFileDialog.getSaveFileName(*args, **kwargs)


__all__ = ["QtGui", "QtCore", "QtOpenGL", "QtLoadUI", "QGLContext"]
