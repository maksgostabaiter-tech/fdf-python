"""Преобразование текста .fdf в проверенную модель."""

import re
from pathlib import Path

from fdf.errors import MapFormatError
from fdf.model import Map, Point

INTEGER = re.compile(r"[+-]?[0-9]+")
COLOR = re.compile(r"0[xX][0-9a-fA-F]{1,6}")


def parse_value(token: str, line: int, column: int) -> tuple[int, str | None]:
    """Колонка — номер значения в строке, начиная с единицы."""
    location = f"строка {line}, колонка {column}"
    parts = token.split(",")
    if not INTEGER.fullmatch(parts[0]):
        raise MapFormatError(f"{location}: {parts[0]!r} — не целое число")
    try:
        height = int(parts[0])
    except ValueError as error:
        raise MapFormatError(f"{location}: слишком длинная запись высоты") from error
    if len(parts) == 1:
        return height, None
    if len(parts) != 2 or not COLOR.fullmatch(parts[1]):
        raise MapFormatError(f"{location}: {token!r} — некорректный цвет")
    return height, f"#{int(parts[1], 16):06X}"


def parse_map(path: str | Path) -> Map:
    """OSError намеренно передаётся вызывающему коду."""
    try:
        lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError as error:
        line = error.object[:error.start].count(b"\n") + 1
        raise MapFormatError(
            f"строка {line}, колонка 1: файл должен быть текстом UTF-8"
        ) from error
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        raise MapFormatError("строка 1, колонка 1: пустой файл карты")

    rows: list[list[Point]] = []
    width = len(lines[0].split())
    for y, line in enumerate(lines):
        tokens = line.split()
        if not tokens:
            raise MapFormatError(f"строка {y + 1}, колонка 1: пустая строка внутри карты")
        if len(tokens) != width:
            column = min(len(tokens), width) + 1
            raise MapFormatError(
                f"строка {y + 1}, колонка {column}: "
                f"ожидалось {width} значений, получено {len(tokens)}"
            )
        row: list[Point] = []
        for x, token in enumerate(tokens):
            z, color = parse_value(token, y + 1, x + 1)
            row.append(Point(x, y, z, color))
        rows.append(row)
    return Map(rows)
