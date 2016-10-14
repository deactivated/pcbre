from pcbre.qt_compat import QtWidgets
from pcbre.ui.menu.imageselectionmenu import ImageSelectionMenu


__author__ = 'davidc'


class PCBMenu(QtWidgets.QMenu):

    def __init__(self, pw):
        QtWidgets.QMenu.__init__(self, "&PCB", pw)
        self.addAction(pw.actions.pcb_stackup_setup_dialog)
        self.addAction(pw.actions.pcb_layer_view_setup_dialog)
        self.addMenu(ImageSelectionMenu(pw))
        self.addSeparator()
        self.addAction(pw.actions.pcb_rebuild_connectivity)
