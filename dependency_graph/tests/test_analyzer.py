"""Тесты модуля analyzer (этап 4).

Проверяются построение обращённого графа и поиск обратных
зависимостей алгоритмом BFS без рекурсии.
"""

import unittest

from src.analyzer import (
    build_reverse_graph,
    find_reverse_deps,
    format_reverse_deps,
)


DIAMOND = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": [],
}
LINEAR = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}
BRANCH = {
    "A": ["B"],
    "B": ["C"],
    "X": ["B"],
    "Y": ["X"],
    "C": [],
}


class TestBuildReverseGraph(unittest.TestCase):
    """Тесты функции build_reverse_graph."""

    def test_simple_reverse(self):
        """Обращение линейного графа корректно."""
        rev = build_reverse_graph(LINEAR)
        self.assertEqual(rev["B"], ["A"])
        self.assertEqual(rev["C"], ["B"])
        self.assertEqual(rev["D"], ["C"])
        self.assertEqual(rev["A"], [])

    def test_diamond_reverse(self):
        """Ромб: D имеет двух родителей."""
        rev = build_reverse_graph(DIAMOND)
        self.assertEqual(set(rev["D"]), {"B", "C"})
        self.assertEqual(set(rev["B"]), {"A"})
        self.assertEqual(set(rev["C"]), {"A"})


class TestFindReverseDeps(unittest.TestCase):
    """Тесты функции find_reverse_deps."""

    def test_linear_leaf(self):
        """Обратные зависимости листа D: A, B, C."""
        result = find_reverse_deps(LINEAR, "D")
        self.assertEqual(result, ["A", "B", "C"])

    def test_diamond_leaf(self):
        """Обратные зависимости D в ромбе: A, B, C."""
        result = find_reverse_deps(DIAMOND, "D")
        self.assertEqual(result, ["A", "B", "C"])

    def test_middle_node(self):
        """Обратные зависимости B: A (прямо)."""
        result = find_reverse_deps(LINEAR, "B")
        self.assertEqual(result, ["A"])

    def test_root_no_reverse(self):
        """Корневой пакет не имеет обратных зависимостей."""
        result = find_reverse_deps(LINEAR, "A")
        self.assertEqual(result, [])

    def test_cycle_handled(self):
        """Цикл не вызывает зацикливание."""
        result = find_reverse_deps(CYCLE, "A")
        self.assertEqual(set(result), {"B", "C"})

    def test_branch_reverse(self):
        """Разветвлённый граф: обратные зависимости C."""
        result = find_reverse_deps(BRANCH, "C")
        self.assertEqual(set(result), {"A", "B", "X", "Y"})

    def test_target_excluded(self):
        """Сам целевой пакет не входит в результат."""
        result = find_reverse_deps(LINEAR, "C")
        self.assertNotIn("C", result)


class TestFormatReverseDeps(unittest.TestCase):
    """Тесты функции format_reverse_deps."""

    def test_with_deps(self):
        """Вывод со списком зависимостей."""
        result = format_reverse_deps(["A", "B"], "D")
        self.assertIn("Обратные зависимости пакета D:", result)
        self.assertIn("- A", result)
        self.assertIn("- B", result)

    def test_empty_deps(self):
        """Пустой список зависимостей."""
        result = format_reverse_deps([], "A")
        self.assertIn("нет обратных зависимостей", result)


if __name__ == "__main__":
    unittest.main()