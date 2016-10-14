from pcbre.ui.dialogs.layerviewsetup import LayerViewSetupDialog
from pcbre.ui.dialogs.stackupsetup import StackupSetupDialog
import time
__author__ = 'davidc'


from PySide import QtGui, QtCore


class StackupSetupDialogAction(QtGui.QAction):

    def __init__(self, window):
        self.__window = window
        QtGui.QAction.__init__(self, "Edit Stackup",
                               window, triggered=self.__action)

    def __action(self):
        dlg = StackupSetupDialog(self.__window, self.__window.project)
        dlg.exec_()


class RebuildConnectivityAction(QtGui.QAction):

    def __init__(self, window):
        self.__window = window

        QtGui.QAction.__init__(self, "Rebuild Connectivity",
                               window, triggered=self.__action)

    class CancelException(Exception):
        pass

    def __action(self):
        self.__pd = None

        try:
            self.__window.project.artwork.rebuild_connectivity(
                progress_cb=self.__progress)
        except RebuildConnectivityAction.CancelException as e:
            pass

        if self.__pd is not None:
            self.__pd.close()

    def __progress(self, now_v, max):
        now = time.time()

        if self.__pd is None:
            self.__pd_last_evt = now
            self.__pd = QtGui.QProgressDialog(
                "Rebuilding Connectivity....", "Cancel", 0, max, self.__window)
            self.__pd.show()

        elif now - self.__pd_last_evt > 0.05:
            self.__pd_last_evt = now
            QtGui.QApplication.instance().processEvents()

        if self.__pd.wasCanceled():
            raise RebuildConnectivityAction.CancelException()

        self.__pd.setValue(now_v)


class LayerViewSetupDialogAction(QtGui.QAction):

    def __init__(self, window):
        self.__window = window
        QtGui.QAction.__init__(
            self, "Edit Stackup/Imagery pairing", self.__window, triggered=self.__action)

    def __action(self):
        dlg = LayerViewSetupDialog(self.__window, self.__window.project)
        dlg.exec_()
