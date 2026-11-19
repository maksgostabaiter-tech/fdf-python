"""Точка входа: аргументы, диагностика и коды возврата."""

import sys
from collections.abc import Sequence

from fdf.errors import FdfError
from fdf.parser import parse_map


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Использование: python main.py <файл.fdf>", file=sys.stderr)
        return 2
    try:
        grid = parse_map(args[0])
        # Отложенный импорт: ошибочные файлы проверяются даже без tkinter.
        from fdf.app import App

        App(grid).run()
    except (FdfError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    except ImportError as error:
        print(f"Ошибка: недоступна библиотека интерфейса: {error}", file=sys.stderr)
        return 1
    except OverflowError:
        print("Ошибка: высота слишком велика для экранных координат", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
