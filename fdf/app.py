"""Единственный модуль, импортирующий графическую библиотеку tkinter."""

from __future__ import annotations

import tkinter as tk

from fdf.errors import FdfError
from fdf.model import Map
from fdf.projection import Camera


class App:
    def __init__(self, grid: Map) -> None:
        self.grid = grid
        self.camera = Camera()
        self.camera.fit(grid, 1000, 700)
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
            self.root, text="Esc — выход", bg="#1E293B", fg="#E2E8F0", pady=10,
        )
        self.status.pack(fill=tk.X)
        self.root.bind("<Escape>", lambda event: self.root.destroy())
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.canvas.bind("<Configure>", self._on_resize)
        self.pending_redraw: str | None = None

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
                self.canvas.create_line(x1, y1, x2, y2, fill="#E2E8F0", width=1.5)
        if len(self.grid) == 1:
            x, y = projected[self.grid[0][0]]
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#E2E8F0", outline="")

    def run(self) -> None:
        try:
            self.root.mainloop()
        except tk.TclError as error:
            raise FdfError(f"Ошибка графического интерфейса: {error}") from error
