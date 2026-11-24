"""Анализ обратных зависимостей в графе.

Этап 4: обратные зависимости — пакеты, которые зависят от
заданного пакета (прямо или транзитивно). Используется алгоритм
BFS без рекурсии на обращённом графе, как и на этапе 3.
"""

from collections import deque

from .config import AppConfig
from .graph import get_full_graph


def build_reverse_graph(graph: dict) -> dict:
    """Построить обращённый граф зависимостей.

    Для каждого ребра A -> B в исходном графе создаётся
    ребро B -> A в обращённом.

    Args:
        graph: прямой граф {пакет: [зависимости]}.

    Returns:
        Обращённый граф {пакет: [кто от него зависит]}.
    """
    reverse = {node: [] for node in graph}
    for node, deps in graph.items():
        for dep in deps:
            _add_reverse_edge(reverse, node, dep)
    return reverse


def _add_reverse_edge(reverse: dict, node: str, dep: str):
    """Добавить обратное ребро dep -> node.

    Args:
        reverse: словарь обращённого графа.
        node: пакет, от которого зависит dep.
        dep: зависимый пакет.
    """
    if dep in reverse:
        reverse[dep].append(node)
    else:
        reverse[dep] = [node]


def find_reverse_deps(graph: dict, target: str) -> list:
    """Найти обратные зависимости пакета BFS без рекурсии.

    Обход обращённого графа от целевого пакета. Возвращает все
    пакеты, которые зависят от target прямо или транзитивно.

    Args:
        graph: прямой граф {пакет: [зависимости]}.
        target: целевой пакет.

    Returns:
        Отсортированный список пакетов, зависящих от target.
        Сам target в список не входит.
    """
    reverse = build_reverse_graph(graph)
    visited = {target}
    queue = deque([target])
    while queue:
        node = queue.popleft()
        for parent in reverse.get(node, []):
            if parent not in visited:
                visited.add(parent)
                queue.append(parent)
    visited.discard(target)
    return sorted(visited)


def get_reverse_dependencies(config: AppConfig) -> list:
    """Получить обратные зависимости пакета по конфигурации.

    Строит полный граф репозитория и находит все пакеты,
    зависящие от config.package, алгоритмом BFS без рекурсии.

    Args:
        config: конфигурация приложения.

    Returns:
        Список пакетов, зависящих от config.package.

    Raises:
        RuntimeError: при ошибке построения графа.
        ValueError: если пакет не найден.
    """
    graph = get_full_graph(config)
    return find_reverse_deps(graph, config.package)


def format_reverse_deps(deps: list, target: str) -> str:
    """Отформатировать обратные зависимости для вывода.

    Args:
        deps: список обратных зависимостей.
        target: целевой пакет.

    Returns:
        Строка с описанием обратных зависимостей.
    """
    lines = [f"Обратные зависимости пакета {target}:"]
    if not deps:
        lines.append("  (нет обратных зависимостей)")
        return "\n".join(lines)
    for dep in deps:
        lines.append(f"  - {dep}")
    return "\n".join(lines)