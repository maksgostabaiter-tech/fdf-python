from pathlib import Path

import pytest

from main import main


@pytest.mark.parametrize("args", [[], ["a.fdf", "b.fdf"]])
def test_usage(args: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert main(args) == 2
    assert "Использование" in capsys.readouterr().err


def test_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(tmp_path / "missing.fdf")]) == 1
    assert "Traceback" not in capsys.readouterr().err


def test_format_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "invalid.fdf"
    path.write_text("0 x", encoding="utf-8")
    assert main([str(path)]) == 1
    message = capsys.readouterr().err
    assert "строка 1, колонка 2" in message
    assert "Traceback" not in message
