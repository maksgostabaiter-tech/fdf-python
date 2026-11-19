"""Преобразование координат карты в координаты окна."""

from dataclasses import dataclass
from math import cos, isfinite, pi, sin

from fdf.model import Map, Point


@dataclass
class Camera:
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    z_scale: float = 1.0
    angle: float = pi / 6  # Радианы; pi / 6 соответствует 30 градусам.
    top_view: bool = False

    def raw_project(self, point: Point) -> tuple[float, float]:
        """Координаты до масштабирования и сдвига."""
        if self.top_view:
            return float(point.x), float(point.y)
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
        if not all(isfinite(value) for value in (min_x, max_x, min_y, max_y, span_x, span_y)):
            raise OverflowError("Координаты выходят за диапазон экранных вычислений")
        limits: list[float] = []
        if span_x > 0:
            limits.append(width / span_x)
        if span_y > 0:
            limits.append(height / span_y)
        # Нулевой размер не ограничивает масштаб. Одна точка — частный случай.
        self.scale = min(limits) * 0.9 if limits else 1.0
        self.offset_x = width / 2 - (min_x + max_x) / 2 * self.scale
        self.offset_y = height / 2 - (min_y + max_y) / 2 * self.scale

    def zoom(self, factor: float, anchor_x: float, anchor_y: float) -> None:
        """Изменить масштаб, оставив экранную опорную точку неподвижной."""
        if factor <= 0:
            raise ValueError("Коэффициент масштаба должен быть положительным")
        new_scale = max(1e-9, min(1e9, self.scale * factor))
        actual_factor = new_scale / self.scale
        self.offset_x = anchor_x + (self.offset_x - anchor_x) * actual_factor
        self.offset_y = anchor_y + (self.offset_y - anchor_y) * actual_factor
        self.scale = new_scale


def lerp_color(start: str, end: str, t: float) -> str:
    """Линейная интерполяция каждого канала RGB, t ограничивается [0, 1]."""
    t = max(0.0, min(1.0, t))
    channels = []
    for offset in (1, 3, 5):
        a = int(start[offset:offset + 2], 16)
        b = int(end[offset:offset + 2], 16)
        channels.append(round(a + (b - a) * t))
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def height_color(z: int, z_min: int, z_max: int) -> str:
    """Палитра: синий, зелёный, жёлтый, красный."""
    palette = ("#3B82F6", "#22C55E", "#FACC15", "#EF4444")
    if z_max == z_min:
        return palette[0]
    t = max(0.0, min(1.0, (z - z_min) / (z_max - z_min)))
    position = t * (len(palette) - 1)
    index = min(int(position), len(palette) - 2)
    return lerp_color(palette[index], palette[index + 1], position - index)
