"""Тесты модуля конфигурации (этап 1).

Проверяются разбор аргументов, валидация всех параметров
и форматирование конфигурации в виде ключ-значение.
"""

import os
import tempfile
import unittest

from src.config import (
    MAX_DEPTH_DEFAULT,
    MAX_DEPTH_MAX,
    MAX_DEPTH_MIN,
    OUTPUT_DEFAULT,
    format_config,
    parse_args,
    validate_max_depth,
    validate_output,
    validate_package,
    validate_repo,
)


class TestValidatePackage(unittest.TestCase):
    """Тесты функции validate_package."""

    def test_valid_name(self):
        """Корректное имя пакета проходит проверку."""
        self.assertEqual(validate_package("serde"), "serde")

    def test_valid_name_with_dash(self):
        """Имя с дефисом проходит проверку."""
        self.assertEqual(validate_package("tokio-util"), "tokio-util")

    def test_empty_name_raises(self):
        """Пустое имя вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_package("")

    def test_name_starting_with_digit_raises(self):
        """Имя, начинающееся с цифры, вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_package("1serde")

    def test_name_with_spaces_raises(self):
        """Имя с пробелами вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_package("ser de")


class TestValidateOutput(unittest.TestCase):
    """Тесты функции validate_output."""

    def test_valid_filename(self):
        """Корректное имя файла проходит проверку."""
        self.assertEqual(validate_output("graph.png"), "graph.png")

    def test_empty_filename_raises(self):
        """Пустое имя файла вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_output("")

    def test_filename_with_slash_raises(self):
        """Имя файла со слешом вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_output("dir/graph.png")


class TestValidateRepo(unittest.TestCase):
    """Тесты функции validate_repo."""

    def test_valid_url(self):
        """URL проходит проверку без тестового режима."""
        result = validate_repo("https://example.com/repo", False)
        self.assertEqual(result, "https://example.com/repo")

    def test_empty_repo_raises(self):
        """Пустой URL вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_repo("", False)

    def test_test_mode_missing_file_raises(self):
        """Несуществующий файл в тестовом режиме вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_repo("/nonexistent/file.txt", True)

    def test_test_mode_existing_file(self):
        """Существующий файл в тестовом режиме проходит проверку."""
        with tempfile.NamedTemporaryFile() as tmp:
            result = validate_repo(tmp.name, True)
            self.assertEqual(result, tmp.name)


class TestValidateMaxDepth(unittest.TestCase):
    """Тесты функции validate_max_depth."""

    def test_valid_depth(self):
        """Корректное значение глубины проходит проверку."""
        self.assertEqual(validate_max_depth("5"), 5)

    def test_non_integer_raises(self):
        """Нечисловое значение вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_max_depth("abc")

    def test_too_small_raises(self):
        """Значение ниже минимума вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_max_depth(str(MAX_DEPTH_MIN - 1))

    def test_too_large_raises(self):
        """Значение выше максимума вызывает ValueError."""
        with self.assertRaises(ValueError):
            validate_max_depth(str(MAX_DEPTH_MAX + 1))


class TestParseArgs(unittest.TestCase):
    """Тесты функции parse_args."""

    def test_default_values(self):
        """Параметры по умолчанию корректны."""
        config = parse_args(["-p", "serde", "-r", "https://x"])
        self.assertEqual(config.package, "serde")
        self.assertFalse(config.test_mode)
        self.assertEqual(config.output, OUTPUT_DEFAULT)
        self.assertEqual(config.max_depth, MAX_DEPTH_DEFAULT)

    def test_all_values(self):
        """Все параметры задаются корректно."""
        config = parse_args(
            [
                "-p", "tokio",
                "-r", "https://example.com",
                "-o", "my.png",
                "-d", "3",
            ]
        )
        self.assertEqual(config.package, "tokio")
        self.assertEqual(config.output, "my.png")
        self.assertEqual(config.max_depth, 3)

    def test_test_mode_flag(self):
        """Флаг тестового режима устанавливается."""
        with tempfile.NamedTemporaryFile() as tmp:
            config = parse_args(["-p", "A", "-r", tmp.name, "-t"])
            self.assertTrue(config.test_mode)


class TestFormatConfig(unittest.TestCase):
    """Тесты функции format_config."""

    def test_contains_all_keys(self):
        """Вывод содержит все параметры в формате ключ=значение."""
        config = parse_args(["-p", "serde", "-r", "https://x"])
        result = format_config(config)
        self.assertIn("package=serde", result)
        self.assertIn("repo=https://x", result)
        self.assertIn("test_mode=False", result)
        self.assertIn(f"output={OUTPUT_DEFAULT}", result)
        self.assertIn(f"max_depth={MAX_DEPTH_DEFAULT}", result)


if __name__ == "__main__":
    unittest.main()