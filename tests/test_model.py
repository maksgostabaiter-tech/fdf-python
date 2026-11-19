import pytest

from fdf.model import Map, Point


def make_grid() -> Map:
    return Map([[Point(x, y, x + y) for x in range(3)] for y in range(2)])


def test_len_and_iteration() -> None:
    grid = make_grid()
    assert len(grid) == 6
    assert [(p.x, p.y) for p in grid] == [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]


def test_neighbors_and_edge_count() -> None:
    grid = make_grid()
    assert grid.neighbors(0, 0) == [grid[0][1], grid[1][0]]
    assert grid.neighbors(2, 1) == []
    edges = [(p, q) for p in grid for q in grid.neighbors(p.x, p.y)]
    assert len(edges) == (grid.width - 1) * grid.height + (grid.height - 1) * grid.width
    assert len({frozenset((p, q)) for p, q in edges}) == len(edges)


def test_invalid_model() -> None:
    with pytest.raises(ValueError):
        Map([])
    with pytest.raises(ValueError):
        Map([[Point(1, 0, 0)]])
    with pytest.raises(IndexError):
        make_grid().neighbors(-1, 0)
