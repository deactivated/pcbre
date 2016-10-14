import math
from pcbre.matrix import project_point_line, line_intersect, line_distance_segment, Vec2
from pcbre.model.artwork_geom import Trace, Via, Polygon
from pcbre.model.const import IntersectionClass
from pcbre.model.pad import Pad
from shapely.geometry import Point as ShapelyPoint

__author__ = 'davidc'


def dist_pt_trace(pt, trace):
    return dist_pt_line_seg(pt, trace.p0, trace.p1) - trace.thickness / 2


def dist_pt_line_seg(pt, s_pt1, s_pt2):
    """
    :param pt:
    :param seg:
    :return:
    """

    pt, dist = project_point_line(pt, s_pt1, s_pt2, True, True)
    return dist


def dist_trace_trace(trace_1, trace_2):
    if trace_1.layer != trace_2.layer:
        return float("inf")
    d = line_distance_segment(trace_1.p0, trace_1.p1, trace_2.p0, trace_2.p1)
    return d - trace_1.thickness / 2 - trace_2.thickness / 2


def dist_via_trace(via, trace):
    if trace.layer not in via.viapair.all_layers:
        return float("inf")
    return dist_pt_line_seg(via.pt, trace.p0, trace.p1) - \
        trace.thickness / 2 - via.r


def dist_via_via(via_1, via_2):
    if not set(via_1.viapair.all_layers).intersection(
            via_2.viapair.all_layers):
        return float("inf")
    d = (via_1.pt - via_2.pt).mag()
    return d - via_1.r - via_2.r


def dist_pad_pad(p1, p2):
    """
    :type p1: pcbre.model.pad.Pad
    :type p2: pcbre.model.pad.Pad
    :param p1:
    :param p2:
    :return:
    """
    if not p1.is_through():
        if p1.layer != p2.layer:
            return float("inf")

    # Fast degenerate case
    if p1.w == p1.l and p2.w == p2.l:
        d = (p1.center - p2.center).mag()
        return d - p1.w / 2 - p2.w / 2

    else:
        t1 = p1.trace_repr
        t2 = p2.trace_repr
        return dist_trace_trace(t1, t2)


def dist_via_pad(v1, p1):
    d = (v1.pt - p1.center).mag()
    return d - p1.w / 2 - v1.r


def dist_trace_pad(trace, p1):
    # inf distance if on other layers
    if not p1.is_through():
        if p1.layer != trace.layer:
            return float("inf")

    # Degenerate case where pad is a circle
    if p1.w == p1.l:
        return dist_pt_line_seg(p1.center, trace.p0,
                                trace.p1) - trace.thickness / 2 - p1.w / 2
    else:
        ptr = p1.trace_repr
        return dist_trace_trace(ptr, trace)


def dist_polygon_polygon(p1, p2):
    if p1.layer != p2.layer:
        return float("inf")

    return p1.get_poly_repr().distance(p2.get_poly_repr())

# Trace is the same, has a layer and a poly repr
dist_polygon_trace = dist_polygon_polygon


def dist_polygon_via(p, v):
    if p.layer not in v.viapair.all_layers:
        return float("inf")

    return p.get_poly_repr().distance(v.get_poly_repr())


def dist_polygon_pad(poly, pad):
    if not pad.is_through():
        if pad.layer != poly.layer:
            return float("inf")

    return poly.get_poly_repr().distance(pad.get_poly_repr())


def dist_virtual_line_XX(airwire, trace):
    if airwire.p0_layer == trace.layer and point_inside(trace, airwire.p0):
        return 0
    elif airwire.p1_layer == trace.layer and point_inside(trace, airwire.p1):
        return 0
    return float("inf")

dist_virtual_line_trace = dist_virtual_line_XX
dist_virtual_line_polygon = dist_virtual_line_XX


def dist_virtual_line_via(airwire, via):
    layers = via.viapair.all_layers
    if airwire.p0_layer in layers and point_inside(via, airwire.p0):
        return 0
    elif airwire.p1_layer in layers and point_inside(via, airwire.p1):
        return 0

    return float("inf")


def dist_virtual_line_pad(airwire, pad):
    if pad.is_through():
        if point_inside(pad, airwire.p0) or point_inside(pad, airwire.p1):
            return 0
        else:
            return float("inf")

    return dist_virtual_line_XX(airwire, pad)


def dist_virtual_line_virtual_line(_, __):
    return float("inf")


def swapped(fn):
    def _(a, b):
        return fn(b, a)
    return _


def pt_inside_pad(pad, pt):
    """

    :param pt:
    :return:
    """
    point_padspace = pad.world_to_pad(pt)
    delta = Vec2(point_padspace)

    if pad.w == pad.l:
        return delta.mag() < pad.l / 2
    else:
        return pt_inside_trace(pad.trace_repr, pt)


def pt_inside_trace(trace, pt):
    return dist_pt_trace(pt, trace) < 0


def pt_inside_via(via, pt):
    return (pt - via.pt).mag2() <= via.r**2


def pt_inside_polygon(poly, pt):
    pt = ShapelyPoint(pt)
    return poly.get_poly_repr().intersects(pt)


def pt_inside_virtual_line(airwire, pt):
    return dist_pt_line_seg(pt, airwire.p0, airwire.p1) <= 0


########### Build comparison functions for geom types #################
_geom_types = [i for i in IntersectionClass if i is not IntersectionClass.NONE]
_geom_ops = {}


def _dist_name(a, b):
    fn_name = "dist_%s_%s" % (a.name.lower(), b.name.lower())
    return fn_name

for n, a in enumerate(_geom_types):
    for b in _geom_types[n:]:
        fwd_name = _dist_name(a, b)
        rev_name = _dist_name(b, a)
        if fwd_name in globals():
            fn = globals()[fwd_name]
            _geom_ops[(a, b)] = fn
            _geom_ops[(b, a)] = swapped(fn)
        elif rev_name in globals():
            fn = globals()[rev_name]
            _geom_ops[(a, b)] = swapped(fn)
            _geom_ops[(b, a)] = fn
        else:
            raise NotImplementedError("Geom distance op for %s %s" % (a, b))


def distance(a, b):
    return _geom_ops[a.ISC, b.ISC](a, b)


def intersect(a, b):
    return distance(a, b) <= 0

_pt_inside_ops = {}
for i in _geom_types:
    _pt_inside_ops[i] = globals()["pt_inside_%s" % i.name.lower()]


def point_inside(geom, pt):
    if not geom.bbox.point_test(pt):
        return False

    return _pt_inside_ops[geom.ISC](geom, pt)


def can_self_intersect(geom):
    return geom.ISC not in [IntersectionClass.NONE,
                            IntersectionClass.VIRTUAL_LINE]


# layer_for finds a layer (or None) for the geometry queried.
def _layer_for_XX(geom):
    return geom.layer

_layer_for_polygon = _layer_for_trace = _layer_for_pad = _layer_for_XX


def _layer_for_via(via):
    return via.viapair.layers[0]


def _layer_for_virtual_line(vl):
    return None

_layer_for_ops = {}
for i in _geom_types:
    _layer_for_ops[i.value] = globals()["_layer_for_%s" % i.name.lower()]


def layer_for(geom):
    if geom:
        return _layer_for_ops[geom.ISC.value](geom)
