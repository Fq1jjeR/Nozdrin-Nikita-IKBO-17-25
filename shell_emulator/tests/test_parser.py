"""Тесты парсера команд."""
import unittest
import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), '..')
)
from src.parser import parse_command


class TestParser(unittest.TestCase):
    """Набор тестов для парсера."""

    def test_empty(self):
        """Тест пустого ввода."""
        cmd, args = parse_command('')
        self.assertIsNone(cmd)
        self.assertEqual(args, [])

    def test_spaces_only(self):
        """Тест ввода из одних пробелов."""
        cmd, args = parse_command('   ')
        self.assertIsNone(cmd)
        self.assertEqual(args, [])

    def test_simple(self):
        """Тест простой команды без аргументов."""
        cmd, args = parse_command('ls')
        self.assertEqual(cmd, 'ls')
        self.assertEqual(args, [])

    def test_with_args(self):
        """Тест команды с аргументами."""
        cmd, args = parse_command('cd dir1')
        self.assertEqual(cmd, 'cd')
        self.assertEqual(args, ['dir1'])

    def test_whitespace(self):
        """Тест обработки лишних пробелов."""
        cmd, args = parse_command('  ls   a  b  ')
        self.assertEqual(cmd, 'ls')
        self.assertEqual(args, ['a', 'b'])

    def test_exit(self):
        """Тест команды exit."""
        cmd, args = parse_command('exit')
        self.assertEqual(cmd, 'exit')
        self.assertEqual(args, [])


if __name__ == '__main__':
    unittest.main()