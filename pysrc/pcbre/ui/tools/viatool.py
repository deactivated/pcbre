from pcbre.qt_compat import QtCore, QtWidgets

from pcbre.matrix import Point2
from pcbre.model.artwork_geom import Via
from pcbre.ui.dialogs.settingsdialog import SettingsDialog
from pcbre.ui.widgets.unitedit import UnitLineEdit, UNIT_GROUP_MM
from pcbre.view.rendersettings import RENDER_OUTLINES


from .basetool import BaseTool, BaseToolController


class ViaSettingsDialog(SettingsDialog):
    def __init__(self, tpm):
        super().__init__()
        self.tpm = tpm

        self.radius_li = UnitLineEdit(UNIT_GROUP_MM)
        self.radius_li.setValue(self.tpm.radius)

        self.layout.addRow("Radius:", self.radius_li)

    @QtCore.Slot()
    def accept(self):
        self.tpm.radius = self.radius_li.getValue()
        QtWidgets.QDialog.accept(self)


class ViaToolOverlay:
    def __init__(self, ctrl):
        """
        :type ctrl: ViaToolController
        """
        self.view = ctrl.view
        self.tpm = ctrl.toolparammodel
        self.ctrl = ctrl

        self.render_b = ctrl.view.via_renderer.batch()

    def initializeGL(self, gls):
        """
        :type gls: GLShared
        :param gls:
        :return:
        """
        self.gls = gls

    def render(self, viewport):
        self.render_b.restart()

        if self.tpm.current_layer_pair is not None:
            self.render_b.deferred(
                Point2(self.ctrl.x, self.ctrl.y), self.tpm.radius, 0, RENDER_OUTLINES
            )

        self.render_b.prepare()
        self.render_b.render_outline(viewport.glMatrix)


class ViaToolController(BaseToolController):
    def __init__(self, view, project, toolparammodel):
        """

        :type view: pcbre.ui.boardviewwidget.BoardViewWidget
        """
        super().__init__()

        self.view = view
        self.project = project

        self.toolparammodel = toolparammodel
        self.toolparammodel.changed.connect(self.__modelchanged)

        self.x = 0
        self.y = 0
        self.show = False

        self.overlay = ViaToolOverlay(self)

    def showSettingsDialog(self):
        ViaSettingsDialog(self.toolparammodel).exec_()

    def __modelchanged(self):
        self.changed.emit()

    def mousePressEvent(self, evt):
        pt_screen = Point2(evt.pos())
        pt_world = Point2(self.view.viewState.tfV2W(pt_screen))

        # New object with dummy net
        if self.toolparammodel.current_layer_pair is not None:
            v = Via(
                pt_world,
                self.toolparammodel.current_layer_pair,
                self.toolparammodel.radius,
                None,
            )
            self.project.artwork.merge_artwork(v)

    def mouseReleaseEvent(self, evt):
        pass

    def mouseMoveEvent(self, evt):
        self.show = True
        self.x, self.y = self.view.viewState.tfV2W(Point2(evt.pos()))
        self.changed.emit()

    def mouseWheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            # TODO: Remove hack on step
            step = event.angleDelta().y() / 120.0

            self.toolparammodel.radius += step
            if self.toolparammodel.radius <= 0:
                self.toolparammodel.radius = 0.00001


class ViaToolModel(QtCore.QObject):
    changed = QtCore.Signal()

    def __init__(self, project):
        super().__init__()
        self.project = project

        self.__current_layer_pair = None
        self.__r = 1000

    @property
    def current_layer_pair(self):
        return self.__current_layer_pair

    @current_layer_pair.setter
    def current_layer_pair(self, value):
        old = self.__current_layer_pair
        self.__current_layer_pair = value

        if old != value:
            self.changed.emit()

    @property
    def radius(self):
        return self.__r

    @radius.setter
    def radius(self, value):
        old = self.__r
        self.__r = value

        if old != value:
            self.changed.emit()


class ViaTool(BaseTool):
    ICON_NAME = "via"
    NAME = "Via"
    SHORTCUT = "v"
    TOOLTIP = "Via (v)"

    def __init__(self, project):
        super(ViaTool, self).__init__(project)

        self.project = project
        self.model = ViaToolModel(project)

    def __changed_selected_viapair(self, vp):
        self.model.current_layer_pair = vp

    def __setupMenu(self):
        self.menu = QtWidgets.QMenu()
        self.menu.aboutToShow.connect(self.aboutShowMenu)
        self.toolButton.setMenu(self.menu)

    def aboutShowMenu(self):
        self.menu.clear()

        self.ag = QtWidgets.QActionGroup(self.menu)
        self.ag.setExclusive(True)

        for n, vp in enumerate(self.project.stackup.via_pairs):
            l1, l2 = vp.layers
            a1 = QtWidgets.QAction("%d-%d" % (l1.order, l2.order), self.menu)
            a1.setCheckable(True)
            a1.setChecked(vp is self.model.current_layer_pair)

            def closure(vp):
                def fn():
                    self.__changed_selected_viapair(vp)

                return fn

            a1.triggered.connect(closure(vp))

            self.menu.addAction(a1)
            self.ag.addAction(a1)

    def setupToolButtonExtra(self):
        self.__setupMenu()

    def getToolController(self, view):
        return ViaToolController(view, self.project, self.model)
