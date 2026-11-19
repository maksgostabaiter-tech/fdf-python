"""Единственный модуль, импортирующий графическую библиотеку tkinter."""

from __future__ import annotations

import tkinter as tk
from math import pi

from fdf.errors import FdfError
from fdf.model import Map
from fdf.projection import Camera, height_color, lerp_color


class App:
    def __init__(self, grid: Map) -> None:
        self.grid = grid
        self.camera = Camera()
        self.camera.fit(grid, 1000, 700)
        z_min = min(point.z for point in grid)
        z_max = max(point.z for point in grid)
        self.colors = {
            point: point.color or height_color(point.z, z_min, z_max) for point in grid
        }
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            raise FdfError(f"Не удалось открыть графическое окно: {error}") from error
        self.root.title("FdF — карта высот")
        self.root.geometry("1000x750")
        self.root.minsize(400, 300)
        self.canvas = tk.Canvas(self.root, bg="#101827", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.status = tk.Label(
            self.root, text="Колесо: масштаб   Стрелки: сдвиг   +/-: высота   "
            "T: вид сверху   [ ]: угол   R: сброс   Esc: выход",
            bg="#1E293B", fg="#E2E8F0", pady=10, wraplength=950,
            font=("DejaVu Sans", 10),
        )
        self.status.pack(fill=tk.X)
        self.root.bind("<Escape>", lambda event: self.root.destroy())
        self.root.bind("<KeyPress>", self._on_key)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", lambda event: self._zoom(1.1))
        self.canvas.bind("<Button-5>", lambda event: self._zoom(1 / 1.1))
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.canvas.bind("<Configure>", self._on_resize)
        self.pending_redraw: str | None = None

    def _fit(self) -> None:
        self.camera.fit(
            self.grid, max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height()),
        )

    def _zoom(self, factor: float) -> None:
        coordinates = [self.camera.project(p) for p in self.grid]
        anchor_x = (min(x for x, _ in coordinates) + max(x for x, _ in coordinates)) / 2
        anchor_y = (min(y for _, y in coordinates) + max(y for _, y in coordinates)) / 2
        self.camera.zoom(factor, anchor_x, anchor_y)
        self.request_redraw()

    def _on_wheel(self, event: tk.Event[tk.Misc]) -> None:
        if event.delta:
            self._zoom(1.1 if event.delta > 0 else 1 / 1.1)

    def _on_key(self, event: tk.Event[tk.Misc]) -> None:
        key = event.keysym
        shifts = {"Left": (-20, 0), "Right": (20, 0), "Up": (0, -20), "Down": (0, 20)}
        if key in shifts:
            dx, dy = shifts[key]
            self.camera.offset_x += dx
            self.camera.offset_y += dy
        elif key in ("plus", "equal", "KP_Add", "+", "=", "minus", "KP_Subtract", "-"):
            step = -0.2 if key in ("minus", "KP_Subtract", "-") else 0.2
            self.camera.z_scale = max(0.0, min(100.0, self.camera.z_scale + step))
            self._fit()
        elif key.lower() == "t":
            self.camera.top_view = not self.camera.top_view
            self._fit()
        elif key in ("bracketleft", "bracketright", "[", "]"):
            step = -pi / 36 if key in ("bracketleft", "[") else pi / 36
            self.camera.angle = max(0.0, min(pi * 4 / 9, self.camera.angle + step))
            self._fit()
        elif key.lower() == "r":
            self.camera = Camera()
            self._fit()
        else:
            return
        self.request_redraw()

    def _on_resize(self, event: tk.Event[tk.Misc]) -> None:
        self.camera.fit(self.grid, max(1, event.width), max(1, event.height))
        self.request_redraw()

    def request_redraw(self) -> None:
        """Объединить частые события изменения окна в одну перерисовку."""
        if self.pending_redraw is not None:
            self.root.after_cancel(self.pending_redraw)
        self.pending_redraw = self.root.after_idle(self.draw)

    def draw(self) -> None:
        self.pending_redraw = None
        self.canvas.delete("all")
        projected = {point: self.camera.project(point) for point in self.grid}
        for point in self.grid:
            x1, y1 = projected[point]
            for neighbor in self.grid.neighbors(point.x, point.y):
                x2, y2 = projected[neighbor]
                self._draw_edge(x1, y1, x2, y2, self.colors[point], self.colors[neighbor])
        if len(self.grid) == 1:
            x, y = projected[self.grid[0][0]]
            self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=self.colors[self.grid[0][0]], outline="",
            )

    def _draw_edge(
        self, x1: float, y1: float, x2: float, y2: float, color1: str, color2: str,
    ) -> None:
        # Tk рисует линию одним цветом. Градиент приближаем 12 отрезками.
        segments = 1 if color1 == color2 else 12
        for index in range(segments):
            t1, t2 = index / segments, (index + 1) / segments
            self.canvas.create_line(
                x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1,
                x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2,
                fill=lerp_color(color1, color2, (t1 + t2) / 2), width=1.5,
            )

    def run(self) -> None:
        try:
            self.root.mainloop()
        except tk.TclError as error:
            raise FdfError(f"Ошибка графического интерфейса: {error}") from error
