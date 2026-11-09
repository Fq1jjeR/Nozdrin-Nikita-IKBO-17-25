"""Тесты модуля visualizer (этап 5).

Проверяются формирование описания графа на языке DOT и
генерация PNG-изображения через утилиту dot.
"""

import os
import tempfile
import unittest

from src.visualizer import render_png, to_dot


SIMPLE_GRAPH = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}


class TestToDot(unittest.TestCase):
    """Тесты функции to_dot."""

    def test_contains_digraph_header(self):
        """DOT содержит заголовок digraph."""
        dot = to_dot(SIMPLE_GRAPH, "A")
        self.assertIn("digraph dependencies {", dot)

    def test_contains_edges(self):
        """DOT содержит все рёбра графа."""
        dot = to_dot(SIMPLE_GRAPH, "A")
        self.assertIn('"A" -> "B";', dot)
        self.assertIn('"A" -> "C";', dot)
        self.assertIn('"B" -> "D";', dot)

    def test_root_highlighted(self):
        """Корневой пакет выделен цветом."""
        dot = to_dot(SIMPLE_GRAPH, "A")
        self.assertIn('"A" [style=filled', dot)

    def test_empty_graph(self):
        """Пустой граф корректно оформляется."""
        dot = to_dot({}, "X")
        self.assertIn("digraph dependencies {", dot)
        self.assertIn("}", dot)

    def test_cycle_in_dot(self):
        """Циклический граф корректно представляется в DOT."""
        cycle = {"A": ["B"], "B": ["A"]}
        dot = to_dot(cycle, "A")
        self.assertIn('"A" -> "B";', dot)
        self.assertIn('"B" -> "A";', dot)


class TestRenderPng(unittest.TestCase):
    """Тесты функции render_png."""

    def test_renders_valid_png(self):
        """Корректный DOT рендерится в PNG-файл."""
        dot = to_dot(SIMPLE_GRAPH, "A")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.png")
            ok = render_png(dot, path)
            if not ok:
                self.skipTest("утилита dot недоступна")
            self.assertTrue(os.path.isfile(path))
            self.assertGreater(os.path.getsize(path), 0)

    def test_invalid_dot_returns_false(self):
        """Некорректный DOT не рендерится."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.png")
            ok = render_png("not valid dot {{{", path)
            self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()