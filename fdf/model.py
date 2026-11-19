"""Данные карты и поиск рёбер без зависимости от графики."""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """Одна точка: столбец x, строка y, высота z и необязательный цвет."""

    x: int
    y: int
    z: int
    color: str | None = None


class Map:
    """Прямоугольная непустая сетка. len и for работают со всеми точками."""

    def __init__(self, points: list[list[Point]]) -> None:
        if not points or not points[0]:
            raise ValueError("Карта должна содержать хотя бы одну точку")
        width = len(points[0])
        if any(len(row) != width for row in points):
            raise ValueError("Карта должна быть прямоугольной")
        for y, row in enumerate(points):
            for x, point in enumerate(row):
                if (point.x, point.y) != (x, y):
                    raise ValueError("Координаты точки не совпадают с её позицией")
        # Копируем в кортежи, чтобы форму карты нельзя было случайно изменить.
        self.points = tuple(tuple(row) for row in points)
        self.width = width
        self.height = len(points)

    def __len__(self) -> int:
        return self.width * self.height

    def __iter__(self) -> Iterator[Point]:
        for row in self.points:
            yield from row

    def __getitem__(self, row: int) -> tuple[Point, ...]:
        """Доступ map[y][x]; сначала строка, затем столбец."""
        return self.points[row]

    def get(self, x: int, y: int) -> Point:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("Точка находится вне карты")
        return self.points[y][x]

    def neighbors(self, x: int, y: int) -> list[Point]:
        """Только правый и нижний соседи — каждое ребро рисуется один раз."""
        self.get(x, y)  # Проверяем исходную точку, включая отрицательные индексы.
        result: list[Point] = []
        if x + 1 < self.width:
            result.append(self.get(x + 1, y))
        if y + 1 < self.height:
            result.append(self.get(x, y + 1))
        return result
