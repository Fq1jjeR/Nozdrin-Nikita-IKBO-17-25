"""Точка входа CLI-приложения визуализации графа зависимостей.

Поддерживает режимы работы:
    - config: вывод параметров (этап 1);
    - deps: вывод прямых зависимостей пакета (этап 2).
"""

import sys

from .collector import get_direct_dependencies
from .config import format_config, parse_args


def run_config_mode(config) -> int:
    """Вывести параметры приложения в формате ключ=значение.

    Args:
        config: конфигурация приложения.

    Returns:
        Код возврата: 0 при успехе.
    """
    print("Параметры приложения:")
    print(format_config(config))
    return 0


def run_deps_mode(config) -> int:
    """Вывести прямые зависимости пакета на экран.

    Args:
        config: конфигурация приложения.

    Returns:
        Код возврата: 0 при успехе, 1 при ошибке.
    """
    try:
        deps = get_direct_dependencies(config)
    except RuntimeError as exc:
        print(f"Ошибка сбора данных: {exc}", file=sys.stderr)
        return 1
    print(f"Прямые зависимости пакета {config.package}:")
    if not deps:
        print("  (нет зависимостей)")
        return 0
    for dep in deps:
        print(f"  - {dep}")
    return 0


def main(argv=None) -> int:
    """Запустить приложение в выбранном режиме.

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
    if config.mode == "config":
        return run_config_mode(config)
    if config.mode == "deps":
        return run_deps_mode(config)
    print(
        f"Режим {config.mode!r} ещё не реализован",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())