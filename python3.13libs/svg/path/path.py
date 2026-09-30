from math import sqrt, cos, sin, acos, degrees, radians, log, pi
from bisect import bisect
from abc import ABC, abstractmethod
import math

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence

# This file contains classes for the different types of SVG path segments as
# well as a Path object that contains a sequence of path segments.

MIN_DEPTH = 5
ERROR = 1e-12


def _find_solutions_for_bezier(c2, c1, c0):
    """Find solutions of c2 * t^2 + c1 * t + c0 = 0 where t in [0, 1]"""
    soln = []
    if c2 == 0:
        if c1 != 0:
            soln.append(-c0 / c1)
    else:
        det = c1**2 - 4 * c2 * c0
        if det >= 0:
            soln.append((-c1 + math.pow(det, 0.5)) / 2.0 / c2)
            soln.append((-c1 - math.pow(det, 0.5)) / 2.0 / c2)
    return [s for s in soln if 0.0 <= s and s <= 1.0]


def _find_solutions_for_arc(a, b, c, d):
    """Find solution for a sin(x) + b cos(x) = 0 where x = c + d * t and t in [0, 1]"""
    if a == 0:
        # when n \in Z
        # pi / 2 + pi * n = c + d * t
        # --> n = d / pi * t - (1/2 - c/pi)
        # --> t = (pi / 2 - c + pi * n) / d
        n_ranges = [-0.5 + c / math.pi, d / math.pi - 0.5 + c / math.pi]
        n_range_start = math.floor(min(n_ranges))
        n_range_end = math.ceil(max(n_ranges))
        t_list = [
            (math.pi / 2 - c + math.pi * n) / d
            for n in range(n_range_start, n_range_end + 1)
        ]
    elif b == 0:
        # when n \in Z
        # pi * n = c + d * t
        # --> n = d / pi * t + c / pi
        # --> t = (- c + pi * n) / d
        n_ranges = [c / math.pi, d / math.pi + c / math.pi]
        n_range_start = math.floor(min(n_ranges))
        n_range_end = math.ceil(max(n_ranges))
        t_list = [(-c + math.pi * n) / d for n in range(n_range_start, n_range_end + 1)]
    else:
        # when n \in Z
        # arct = tan^-1 (- b / a)  and
        # arct + pi * n = c + d * t
        # --> n = (c - arct + d * t) / pi
        # --> t = (arct - c + pi * n) / d
        arct = math.atan(-b / a)
        n_ranges = [(c - arct) / math.pi, d / math.pi + (c - arct) / math.pi]
        n_range_start = math.floor(min(n_ranges))
        n_range_end = math.ceil(max(n_ranges))
        t_list = [
            (arct - c + math.pi * n) / d for n in range(n_range_start, n_range_end + 1)
        ]

    t_list = [t for t in t_list if 0.0 <= t and t <= 1.0]
    return t_list


def segment_length(curve, start, end, start_point, end_point, error, min_depth, depth):
    """Recursively approximates the length by straight lines"""
    mid = (start + end) / 2
    mid_point = curve.point(mid)
    length = abs(end_point - start_point)
    first_half = abs(mid_point - start_point)
    second_half = abs(end_point - mid_point)

    length2 = first_half + second_half
    if (length2 - length > error) or (depth < min_depth):
        # Calculate the length of each segment:
        depth += 1
        return segment_length(
            curve, start, mid, start_point, mid_point, error, min_depth, depth
        ) + segment_length(
            curve, mid, end, mid_point, end_point, error, min_depth, depth
        )
    # This is accurate enough.
    return length2


class PathSegment(ABC):
    @abstractmethod
    def point(self, pos):
        """Returns the coordinate point (as a complex number) of a point on the path,
        as expressed as a floating point number between 0 (start) and 1 (end).
        """

    @abstractmethod
    def tangent(self, pos):
        """Returns a vector (as a complex number) representing the tangent of a point
        on the path as expressed as a floating point number between 0 (start) and 1 (end).
        """

    @abstractmethod
    def length(self, error=ERROR, min_depth=MIN_DEPTH):
        """Returns the length of a path.

        The CubicBezier and Arc lengths are non-exact and iterative and you can select to
        either do the calculations until a maximum error has been achieved, or a minimum
        number of iterations.
        """

    @abstractmethod
    def boundingbox(self):
        """Returns the bounding box of a path in the format of [left, top, right, bottom]"""


class NonLinear(PathSegment):
    """A line that is not straight

    The base of Arc, QuadraticBezier and CubicBezier
    """


class Linear(PathSegment):
    """A straight line

    The base for Line() and Close().
    """

    def __init__(self, start, end, relative=False):
        self.start = start
        self.end = end
        self.relative = relative

    def __ne__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return not self == other

    def point(self, pos):
        distance = self.end - self.start
        return self.start + distance * pos

    def tangent(self, pos):
        return self.end - self.start

    def length(self, error=None, min_depth=None):
        distance = self.end - self.start
        return sqrt(distance.real**2 + distance.imag**2)


class Line(Linear):
    def __init__(self, start, end, relative=False, vertical=False, horizontal=False):
        self.start = start
        self.end = end
        self.relative = relative
        self.vertical = vertical
        self.horizontal = horizontal

    def __repr__(self):
        return f"Line(start={self.start}, end={self.end})"

    def __eq__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def _d(self, previous):
        x = self.end.real
        y = self.end.imag
        if self.relative:
            x -= previous.end.real
            y -= previous.end.imag

        if self.horizontal and self.is_horizontal_from(previous):
            cmd = "h" if self.relative else "H"
            return f"{cmd} {x:G}"

        if self.vertical and self.is_vertical_from(previous):
            cmd = "v" if self.relative else "V"
            return f"{cmd} {y:G}"

        cmd = "l" if self.relative else "L"
        return f"{cmd} {x:G},{y:G}"

    def is_vertical_from(self, previous):
        return self.start == previous.end and self.start.real == self.end.real

    def is_horizontal_from(self, previous):
        return self.start == previous.end and self.start.imag == self.end.imag

    def boundingbox(self):
        x_min = min(self.start.real, self.end.real)
        x_max = max(self.start.real, self.end.real)
        y_min = min(self.start.imag, self.end.imag)
        y_max = max(self.start.imag, self.end.imag)
        return [x_min, y_min, x_max, y_max]


class CubicBezier(NonLinear):
    def __init__(self, start, control1, control2, end, relative=False, smooth=False):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end
        self.relative = relative
        self.smooth = smooth

    def __repr__(self):
        return (
            f"CubicBezier(start={self.start}, control1={self.control1}, "
            f"control2={self.control2}, end={self.end}, smooth={self.smooth})"
        )

    def __eq__(self, other):
        if not isinstance(other, CubicBezier):
            return NotImplemented
        return (
            self.start == other.start
            and self.end == other.end
            and self.control1 == other.control1
            and self.control2 == other.control2
        )

    def __ne__(self, other):
        if not isinstance(other, CubicBezier):
            return NotImplemented
        return not self == other

    def _d(self, previous):
        c1 = self.control1
        c2 = self.control2
        end = self.end

        if self.relative and previous:
            c1 -= previous.end
            c2 -= previous.end
            end -= previous.end

        if self.smooth and self.is_smooth_from(previous):
            cmd = "s" if self.relative else "S"
            return f"{cmd} {c2.real:G},{c2.imag:G} {end.real:G},{end.imag:G}"

        cmd = "c" if self.relative else "C"
        return f"{cmd} {c1.real:G},{c1.imag:G} {c2.real:G},{c2.imag:G} {end.real:G},{end.imag:G}"

    def is_smooth_from(self, previous):
        """Checks if this segment would be a smooth segment following the previous"""
        if isinstance(previous, CubicBezier):
            return self.start == previous.end and (self.control1 - self.start) == (
                previous.end - previous.control2
            )
        else:
            return self.control1 == self.start

    def set_smooth_from(self, previous):
        assert isinstance(previous, CubicBezier)
        self.start = previous.end
        self.control1 = previous.end - previous.control2 + self.start
        self.smooth = True

    def point(self, pos):
        """Calculate the x,y position at a certain position of the path"""
        return (
            ((1 - pos) ** 3 * self.start)
            + (3 * (1 - pos) ** 2 * pos * self.control1)
            + (3 * (1 - pos) * pos**2 * self.control2)
            + (pos**3 * self.end)
        )

    def tangent(self, pos):
        return (
            -3 * (1 - pos) ** 2 * self.start
            + 3 * (1 - pos) ** 2 * self.control1
            - 6 * pos * (1 - pos) * self.control1
            - 3 * pos**2 * self.control2
            + 6 * pos * (1 - pos) * self.control2
            + 3 * pos**2 * self.end
        )

    def length(self, error=ERROR, min_depth=MIN_DEPTH):
        """Calculate the length of the path up to a certain position"""
        start_point = self.point(0)
        end_point = self.point(1)
        return segment_length(self, 0, 1, start_point, end_point, error, min_depth, 0)

    def boundingbox(self):
        """Calculate the bounding box of a cubic Bezier curve.

        A cubic Bezier curve and its derivative are given as follows.

        P(t)  = (1-t)^3 P0 + 3 t (1-t)^2 P1 + 3 t^2 (1-t) P2 + t^3 P_3
        P'(t) = 3(1-t)^2 (P1-P0) + 6(1-t)t (P2-P1) + 3 t^2 (P3 - P2)
        """
        g0 = self.control1 - self.start
        g1 = self.control2 - self.control1
        g2 = self.end - self.control2

        c0 = 3 * g0
        c1 = -6 * g0 + 6 * g1
        c2 = 3 * g0 - 6 * g1 + 3 * g2

        x_c0, x_c1, x_c2 = [c.real for c in [c0, c1, c2]]
        y_c0, y_c1, y_c2 = [c.imag for c in [c0, c1, c2]]

        x_cand = [0, 1] + _find_solutions_for_bezier(x_c2, x_c1, x_c0)
        y_cand = [0, 1] + _find_solutions_for_bezier(y_c2, y_c1, y_c0)

        x_coords = []
        y_coords = []
        for t in x_cand:
            p = self.point(t)
            x_coords.append(p.real)
        for t in y_cand:
            p = self.point(t)
            y_coords.append(p.imag)

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        return [x_min, y_min, x_max, y_max]


class QuadraticBezier(NonLinear):
    def __init__(self, start, control, end, relative=False, smooth=False):
        self.start = start
        self.end = end
        self.control = control
        self.relative = relative
        self.smooth = smooth

    def __repr__(self):
        return (
            f"QuadraticBezier(start={self.start}, control={self.control}, "
            f"end={self.end}, smooth={self.smooth})"
        )

    def __eq__(self, other):
        if not isinstance(other, QuadraticBezier):
            return NotImplemented
        return (
            self.start == other.start
            and self.end == other.end
            and self.control == other.control
        )

    def __ne__(self, other):
        if not isinstance(other, QuadraticBezier):
            return NotImplemented
        return not self == other

    def _d(self, previous):
        control = self.control
        end = self.end
        if self.relative and previous:
            control -= previous.end
            end -= previous.end

        if self.smooth and self.is_smooth_from(previous):
            cmd = "t" if self.relative else "T"
            return f"{cmd} {end.real:G},{end.imag:G}"

        cmd = "q" if self.relative else "Q"
        return f"{cmd} {control.real:G},{control.imag:G} {end.real:G},{end.imag:G}"

    def is_smooth_from(self, previous):
        """Checks if this segment would be a smooth segment following the previous"""
        if isinstance(previous, QuadraticBezier):
            return self.start == previous.end and (self.control - self.start) == (
                previous.end - previous.control
            )
        else:
            return self.control == self.start

    def set_smooth_from(self, previous):
        assert isinstance(previous, QuadraticBezier)
        self.start = previous.end
        self.control = previous.end - previous.control + self.start
        self.smooth = True

    def point(self, pos):
        return (
            (1 - pos) ** 2 * self.start
            + 2 * (1 - pos) * pos * self.control
            + pos**2 * self.end
        )

    def tangent(self, pos):
        return (
            self.start * (2 * pos - 2)
            + (2 * self.end - 4 * self.control) * pos
            + 2 * self.control
        )

    def length(self, error=None, min_depth=None):
        a = self.start - 2 * self.control + self.end
        b = 2 * (self.control - self.start)

        try:
            # For an explanation of this case, see
            # http://www.malczak.info/blog/quadratic-bezier-curve-length/
            A = 4 * (a.real**2 + a.imag**2)
            B = 4 * (a.real * b.real + a.imag * b.imag)
            C = b.real**2 + b.imag**2

            Sabc = 2 * sqrt(A + B + C)
            A2 = sqrt(A)
            A32 = 2 * A * A2
            C2 = 2 * sqrt(C)
            BA = B / A2

            s = (
                A32 * Sabc
                + A2 * B * (Sabc - C2)
                + (4 * C * A - B**2) * log((2 * A2 + BA + Sabc) / (BA + C2))
            ) / (4 * A32)
        except (ZeroDivisionError, ValueError):
            if abs(a) < 1e-10:
                s = abs(b)
            else:
                k = abs(b) / abs(a)
                if k >= 2:
                    s = abs(b) - abs(a)
                else:
                    s = abs(a) * (k**2 / 2 - k + 1)
        return s

    def boundingbox(self):
        """Calculate the bounding box of a quadratic Bezier curve.

        A quadratic Bezier curve and its derivative are given as follows.

        P(t)  = (1-t)^2 P0 + 2 t (1-t)^2 P1 + t^2 P2
        P'(t) = 2(1-t) (P1-P0) + 2t (P2-P1)
        """
        g0 = self.control - self.start
        g1 = self.end - self.control

        c0 = 2 * g0
        c1 = -2 * g0 + 2 * g1

        x_c0, x_c1 = [c.real for c in [c0, c1]]
        y_c0, y_c1 = [c.imag for c in [c0, c1]]

        x_cand = [0, 1] + _find_solutions_for_bezier(0, x_c1, x_c0)
        y_cand = [0, 1] + _find_solutions_for_bezier(0, y_c1, y_c0)

        x_coords = []
        y_coords = []
        for t in x_cand:
            p = self.point(t)
            x_coords.append(p.real)
        for t in y_cand:
            p = self.point(t)
            y_coords.append(p.imag)

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        return [x_min, y_min, x_max, y_max]


class Arc(NonLinear):
    def __init__(self, start, radius, rotation, arc, sweep, end, relative=False):
        """radius is complex, rotation is in degrees,
        large and sweep are 1 or 0 (True/False also work)"""

        self.start = start
        self.radius = radius
        self.rotation = rotation
        self.arc = bool(arc)
        self.sweep = bool(sweep)
        self.end = end
        self.relative = relative

        self._parameterize()

    def __repr__(self):
        return (
            f"Arc(start={self.start}, radius={self.radius}, rotation={self.rotation}, "
            f"arc={self.arc}, sweep={self.sweep}, end={self.end})"
        )

    def __eq__(self, other):
        if not isinstance(other, Arc):
            return NotImplemented
        return (
            self.start == other.start
            and self.end == other.end
            and self.radius == other.radius
            and self.rotation == other.rotation
            and self.arc == other.arc
            and self.sweep == other.sweep
        )

    def __ne__(self, other):
        if not isinstance(other, Arc):
            return NotImplemented
        return not self == other

    def _d(self, previous):
        end = self.end
        cmd = "a" if self.relative else "A"
        if self.relative:
            end -= previous.end

        return (
            f"{cmd} {self.radius.real:G},{self.radius.imag:G} {self.rotation:G} "
            f"{int(self.arc):d},{int(self.sweep):d} {end.real:G},{end.imag:G}"
        )

    def _parameterize(self):
        # Conversion from endpoint to center parameterization
        # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        if self.start == self.end:
            # This is equivalent of omitting the segment, so do nothing
            return

        if self.radius.real == 0 or self.radius.imag == 0:
            # This should be treated as a straight line
            return

        cosr = cos(radians(self.rotation))
        sinr = sin(radians(self.rotation))
        dx = (self.start.real - self.end.real) / 2
        dy = (self.start.imag - self.end.imag) / 2
        x1prim = cosr * dx + sinr * dy
        x1prim_sq = x1prim * x1prim
        y1prim = -sinr * dx + cosr * dy
        y1prim_sq = y1prim * y1prim

        rx = self.radius.real
        rx_sq = rx * rx
        ry = self.radius.imag
        ry_sq = ry * ry

        # Correct out of range radii
        radius_scale = (x1prim_sq / rx_sq) + (y1prim_sq / ry_sq)
        if radius_scale > 1:
            radius_scale = sqrt(radius_scale)
            rx *= radius_scale
            ry *= radius_scale
            rx_sq = rx * rx
            ry_sq = ry * ry
            self.radius_scale = radius_scale
        else:
            # SVG spec only scales UP
            self.radius_scale = 1

        t1 = rx_sq * y1prim_sq
        t2 = ry_sq * x1prim_sq
        c = sqrt(abs((rx_sq * ry_sq - t1 - t2) / (t1 + t2)))

        if self.arc == self.sweep:
            c = -c
        cxprim = c * rx * y1prim / ry
        cyprim = -c * ry * x1prim / rx

        self.center = complex(
            (cosr * cxprim - sinr * cyprim) + ((self.start.real + self.end.real) / 2),
            (sinr * cxprim + cosr * cyprim) + ((self.start.imag + self.end.imag) / 2),
        )

        ux = (x1prim - cxprim) / rx
        uy = (y1prim - cyprim) / ry
        vx = (-x1prim - cxprim) / rx
        vy = (-y1prim - cyprim) / ry
        n = sqrt(ux * ux + uy * uy)
        p = ux
        theta = degrees(acos(p / n))
        if uy < 0:
            theta = -theta
        self.theta = theta % 360

        n = sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
        p = ux * vx + uy * vy
        d = p / n
        # In certain cases the above calculation can through inaccuracies
        # become just slightly out of range, f ex -1.0000000000000002.
        if d > 1.0:
            d = 1.0
        elif d < -1.0:
            d = -1.0
        delta = degrees(acos(d))
        if (ux * vy - uy * vx) < 0:
            delta = -delta
        self.delta = delta % 360
        if not self.sweep:
            self.delta -= 360

    def point(self, pos):
        if self.start == self.end:
            # This is equivalent of omitting the segment
            return self.start

        if self.radius.real == 0 or self.radius.imag == 0:
            # This should be treated as a straight line
            distance = self.end - self.start
            return self.start + distance * pos

        angle = radians(self.theta + (self.delta * pos))
        cosr = cos(radians(self.rotation))
        sinr = sin(radians(self.rotation))
        radius = self.radius * self.radius_scale

        x = (
            cosr * cos(angle) * radius.real
            - sinr * sin(angle) * radius.imag
            + self.center.real
        )
        y = (
            sinr * cos(angle) * radius.real
            + cosr * sin(angle) * radius.imag
            + self.center.imag
        )
        return complex(x, y)

    def tangent(self, pos):
        angle = radians(self.theta + (self.delta * pos))
        cosr = cos(radians(self.rotation))
        sinr = sin(radians(self.rotation))
        radius = self.radius * self.radius_scale

        x = cosr * cos(angle) * radius.real - sinr * sin(angle) * radius.imag
        y = sinr * cos(angle) * radius.real + cosr * sin(angle) * radius.imag
        return complex(x, y) * complex(0, 1)

    def length(self, error=ERROR, min_depth=MIN_DEPTH):
        """The length of an elliptical arc segment requires numerical
        integration, and in that case it's simpler to just do a geometric
        approximation, as for cubic bezier curves.
        """
        if self.start == self.end:
            # This is equivalent of omitting the segment
            return 0

        if self.radius.real == 0 or self.radius.imag == 0:
            # This should be treated as a straight line
            distance = self.end - self.start
            return sqrt(distance.real**2 + distance.imag**2)

        if self.radius.real == self.radius.imag:
            # It's a circle, which simplifies this a LOT.
            radius = self.radius.real * self.radius_scale
            return abs(radius * self.delta * pi / 180)

        start_point = self.point(0)
        end_point = self.point(1)
        return segment_length(self, 0, 1, start_point, end_point, error, min_depth, 0)

    def boundingbox(self):
        """Calculate the bounding box of an arc

        To calculate the extremums of the arc coordinates, we solve

        x'(angle) = - cosr * radius.real * sin(angle)
                    - sinr * radius.imag * cos(angle) = 0

        y'(angle) = - sinr * radius.real * sin(angle)
                    + cosr * radius.imag * cos(angle) = 0

        and
            angle = radians(self.theta + (self.delta * pos))
        where pos ranges from 0 to 1
        """

        # angle = radians(self.theta + (self.delta * pos))
        cosr = cos(radians(self.rotation))
        sinr = sin(radians(self.rotation))
        radius = self.radius * self.radius_scale

        x_a = -cosr * radius.real
        x_b = -sinr * radius.imag
        x_c = radians(self.theta)
        x_d = radians(self.delta)

        y_a = -sinr * radius.real
        y_b = +cosr * radius.imag
        y_c = radians(self.theta)
        y_d = radians(self.delta)

        x_pos = [0, 1.0] + _find_solutions_for_arc(x_a, x_b, x_c, x_d)
        y_pos = [0, 1.0] + _find_solutions_for_arc(y_a, y_b, y_c, y_d)

        x_coords = []
        y_coords = []
        for pos in x_pos:
            p = self.point(pos)
            x_coords.append(p.real)
        for pos in y_pos:
            p = self.point(pos)
            y_coords.append(p.imag)

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        return [x_min, y_min, x_max, y_max]


class Move:
    """Represents move commands. Does nothing, but is there to handle
    paths that consist of only move commands, which is valid, but pointless.
    """

    def __init__(self, to, relative=False):
        self.start = self.end = to
        self.relative = relative

    def __repr__(self):
        return "Move(to=%s)" % self.start

    def __eq__(self, other):
        if not isinstance(other, Move):
            return NotImplemented
        return self.start == other.start

    def __ne__(self, other):
        if not isinstance(other, Move):
            return NotImplemented
        return not self == other

    def _d(self, previous):
        cmd = "M"
        x = self.end.real
        y = self.end.imag
        if self.relative:
            cmd = "m"
            if previous:
                x -= previous.end.real
                y -= previous.end.imag
        return f"{cmd} {x:G},{y:G}"

    def point(self, pos):
        return self.start

    def tangent(self, pos):
        return 0

    def length(self, error=ERROR, min_depth=MIN_DEPTH):
        return 0

    def boundingbox(self):
        x_min = min(self.start.real, self.end.real)
        x_max = max(self.start.real, self.end.real)
        y_min = min(self.start.imag, self.end.imag)
        y_max = max(self.start.imag, self.end.imag)
        return [x_min, y_min, x_max, y_max]


class Close(Linear):
    """Represents the closepath command"""

    def __eq__(self, other):
        if not isinstance(other, Close):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __repr__(self):
        return f"Close(start={self.start}, end={self.end})"

    def _d(self, previous):
        return "z" if self.relative else "Z"

    def boundingbox(self):
        x_min = min(self.start.real, self.end.real)
        x_max = max(self.start.real, self.end.real)
        y_min = min(self.start.imag, self.end.imag)
        y_max = max(self.start.imag, self.end.imag)
        return [x_min, y_min, x_max, y_max]


class Path(MutableSequence):
    """A Path is a sequence of path segments"""

    def __init__(self, *segments):
        self._segments = list(segments)
        self._length = None
        self._lengths = None
        # Fractional distance from starting point through the end of each segment.
        self._fractions = []

    def __getitem__(self, index):
        return self._segments[index]

    def __setitem__(self, index, value):
        self._segments[index] = value
        self._length = None

    def __delitem__(self, index):
        del self._segments[index]
        self._length = None

    def insert(self, index, value):
        self._segments.insert(index, value)
        self._length = None

    def reverse(self):
        # Reversing the order of a path would require reversing each element
        # as well. That's not implemented.
        raise NotImplementedError

    def __len__(self):
        return len(self._segments)

    def __repr__(self):
        return "Path(%s)" % (", ".join(repr(x) for x in self._segments))

    def __eq__(self, other):
        if not isinstance(other, Path):
            return NotImplemented
        if len(self) != len(other):
            return False
        for s, o in zip(self._segments, other._segments):
            if not s == o:
                return False
        return True

    def __ne__(self, other):
        if not isinstance(other, Path):
            return NotImplemented
        return not self == other

    def _calc_lengths(self, error=ERROR, min_depth=MIN_DEPTH):
        if self._length is not None:
            return

        lengths = [
            each.length(error=error, min_depth=min_depth) for each in self._segments
        ]
        self._length = sum(lengths)
        if self._length == 0:
            self._lengths = lengths
        else:
            self._lengths = [each / self._length for each in lengths]
        # Calculate the fractional distance for each segment to use in point()
        fraction = 0
        for each in self._lengths:
            fraction += each
            self._fractions.append(fraction)

    def _find_segment(self, pos, error=ERROR):
        # Shortcuts
        if pos == 0.0:
            return self._segments[0], pos
        if pos == 1.0:
            return self._segments[-1], pos

        self._calc_lengths(error=error)

        # Fix for paths of length 0 (i.e. points)
        if self._length == 0:
            return self._segments[0], 0.0

        # Find which segment the point we search for is located on:
        i = bisect(self._fractions, pos)
        if i == 0:
            segment_pos = pos / self._fractions[0]
        else:
            segment_pos = (pos - self._fractions[i - 1]) / (
                self._fractions[i] - self._fractions[i - 1]
            )
        return self._segments[i], segment_pos

    def point(self, pos, error=ERROR):
        segment, pos = self._find_segment(pos, error)
        return segment.point(pos)

    def tangent(self, pos, error=ERROR):
        segment, pos = self._find_segment(pos, error)
        return segment.tangent(pos)

    def length(self, error=ERROR, min_depth=MIN_DEPTH):
        self._calc_lengths(error, min_depth)
        return self._length

    def d(self):
        parts = []
        previous_segment = None

        for segment in self:
            parts.append(segment._d(previous_segment))
            previous_segment = segment

        return " ".join(parts)

    def boundingbox(self):
        x_coords = []
        y_coords = []

        for e in self:
            x_min, y_min, x_max, y_max = e.boundingbox()
            x_coords.append(x_min)
            x_coords.append(x_max)
            y_coords.append(y_min)
            y_coords.append(y_max)

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        return [x_min, y_min, x_max, y_max]
