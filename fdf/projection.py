"""Преобразование координат карты в координаты окна."""

from dataclasses import dataclass
from math import cos, pi, sin

from fdf.model import Map, Point


@dataclass
class Camera:
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    z_scale: float = 1.0
    angle: float = pi / 6  # Радианы; pi / 6 соответствует 30 градусам.

    def raw_project(self, point: Point) -> tuple[float, float]:
        """Координаты до масштабирования и сдвига."""
        return (
            (point.x - point.y) * cos(self.angle),
            (point.x + point.y) * sin(self.angle) - point.z * self.z_scale,
        )

    def project(self, point: Point) -> tuple[float, float]:
        x, y = self.raw_project(point)
        return x * self.scale + self.offset_x, y * self.scale + self.offset_y

    def fit(self, grid: Map, width: int, height: int) -> None:
        """Вписать ограничивающий прямоугольник с полями 5% с каждой стороны."""
        if width <= 0 or height <= 0:
            raise ValueError("Размеры окна должны быть положительными")
        coordinates = [self.raw_project(point) for point in grid]
        min_x = min(x for x, _ in coordinates)
        max_x = max(x for x, _ in coordinates)
        min_y = min(y for _, y in coordinates)
        max_y = max(y for _, y in coordinates)
        span_x, span_y = max_x - min_x, max_y - min_y
        limits: list[float] = []
        if span_x > 0:
            limits.append(width / span_x)
        if span_y > 0:
            limits.append(height / span_y)
        # Нулевой размер не ограничивает масштаб. Одна точка — частный случай.
        self.scale = min(limits) * 0.9 if limits else 1.0
        self.offset_x = width / 2 - (min_x + max_x) / 2 * self.scale
        self.offset_y = height / 2 - (min_y + max_y) / 2 * self.scale
