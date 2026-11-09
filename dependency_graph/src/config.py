"""Конфигурация CLI-приложения для анализа зависимостей.

Модуль содержит функции для разбора опций командной строки,
их валидации и форматирования в виде ключ-значение.

Вариант 17: источник параметров -- опции командной строки.
Настраиваемые параметры:
    - имя анализируемого пакета;
    - URL репозитория или путь к файлу тестового репозитория;
    - режим работы с тестовым репозиторием;
    - имя сгенерированного файла с изображением графа;
    - максимальная глубина анализа зависимостей.
"""

import argparse
import os
import re
from dataclasses import dataclass


MAX_DEPTH_DEFAULT = 10
MAX_DEPTH_MIN = 1
MAX_DEPTH_MAX = 100
OUTPUT_DEFAULT = "graph.png"
MODE_DEFAULT = "config"
MODE_CHOICES = ("config", "deps", "graph", "reverse", "viz")
PACKAGE_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
OUTPUT_FORBIDDEN_CHARS = ("/", "\\", os.sep)


@dataclass
class AppConfig:
    """Конфигурация приложения.

    Атрибуты:
        package: имя анализируемого пакета.
        repo: URL репозитория или путь к файлу тестового репозитория.
        test_mode: флаг режима работы с тестовым репозиторием.
        output: имя сгенерированного файла с изображением графа.
        max_depth: максимальная глубина анализа зависимостей.
        mode: режим работы приложения (config, deps, graph, ...).
    """

    package: str
    repo: str
    test_mode: bool
    output: str
    max_depth: int
    mode: str = MODE_DEFAULT


def validate_package(name: str) -> str:
    """Проверить корректность имени пакета.

    Args:
        name: имя пакета из командной строки.

    Returns:
        Проверенное имя пакета.

    Raises:
        ValueError: если имя пустое или содержит недопустимые символы.
    """
    if not name:
        raise ValueError("имя пакета не должно быть пустым")
    if not PACKAGE_NAME_PATTERN.match(name):
        raise ValueError(
            "имя пакета должно начинаться с буквы и "
            "содержать только буквы, цифры, '_' и '-'"
        )
    return name


def validate_output(filename: str) -> str:
    """Проверить корректность имени выходного файла.

    Args:
        filename: имя файла изображения графа.

    Returns:
        Проверенное имя файла.

    Raises:
        ValueError: если имя пустое или содержит разделители пути.
    """
    if not filename:
        raise ValueError("имя выходного файла не должно быть пустым")
    for char in OUTPUT_FORBIDDEN_CHARS:
        if char in filename:
            raise ValueError(
                "имя файла не должно содержать "
                "разделители пути"
            )
    return filename


def validate_repo(repo: str, test_mode: bool) -> str:
    """Проверить корректность URL или пути к репозиторию.

    Args:
        repo: URL репозитория или путь к файлу.
        test_mode: флаг тестового режима.

    Returns:
        Проверенный URL или путь.

    Raises:
        ValueError: если значение пустое, либо в тестовом режиме
            указанный файл не существует.
    """
    if not repo:
        raise ValueError("URL или путь не должен быть пустым")
    if test_mode and not os.path.isfile(repo):
        raise ValueError(
            f"файл тестового репозитория не найден: {repo}"
        )
    return repo


def validate_max_depth(value: str) -> int:
    """Проверить корректность максимальной глубины анализа.

    Args:
        value: строковое значение глубины.

    Returns:
        Целочисленное значение глубины.

    Raises:
        ValueError: если значение не является целым числом в диапазоне.
    """
    try:
        depth = int(value)
    except ValueError as exc:
        raise ValueError(
            "глубина должна быть целым числом"
        ) from exc
    if depth < MAX_DEPTH_MIN:
        raise ValueError(
            f"глубина должна быть не менее {MAX_DEPTH_MIN}"
        )
    if depth > MAX_DEPTH_MAX:
        raise ValueError(
            f"глубина должна быть не более {MAX_DEPTH_MAX}"
        )
    return depth


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки.

    Returns:
        Настроенный объект ArgumentParser с описанием всех параметров.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Инструмент визуализации графа зависимостей "
            "для пакетов Cargo (Rust). Вариант 17."
        ),
    )
    _add_required_args(parser)
    _add_optional_args(parser)
    return parser


def _add_required_args(parser: argparse.ArgumentParser):
    """Добавить обязательные аргументы командной строки.

    Args:
        parser: объект ArgumentParser для добавления аргументов.
    """
    parser.add_argument(
        "-p", "--package",
        required=True,
        help="имя анализируемого пакета",
    )
    parser.add_argument(
        "-r", "--repo",
        required=True,
        help="URL репозитория или путь к файлу тестового репозитория",
    )


def _add_optional_args(parser: argparse.ArgumentParser):
    """Добавить необязательные аргументы командной строки.

    Args:
        parser: объект ArgumentParser для добавления аргументов.
    """
    parser.add_argument(
        "-t", "--test-mode",
        action="store_true",
        help="режим работы с тестовым репозиторием",
    )
    parser.add_argument(
        "-o", "--output",
        default=OUTPUT_DEFAULT,
        help=f"имя файла изображения (по умолчанию: {OUTPUT_DEFAULT})",
    )
    parser.add_argument(
        "-d", "--max-depth",
        default=str(MAX_DEPTH_DEFAULT),
        help=(
            "максимальная глубина анализа "
            f"(по умолчанию: {MAX_DEPTH_DEFAULT})"
        ),
    )
    parser.add_argument(
        "-m", "--mode",
        choices=MODE_CHOICES,
        default=MODE_DEFAULT,
        help=f"режим работы (по умолчанию: {MODE_DEFAULT})",
    )


def parse_args(argv=None) -> AppConfig:
    """Разобрать аргументы командной строки и создать конфигурацию.

    Args:
        argv: список аргументов или None для использования sys.argv.

    Returns:
        Объект конфигурации AppConfig.

    Raises:
        ValueError: при некорректных значениях параметров.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    package = validate_package(args.package)
    output = validate_output(args.output)
    repo = validate_repo(args.repo, args.test_mode)
    max_depth = validate_max_depth(args.max_depth)
    return AppConfig(
        package=package,
        repo=repo,
        test_mode=args.test_mode,
        output=output,
        max_depth=max_depth,
        mode=args.mode,
    )


def format_config(config: AppConfig) -> str:
    """Отформатировать конфигурацию в виде пар ключ-значение.

    Args:
        config: объект конфигурации приложения.

    Returns:
        Строка с параметрами, по одной паре ключ=значение на строку.
    """
    lines = [
        f"package={config.package}",
        f"repo={config.repo}",
        f"test_mode={config.test_mode}",
        f"output={config.output}",
        f"max_depth={config.max_depth}",
    ]
    return "\n".join(lines)