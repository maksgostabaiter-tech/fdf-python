from pathlib import Path

import pytest

from fdf.errors import MapFormatError
from fdf.parser import parse_map, parse_value

ROOT = Path(__file__).resolve().parents[1]


def test_elem() -> None:
    grid = parse_map(ROOT / "maps/elem.fdf")
    assert (grid.width, grid.height, len(grid)) == (5, 5, 25)
    assert grid[2][2].z == 5
    assert all((p.x, p.y) == (x, y) for y, row in enumerate(grid.points)
               for x, p in enumerate(row))


@pytest.mark.parametrize(("token", "z", "color"), [
    ("7", 7, None), ("-3", -3, None),
    ("2,0xFF8800", 2, "#FF8800"), ("1,0xff", 1, "#0000FF"),
    ("1,0XF", 1, "#00000F"),
])
def test_values(token: str, z: int, color: str | None) -> None:
    assert parse_value(token, 1, 1) == (z, color)


@pytest.mark.parametrize("filename", [
    "empty.fdf", "non_numeric.fdf", "ragged.fdf", "color.fdf", "internal_blank.fdf",
])
def test_bad_maps(filename: str) -> None:
    with pytest.raises(MapFormatError, match=r"строка \d+, колонка \d+"):
        parse_map(ROOT / "maps/bad" / filename)


@pytest.mark.parametrize("token", [
    "x", "1.5", "1_000", "1,", "1,FF0000", "1,0x1000000", "1,0x1,0x2", "1,0x",
])
def test_invalid_tokens(token: str) -> None:
    with pytest.raises(MapFormatError, match="строка 2, колонка 3"):
        parse_value(token, 2, 3)


def test_trailing_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "trailing.fdf"
    path.write_text("1 2\n3 4\n\n  \n", encoding="utf-8")
    assert len(parse_map(path)) == 4


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        parse_map(tmp_path / "missing.fdf")


def test_bad_encoding(tmp_path: Path) -> None:
    path = tmp_path / "binary.fdf"
    path.write_bytes(b"1 2\n3 \xff")
    with pytest.raises(MapFormatError, match="UTF-8"):
        parse_map(path)
