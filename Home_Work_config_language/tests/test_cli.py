"""Тесты интерфейса командной строки транслятора.

Проверяют, что CLI корректно читает вход из стандартного ввода,
записывает результат в указанный файл и возвращает ненулевой
код при ошибках трансляции или записи.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_cli(
    source: str,
    output_path: Path,
) -> tuple[int, str, str]:
    """Запустить CLI как модуль и вернуть код, stdout и stderr.

    Args:
        source: Входной текст для подачи на stdin.
        output_path: Путь к файлу результата.

    Returns:
        Кортеж (код возврата, stdout, stderr).
    """
    proc = subprocess.run(
        [sys.executable, "-m", "config_lang", "-o", str(output_path)],
        input=source,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_cli_writes_yaml_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """CLI пишет корректный YAML в указанный файл."""
    monkeypatch.setenv(
        "PYTHONPATH",
        "src;" + str(Path(__file__).resolve().parents[1]),
    )
    output = tmp_path / "out.yaml"
    code, _out, err = _run_cli("{ a -> 1.0. }", output)
    assert code == 0, f"CLI завершился с ошибкой: {err}"
    assert output.read_text(encoding="utf-8").strip() == "a: 1.0"


def test_cli_returns_error_on_syntax_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """При синтаксической ошибке CLI возвращает код 1."""
    monkeypatch.setenv(
        "PYTHONPATH",
        "src;" + str(Path(__file__).resolve().parents[1]),
    )
    output = tmp_path / "out.yaml"
    code, _out, _err = _run_cli("{ a -> 1.0. ", output)
    assert code == 1
