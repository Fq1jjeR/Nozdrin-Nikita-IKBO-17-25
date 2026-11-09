"""Построение графа зависимостей алгоритмом BFS без рекурсии.

Этап 3: транзитивный обход зависимостей с учётом максимальной
глубины и корректной обработкой циклических зависимостей.

Тестовый режим использует файл описания графа репозитория, где
пакеты названы большими латинскими буквами (A, B, C, ...).
"""

import re
from collections import deque

from .collector import get_cargo_toml, parse_dependencies, read_file
from .config import AppConfig


PACKAGE_LINE = re.compile(r"^([A-Z]+):\s*(.*)$")
ROOT_DEPTH = 0


def parse_test_repo(text: str) -> dict:
    """Разобрать файл тестового репозитория.

    Формат: каждая непустая строка 'PACKAGE: dep1, dep2, ...'
    описывает пакет (большими латинскими буквами) и его прямые
    зависимости. Строки, начинающиеся с '#', игнорируются.

    Args:
        text: содержимое файла тестового репозитория.

    Returns:
        Словарь {имя пакета: [зависимости]}.

    Raises:
        ValueError: при нарушении формата файла.
    """
    result = {}
    for line_num, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = PACKAGE_LINE.match(stripped)
        if not match:
            raise ValueError(
                f"строка {line_num}: ожидался формат "
                "'PACKAGE: dep1, dep2, ...'"
            )
        name = match.group(1)
        deps_str = match.group(2).strip()
        deps = _split_deps(deps_str)
        result[name] = deps
    return result


def _split_deps(deps_str: str) -> list:
    """Разбить строку зависимостей на список имён.

    Args:
        deps_str: строка вида 'dep1, dep2, dep3'.

    Returns:
        Список имён зависимостей без пробелов.
    """
    if not deps_str:
        return []
    return [d.strip() for d in deps_str.split(",") if d.strip()]


class TestRepoProvider:
    """Поставщик зависимостей из тестового репозитория.

    Атрибуты:
        _repo: словарь {пакет: [зависимости]}.
    """

    def __init__(self, repo_map: dict):
        """Инициализировать поставщика картой пакетов.

        Args:
            repo_map: словарь {пакет: [зависимости]}.
        """
        self._repo = repo_map

    def get_deps(self, name: str) -> list:
        """Вернуть прямые зависимости пакета.

        Args:
            name: имя пакета.

        Returns:
            Список зависимостей или пустой список.
        """
        return list(self._repo.get(name, []))

    def has_package(self, name: str) -> bool:
        """Проверить наличие пакета в репозитории."""
        return name in self._repo

    def all_packages(self) -> list:
        """Вернуть все пакеты тестового репозитория.

        Returns:
            Список всех имён пакетов в репозитории.
        """
        return list(self._repo.keys())


class UrlProvider:
    """Поставщик зависимостей по URL репозитория.

    Получает прямые зависимости корневого пакета по URL.
    Транзитивные зависимости не разрешаются: для разрешения
    имён пакетов в URL требуется реестр (запрещён методичкой).
    """

    def __init__(self, config: AppConfig):
        """Инициализировать поставщик конфигурацией.

        Args:
            config: конфигурация приложения.
        """
        self._config = config
        self._root_deps = None

    def get_deps(self, name: str) -> list:
        """Вернуть прямые зависимости пакета.

        Args:
            name: имя пакета.

        Returns:
            Список зависимостей корневого пакета; пустой
            список для остальных пакетов.

        Raises:
            RuntimeError: при ошибке получения Cargo.toml.
        """
        if name != self._config.package:
            return []
        if self._root_deps is None:
            toml = get_cargo_toml(self._config)
            self._root_deps = parse_dependencies(toml)
        return list(self._root_deps)

    def has_package(self, name: str) -> bool:
        """Корневой пакет всегда доступен по URL."""
        return name == self._config.package

    def all_packages(self) -> list:
        """Вернуть корневой пакет и его прямые зависимости.

        Returns:
            Список с корневым пакетом и его зависимостями.
        """
        deps = self.get_deps(self._config.package)
        return [self._config.package] + deps


def make_provider(config: AppConfig):
    """Создать поставщика зависимостей по конфигурации.

    Args:
        config: конфигурация приложения.

    Returns:
        Объект-поставщик (TestRepoProvider или UrlProvider).

    Raises:
        RuntimeError: при ошибке чтения тестового репозитория.
    """
    if config.test_mode:
        text = read_file(config.repo)
        repo_map = parse_test_repo(text)
        return TestRepoProvider(repo_map)
    return UrlProvider(config)


def build_graph_bfs(config: AppConfig, provider) -> dict:
    """Построить граф зависимостей алгоритмом BFS без рекурсии.

    Обход начинается с корневого пакета на глубине 0. Для каждого
    пакета запрашиваются прямые зависимости, которые добавляются
    в очередь с увеличением глубины. Циклы обрабатываются через
    множество посещённых узлов.

    Args:
        config: конфигурация приложения.
        provider: поставщик зависимостей.

    Returns:
        Словарь {пакет: [зависимости]} для всех достижимых пакетов.
    """
    graph = {}
    visited = set()
    queue = deque()
    queue.append((config.package, ROOT_DEPTH))
    while queue:
        node, depth = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        deps = provider.get_deps(node)
        graph[node] = list(deps)
        if depth < config.max_depth:
            _enqueue_children(deps, depth, queue, visited)
    return graph


def _enqueue_children(deps, depth, queue, visited):
    """Добавить непосещённых детей в очередь BFS.

    Args:
        deps: список зависимостей текущего пакета.
        depth: глубина текущего пакета.
        queue: очередь BFS.
        visited: множество посещённых узлов.
    """
    for dep in deps:
        if dep not in visited:
            queue.append((dep, depth + 1))


def get_graph(config: AppConfig) -> dict:
    """Построить граф зависимостей по конфигурации.

    Args:
        config: конфигурация приложения.

    Returns:
        Словарь {пакет: [зависимости]}.

    Raises:
        RuntimeError: при ошибке получения данных.
        ValueError: если корневой пакет не найден.
    """
    provider = make_provider(config)
    if not provider.has_package(config.package):
        raise ValueError(
            f"пакет {config.package!r} не найден в репозитории"
        )
    return build_graph_bfs(config, provider)


def format_graph(graph: dict, root: str) -> str:
    """Отформатировать граф для вывода на экран.

    Args:
        graph: словарь {пакет: [зависимости]}.
        root: корневой пакет.

    Returns:
        Строка с описанием графа, по одной строке на пакет.
    """
    lines = [f"Граф зависимостей (корень: {root}):"]
    for node in sorted(graph):
        deps = graph[node]
        if deps:
            lines.append(f"  {node} -> {', '.join(deps)}")
        else:
            lines.append(f"  {node} -> (нет зависимостей)")
    return "\n".join(lines)


def get_full_graph(config: AppConfig) -> dict:
    """Построить полный граф всех пакетов репозитория.

    В отличие от get_graph, возвращает все пакеты репозитория,
    а не только достижимые из корневого. Используется для
    анализа обратных зависимостей.

    Args:
        config: конфигурация приложения.

    Returns:
        Словарь {пакет: [зависимости]} для всех пакетов.

    Raises:
        RuntimeError: при ошибке получения данных.
        ValueError: если корневой пакет не найден.
    """
    provider = make_provider(config)
    if not provider.has_package(config.package):
        raise ValueError(
            f"пакет {config.package!r} не найден в репозитории"
        )
    graph = {}
    for name in provider.all_packages():
        graph[name] = provider.get_deps(name)
    return graph