"""Запускаемая заготовка приложения."""

import sys


def main() -> int:
    print("Использование: python main.py <файл.fdf>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
