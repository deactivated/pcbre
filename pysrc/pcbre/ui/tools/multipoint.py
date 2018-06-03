import math
from copy import copy, deepcopy
from enum import Enum

from pcbre.qt_compat import QtCore, QtGui
from pcbre.matrix import Point2, Vec2, clip_point_to_rect, Rect
from pcbre.view.rendersettings import RENDER_HINT_ONCE

__author__ = "davidc"


class RenderIcon:
    POINT = 0
    POINT_ON_LINE = 1  # implies has .get_vector()
    LINE = 2  # implies has .get_vector()


class EditablePoint:
    def __init__(self, defv=None, icon=RenderIcon.POINT, enabled=True):
        self.is_set = False
        self.pt = defv
        self.icon = icon

        if not callable(enabled):
            self.__enabled = lambda: enabled
        else:
            self.__enabled = enabled

    @property
    def enabled(self):
        return self.__enabled()

    def save(self):
        return deepcopy((self.is_set, self.pt))

    def restore(self, v):
        self.is_set, self.pt = v

    def set(self, pt):
        self.pt = pt
        self.is_set = True

    def unset(self):
        self.pt = None
        self.is_set = False

    def get(self):
        return self.pt


class OffsetDefaultPoint(EditablePoint):
    def __init__(self, pt, default_offset, icon=RenderIcon.POINT_ON_LINE, enabled=True):
        super(OffsetDefaultPoint, self).__init__(enabled=enabled)
        self.reference = pt
        self.offset = default_offset
        self.icon = icon

    def get_vector(self):
        return self.get() - self.reference.get()

    def get(self):
        if self.is_set:
            return self.pt

        if callable(self.offset):
            offset = self.offset()
        else:
            offset = self.offset

        return self.reference.get() + offset


class DONE_REASON(Enum):
    NOT_DONE = 0
    ACCEPT = 1
    REJECT = 2


def _default_color_fn(flow, pt):
    if pt is flow.current_point:
        return (1, 1, 1)
    elif pt.is_set:
        return (1, 0, 0)
    else:
        return (0.5, 0, 0)


class MultipointEditRenderer:
    def __init__(
        self, flow, view, color_fn=_default_color_fn, show_fn=lambda pt: pt.enabled
    ):
        """
        :type view: pcbre.ui.boardviewwidget.BoardViewWidget
        :param flow:
        :param view:
        :param color_fn:
        :return:
        """
        self.view = view
        self.flow = flow
        self.color_fn = color_fn
        self.show_fn = show_fn

    def render(self):
        N = 5
        corners = list(map(Point2, [(-N, -N), (N, -N), (N, N), (-N, N)]))

        for p in self.flow.points:
            if not self.show_fn(p) or not p.get():
                continue

            color = self.color_fn(self.flow, p)
            p_view = self.view.viewState.tfW2V(p.get())
            # p_view = p.get()

            # Draw crappy cross for now

            for pa, pb in zip(corners, corners[1:] + corners[:1]):
                self.view.hairline_renderer.deferred(
                    p_view + pa, p_view + pb, color, "OVERLAY_VS", RENDER_HINT_ONCE
                )


class MultipointEditFlow:
    def __init__(self, view, points, can_shortcut=False):
        self.view = view
        self.__points = points
        self.__current_point_index = 0
        self.__point_active = False
        self.is_initial_active = True
        self.is_first_point = True
        self.can_shortcut = can_shortcut

        self.__done = DONE_REASON.NOT_DONE

        self.__grab_delta = Vec2(0, 0)

    @property
    def current_point(self):
        return self.__points[self.__current_point_index]

    @property
    def points(self):
        return self.__points

    def select_point(self, pt):
        self.__current_point_index = self.__points.index(pt)

    def make_active(self, world_to_point=False):
        self.__saved_point = self.current_point.save()

        if not world_to_point:
            pt = self.view.viewState.tfW2V(self.current_point.get())

            bounds = Rect.fromPoints(
                Point2(0, 0), Point2(self.view.width(), self.view.height())
            )
            pt_clipped = clip_point_to_rect(pt, bounds)

            screen_pt = self.view.mapToGlobal(QtCore.QPoint(*pt_clipped.intTuple()))

            QtGui.QCursor.setPos(screen_pt)
        else:
            rect_pt = Point2(self.view.mapFromGlobal(QtGui.QCursor.pos()))
            world_pt = self.view.viewState.tfV2W(rect_pt)
            self.current_point.set(world_pt)

        self.__point_active = True

    def abort_entry(self):
        self.is_initial_active = False
        if self.__point_active:
            self.__point_active = False
            self.current_point.restore(self.__saved_point)
        else:
            self.__done = DONE_REASON.REJECT

    def commit_entry(self, shift_pressed):
        if self.is_first_point and not shift_pressed:
            self.__done = DONE_REASON.ACCEPT
            self.__point_active = False
        self.is_first_point = False

        if self.__point_active:
            self.__point_active = False
            self.next_point()
            if not self.current_point.is_set:
                if self.is_initial_active:
                    self.__grab_delta = Vec2(0, 0)
                    self.make_active()
            else:
                self.is_initial_active = False

    def __step_point(self, step):
        for i in range(len(self.points)):
            self.__current_point_index = (self.__current_point_index + step) % len(
                self.__points
            )
            if self.current_point.enabled:
                break
        else:
            assert False, "Could not find enabled point"

    def next_point(self):
        self.__step_point(1)

    def prev_point(self):
        self.__step_point(-1)

    def mouseMoveEvent(self, evt):
        if self.__point_active:
            point_pos = self.view.viewState.tfV2W(Point2(evt.pos()) + self.__grab_delta)
            self.current_point.set(point_pos)
            self.updated(self.current_point)

    def mousePressEvent(self, evt):
        if evt.button() == QtCore.Qt.RightButton:
            if hasattr(self, "theta"):
                angle = math.pi / 2
                if evt.modifiers() & QtCore.Qt.ShiftModifier:
                    angle = -angle

                self.theta += angle

        if evt.button() == QtCore.Qt.LeftButton:
            if self.__point_active:
                self.commit_entry(evt.modifiers() & QtCore.Qt.ShiftModifier)

    def mouseReleaseEvent(self, evt):
        pass

    def do_jog(self, vec):
        p = self.view.viewState.tfW2V(self.current_point.get())
        self.current_point.set(self.view.viewState.tfV2W(p + vec))
        self.updated()

    def keyReleaseEvent(self, evt):
        if evt.key() in [
            QtCore.Qt.Key_Q,
            QtCore.Qt.Key_W,
            QtCore.Qt.Key_E,
            QtCore.Qt.Key_R,
            QtCore.Qt.Key_Left,
            QtCore.Qt.Key_Right,
            QtCore.Qt.Key_Up,
            QtCore.Qt.Key_Down,
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Escape,
        ]:
            return True

        return False

    def keyPressEvent(self, evt):
        keycode = evt.key()

        jog_keys = {
            QtCore.Qt.Key_Left: Vec2(-1, 0),
            QtCore.Qt.Key_Right: Vec2(1, 0),
            QtCore.Qt.Key_Up: Vec2(0, 1),
            QtCore.Qt.Key_Down: Vec2(0, -1),
        }

        if keycode == QtCore.Qt.Key_Escape:
            self.abort_entry()
        elif keycode in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            if self.__point_active:
                self.commit_entry()
            else:
                self.__done = DONE_REASON.ACCEPT

        elif keycode in jog_keys:
            self.do_jog(jog_keys[keycode])
        elif keycode == QtCore.Qt.Key_Q:
            self.prev_point()
        elif keycode == QtCore.Qt.Key_W:
            self.next_point()
        elif keycode == QtCore.Qt.Key_E:
            self.make_active()
        elif keycode == QtCore.Qt.Key_R:
            self.next_option()
        else:
            return False

        return True

    def updated(self, ep):
        pass

    def next_option(self):
        pass

    @property
    def done(self):
        return self.__done
