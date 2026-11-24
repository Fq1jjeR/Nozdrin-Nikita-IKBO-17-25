"""Сбор данных о прямых зависимостях пакетов Cargo (Rust).

Этап 2: получение Cargo.toml по URL репозитория и разбор секции
[dependencies] для извлечения прямых зависимостей пакета.

Запрещено использовать менеджеры пакетов и сторонние библиотеки
для получения информации о зависимостях: разбор Cargo.toml и
HTTP-запросы выполняются средствами стандартной библиотеки Python.
"""

import re
import urllib.error
import urllib.request

from .config import AppConfig


GITHUB_PATTERN = re.compile(
    r"^https?://github\.com/([^/]+)/([^/]+)/?$"
)
RAW_BASE = "https://raw.githubusercontent.com"
DEFAULT_BRANCHES = ("main", "master")
CARGO_TOML_NAME = "Cargo.toml"
FETCH_TIMEOUT = 15
DEPENDENCIES_HEADER = "[dependencies]"
INLINE_DEPS_PREFIX = "[dependencies."
DEPENDENCY_LINE = re.compile(r"^([A-Za-z0-9_-]+)\s*=")
INLINE_DEPS_PATTERN = re.compile(
    r"^\[dependencies\.([A-Za-z0-9_-]+)\]$"
)


def fetch_text(url: str) -> str:
    """Получить текстовое содержимое ресурса по URL.

    Args:
        url: URL-адрес ресурса.

    Returns:
        Текстовое содержимое ресурса в кодировке UTF-8.

    Raises:
        RuntimeError: при ошибке сети или HTTP-запроса.
    """
    try:
        with urllib.request.urlopen(
            url, timeout=FETCH_TIMEOUT
        ) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as exc:
        raise RuntimeError(
            f"не удалось получить данные по URL {url}: {exc}"
        ) from exc


def read_file(path: str) -> str:
    """Прочитать текстовый файл.

    Args:
        path: путь к файлу.

    Returns:
        Содержимое файла в кодировке UTF-8.

    Raises:
        RuntimeError: при ошибке чтения файла.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise RuntimeError(
            f"не удалось прочитать файл {path}: {exc}"
        ) from exc


def github_raw_candidates(repo_url: str) -> list:
    """Построить список URL-кандидатов для Cargo.toml на GitHub.

    Args:
        repo_url: URL репозитория на GitHub.

    Returns:
        Список URL-кандидатов для веток main и master.
        Пустой список, если URL не является GitHub-репозиторием.
    """
    match = GITHUB_PATTERN.match(repo_url.rstrip("/"))
    if not match:
        return []
    owner, repo = match.group(1), match.group(2)
    candidates = []
    for branch in DEFAULT_BRANCHES:
        url = (
            f"{RAW_BASE}/{owner}/{repo}/{branch}/"
            f"{CARGO_TOML_NAME}"
        )
        candidates.append(url)
    return candidates


def fetch_first(candidates: list) -> str:
    """Получить содержимое первого доступного URL из списка.

    Args:
        candidates: список URL-кандидатов.

    Returns:
        Содержимое первого доступного ресурса.

    Raises:
        RuntimeError: если ни один URL недоступен.
    """
    errors = []
    for url in candidates:
        try:
            return fetch_text(url)
        except RuntimeError as exc:
            errors.append(str(exc))
    raise RuntimeError(
        "все URL-кандидаты недоступны: " + "; ".join(errors)
    )


def get_cargo_toml(config: AppConfig) -> str:
    """Получить содержимое Cargo.toml согласно конфигурации.

    Args:
        config: конфигурация приложения.

    Returns:
        Содержимое Cargo.toml в виде строки.

    Raises:
        RuntimeError: при ошибке получения данных.
    """
    if config.test_mode:
        return read_file(config.repo)
    candidates = github_raw_candidates(config.repo)
    if candidates:
        return fetch_first(candidates)
    return fetch_text(config.repo)


def parse_dependencies(toml_text: str) -> list:
    """Разобрать прямые зависимости из файла Cargo.toml.

    Поддерживаются два формата описания зависимостей:
        1. Секция [dependencies] с записями name = ...
        2. Inline-таблицы [dependencies.name] для каждой зависимости.

    Args:
        toml_text: содержимое файла Cargo.toml.

    Returns:
        Список имён прямых зависимостей пакета.
    """
    lines = toml_text.splitlines()
    in_deps = False
    deps = []
    for line in lines:
        stripped = line.strip()
        section = _classify_section(stripped)
        if section == "inline":
            deps.append(
                INLINE_DEPS_PATTERN.match(stripped).group(1)
            )
            in_deps = False
            continue
        in_deps = _update_section_state(section, in_deps)
        if not in_deps:
            continue
        match = DEPENDENCY_LINE.match(stripped)
        if match:
            deps.append(match.group(1))
    return deps


def _classify_section(stripped: str) -> str:
    """Классифицировать строку-заголовок секции.

    Args:
        stripped: очищенная строка Cargo.toml.

    Returns:
        "dependencies", "inline", "other" или "none".
    """
    if not (stripped.startswith("[") and stripped.endswith("]")):
        return "none"
    if stripped == DEPENDENCIES_HEADER:
        return "dependencies"
    if stripped.startswith(INLINE_DEPS_PREFIX):
        return "inline"
    return "other"


def _update_section_state(section: str, current: bool) -> bool:
    """Обновить флаг нахождения в секции [dependencies].

    Args:
        section: классификация текущей строки.
        current: текущее значение флага секции.

    Returns:
        True, если обработка идёт внутри [dependencies].
    """
    if section == "dependencies":
        return True
    if section in ("inline", "other"):
        return False
    return current


def get_direct_dependencies(config: AppConfig) -> list:
    """Получить список прямых зависимостей пакета.

    Args:
        config: конфигурация приложения.

    Returns:
        Список имён прямых зависимостей пакета.

    Raises:
        RuntimeError: при ошибке получения или разбора данных.
    """
    toml_text = get_cargo_toml(config)
    return parse_dependencies(toml_text)