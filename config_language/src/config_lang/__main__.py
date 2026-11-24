#Командная строка транслятора учебного языка в YAML.

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .translator import Translator, TranslationError


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Разобрать аргументы командной строки.

    Args:
        argv: Список аргументов; ``None`` для ``sys.argv[1:]``.

    Returns:
        Объект с полями ``output`` (путь к файлу результата).
    """
    parser = argparse.ArgumentParser(
        prog="config_lang",
        description=(
            "Преобразование учебного конфигурационного языка "
            "варианта №17 в YAML."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Путь к файлу результата в формате YAML.",
    )
    return parser.parse_args(argv)


def run(argv: Sequence[str] | None = None) -> int:
    """Выполнить трансляцию stdin в выходной файл YAML.

    Args:
        argv: Аргументы командной строки.

    Returns:
        Код возврата: ``0`` при успехе, ``1`` при ошибке.
    """
    args = parse_args(argv)
    source = sys.stdin.read()
    translator = Translator()
    try:
        result = translator.translate(source)
    except TranslationError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(result)
    except OSError as exc:
        print(f"Ошибка записи файла: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    """Точка входа консольного скрипта."""
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
