"""Точка входа CLI-приложения визуализации графа зависимостей.

Этап 1: вывод настраиваемых параметров в формате ключ-значение
и обработка ошибок для всех параметров.
"""

import sys

from .config import format_config, parse_args


def main(argv=None) -> int:
    """Запустить приложение.

    Разбирает аргументы командной строки, проверяет их корректность
    и выводит все настраиваемые параметры в формате ключ=значение.

    Args:
        argv: список аргументов или None для использования sys.argv.

    Returns:
        Код возврата: 0 при успешном выполнении, 1 при ошибке.
    """
    try:
        config = parse_args(argv)
    except ValueError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1
    print("Параметры приложения:")
    print(format_config(config))
    return 0


if __name__ == "__main__":
    sys.exit(main())