"""Тесты модуля graph (этап 3).

Проверяются разбор тестового репозитория, построение графа BFS
без рекурсии, учёт максимальной глубины и обработка циклов.
"""

import unittest

from src.config import AppConfig
from src.graph import (
    build_graph_bfs,
    format_graph,
    parse_test_repo,
    TestRepoProvider,
)


LINEAR = "A: B\nB: C\nC: D\nD:\n"
CYCLE = "A: B\nB: C\nC: A\n"
DIAMOND = "A: B, C\nB: D\nC: D\nD:\n"
DEEP = "A: B\nB: C\nC: D\nD: E\nE: F\nF:\n"


def make_config(package, repo, max_depth=10, test_mode=True):
    """Создать конфигурацию для тестов."""
    return AppConfig(
        package=package,
        repo=repo,
        test_mode=test_mode,
        output="graph.png",
        max_depth=max_depth,
        mode="graph",
    )


class TestParseTestRepo(unittest.TestCase):
    """Тесты функции parse_test_repo."""

    def test_parse_linear(self):
        """Линейный граф разбирается корректно."""
        repo = parse_test_repo(LINEAR)
        self.assertEqual(repo["A"], ["B"])
        self.assertEqual(repo["D"], [])

    def test_ignores_comments(self):
        """Комментарии игнорируются."""
        text = "# comment\nA: B\n"
        self.assertEqual(parse_test_repo(text), {"A": ["B"]})

    def test_multiple_deps(self):
        """Несколько зависимостей разбираются."""
        repo = parse_test_repo(DIAMOND)
        self.assertEqual(repo["A"], ["B", "C"])

    def test_invalid_format_raises(self):
        """Некорректный формат вызывает ValueError."""
        with self.assertRaises(ValueError):
            parse_test_repo("A B C\n")


class TestBuildGraphBfs(unittest.TestCase):
    """Тесты функции build_graph_bfs."""

    def _build(self, text, package, max_depth=10):
        """Построить граф из текста тестового репозитория."""
        repo = parse_test_repo(text)
        provider = TestRepoProvider(repo)
        config = make_config(package, "fake", max_depth)
        return build_graph_bfs(config, provider)

    def test_linear_full(self):
        """Линейный граф проходится полностью."""
        graph = self._build(LINEAR, "A")
        self.assertEqual(set(graph), {"A", "B", "C", "D"})

    def test_cycle_handled(self):
        """Циклическая зависимость не вызывает зацикливание."""
        graph = self._build(CYCLE, "A")
        self.assertEqual(set(graph), {"A", "B", "C"})

    def test_diamond_no_duplicates(self):
        """Ромб: D достигается один раз."""
        graph = self._build(DIAMOND, "A")
        self.assertEqual(set(graph), {"A", "B", "C", "D"})
        self.assertEqual(graph["D"], [])

    def test_max_depth_limits(self):
        """max_depth ограничивает глубину обхода."""
        graph = self._build(DEEP, "A", max_depth=2)
        self.assertEqual(set(graph), {"A", "B", "C"})

    def test_max_depth_one(self):
        """max_depth=1 даёт только прямые зависимости."""
        graph = self._build(DIAMOND, "A", max_depth=1)
        self.assertEqual(set(graph), {"A", "B", "C"})

    def test_unreachable_not_included(self):
        """Недостижимые пакеты не попадают в граф."""
        text = "A: B\nB:\nC: A\n"
        graph = self._build(text, "A")
        self.assertNotIn("C", graph)


class TestFormatGraph(unittest.TestCase):
    """Тесты функции format_graph."""

    def test_contains_root(self):
        """Вывод содержит корневой пакет."""
        graph = {"A": ["B"], "B": []}
        result = format_graph(graph, "A")
        self.assertIn("корень: A", result)

    def test_empty_deps_shown(self):
        """Пакет без зависимостей помечается."""
        graph = {"A": []}
        result = format_graph(graph, "A")
        self.assertIn("нет зависимостей", result)


if __name__ == "__main__":
    unittest.main()