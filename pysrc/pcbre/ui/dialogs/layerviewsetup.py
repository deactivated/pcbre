import random
import numpy

from pcbre.qt_compat import QtCore, QtGui, QtWidgets

import pcbre.model.project
import pcbre.model.stackup

FIRST_VIEW_COL = 1


class LayerViewSetupDialog(QtWidgets.QDialog):

    def __init__(self, parent, data_list):
        QtWidgets.QDialog.__init__(self, parent)

        self.resize(470, 350)
        self.setWindowTitle("Layer imagery")

        self.table_model = MyTableModel(self, data_list)

        self.table_view = QtWidgets.QTableView()

        self.table_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)

        self.table_view.setModel(self.table_model)
        # set font
        font = QtGui.QFont("Courier New", 10)
        self.table_view.setFont(font)
        self.table_view.resizeColumnsToContents()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.table_view)
        l2 = QtWidgets.QVBoxLayout()

        self.cancelButton = QtWidgets.QPushButton("cancel")
        self.cancelButton.clicked.connect(self.reject)
        self.okButton = QtWidgets.QPushButton("apply")
        self.okButton.setDefault(True)
        self.okButton.clicked.connect(self.accept)

        l2.addStretch()
        l2.addWidget(self.cancelButton)
        l2.addWidget(self.okButton)

        #l2.addRow("test", None)
        layout.addLayout(l2)

        self.setLayout(layout)

        self.table_view.selectRow(0)

    def accept(self):
        self.table_model.update()
        return QtWidgets.QDialog.accept(self)


class EditableLayer(object):

    def __init__(self, mdl, ref, name, ils):
        self.name = name
        self.mdl = mdl
        self.ref = ref
        self.view_set = set(ils)


class MyTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent, project, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.p = project
        self._layers = [
            EditableLayer(self, pl, pl.name, pl.imagelayers)
            for pl in project.stackup.layers]

        self._views = project.imagery.imagelayers

    def update(self):
        for i in self._layers:
            i.ref.imagelayers = list(i.view_set)

    def rowCount(self, parent):
        return len(self._layers)

    def columnCount(self, parent):
        return len(self._views)

    def data(self, index, role):
        if not index.isValid():
            return None

        col = index.column()
        row = index.row()

        if role == QtCore.Qt.DisplayRole:

            return None

        elif role == QtCore.Qt.CheckStateRole:
            layer = self._layers[row]
            view = self._views[col]
            return QtCore.Qt.Checked if view in layer.view_set else QtCore.Qt.Unchecked

        return None

    def setData(self, index, data, role):
        if not index.isValid():
            return None

        col = index.column()
        row = index.row()

        layer = self._layers[row]
        view = self._views[col]
        if data:
            layer.view_set.add(view)
        else:
            layer.view_set.remove(view)

        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        if not index.isValid():
            return 0

        col = index.column()
        row = index.row()

        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable
        return flags

    def headerData(self, index, orientation, role):
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._layers[index].name

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            # TODO HACK
            import os.path
            return os.path.basename(self._views[index].name)
        return None

# Test harness
if __name__ == "__main__":
    app = QtCore.QApplication([])
    import os.path
    PATH = '/tmp/test.pcbre'
    if os.path.exists(PATH):
        project = pcbre.model.project.Project.open(PATH)
    else:
        project = pcbre.model.project.Project.create(PATH)

    win = LayerViewSetupDialog(project)
    win.show()
    app.exec_()
