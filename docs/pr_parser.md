Модель Point и Map хранит прямоугольную карту, координаты и цвета.
Парсер принимает отрицательные высоты и короткую запись цвета, сообщает
строку и колонку при ошибке формата. OSError остаётся вызывающему коду.

Проверка: pytest -q, mypy --strict fdf main.py, ruff check .
Карты elem.fdf, flat.fdf, peak.fdf, negative.fdf, single.fdf и maps/bad/.
