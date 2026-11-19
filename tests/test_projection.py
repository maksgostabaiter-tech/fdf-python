from math import sqrt
from pathlib import Path

import pytest

from fdf.model import Map, Point
from fdf.parser import parse_map
from fdf.projection import Camera

ROOT = Path(__file__).resolve().parents[1]


def test_origin_and_height() -> None:
    camera = Camera()
    assert camera.project(Point(0, 0, 0)) == (0, 0)
    assert camera.project(Point(0, 0, 1))[1] == -1
    assert camera.project(Point(1, 0, 0)) == pytest.approx((sqrt(3) / 2, 0.5))


@pytest.mark.parametrize("filename", ["elem.fdf", "flat.fdf", "negative.fdf", "single.fdf"])
@pytest.mark.parametrize(("width", "height"), [(800, 600), (100, 1000), (1000, 100)])
def test_fit(filename: str, width: int, height: int) -> None:
    grid = parse_map(ROOT / "maps" / filename)
    camera = Camera()
    camera.fit(grid, width, height)
    coords = [camera.project(p) for p in grid]
    assert all(0 <= x <= width and 0 <= y <= height for x, y in coords)
    assert (min(x for x, _ in coords) + max(x for x, _ in coords)) / 2 == pytest.approx(width / 2)
    assert (min(y for _, y in coords) + max(y for _, y in coords)) / 2 == pytest.approx(height / 2)


def test_one_point() -> None:
    camera = Camera()
    camera.fit(Map([[Point(0, 0, 100)]]), 800, 600)
    assert camera.project(Point(0, 0, 100)) == (400, 300)


def test_flat_is_symmetric() -> None:
    grid = parse_map(ROOT / "maps/flat.fdf")
    camera = Camera()
    camera.fit(grid, 800, 600)
    for p in grid:
        a = camera.project(p)
        b = camera.project(grid[p.x][p.y])
        assert a[0] + b[0] == pytest.approx(800)
        assert a[1] == pytest.approx(b[1])


def test_degenerate_line() -> None:
    camera = Camera(angle=0)
    grid = Map([[Point(x, 0, 0) for x in range(3)]])
    camera.fit(grid, 800, 600)
    assert all(camera.project(p)[1] == 300 for p in grid)
