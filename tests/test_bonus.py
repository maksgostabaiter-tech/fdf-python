from math import pi

import pytest

from fdf.model import Map, Point
from fdf.projection import Camera, height_color, lerp_color


@pytest.mark.parametrize(("t", "expected"), [
    (0, "#000000"), (1, "#FFFFFF"), (0.5, "#808080"),
    (-1, "#000000"), (2, "#FFFFFF"),
])
def test_lerp(t: float, expected: str) -> None:
    assert lerp_color("#000000", "#FFFFFF", t) == expected


def test_height_palette() -> None:
    assert height_color(0, 0, 3) == "#3B82F6"
    assert height_color(1, 0, 3) == "#22C55E"
    assert height_color(2, 0, 3) == "#FACC15"
    assert height_color(3, 0, 3) == "#EF4444"
    assert height_color(7, 7, 7) == "#3B82F6"


def test_zoom_anchor_stays_fixed() -> None:
    camera = Camera(scale=10, offset_x=30, offset_y=40)
    point = Point(2, 3, 4)
    anchor = camera.project(point)
    camera.zoom(2, *anchor)
    assert camera.project(point) == pytest.approx(anchor)
    assert camera.scale == 20


def test_zoom_distances_double() -> None:
    camera = Camera()
    p = Point(1, 0, 0)
    before = camera.project(p)
    camera.zoom(2, 0, 0)
    assert camera.project(p) == pytest.approx((before[0] * 2, before[1] * 2))


def test_top_view_ignores_height() -> None:
    camera = Camera(top_view=True)
    assert camera.project(Point(2, 3, 999)) == (2, 3)


def test_angle_zero_and_height_scale_zero() -> None:
    assert Camera(angle=0).project(Point(2, 1, 3)) == (1, -3)
    assert Camera(z_scale=0).project(Point(2, 1, 3)) == Camera(z_scale=0).project(Point(2, 1, 0))


@pytest.mark.parametrize("angle", [0, pi / 6, pi / 3])
def test_rotated_fit_stays_centered(angle: float) -> None:
    grid = Map([[Point(x, y, x + y) for x in range(3)] for y in range(2)])
    camera = Camera(angle=angle)
    camera.fit(grid, 800, 600)
    coords = [camera.project(p) for p in grid]
    assert (min(x for x, _ in coords) + max(x for x, _ in coords)) / 2 == pytest.approx(400)
    assert (min(y for _, y in coords) + max(y for _, y in coords)) / 2 == pytest.approx(300)
