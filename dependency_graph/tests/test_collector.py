"""Тесты модуля collector (этап 2).

Проверяются разбор Cargo.toml, извлечение прямых зависимостей
и построение URL-кандидатов для GitHub.
"""

import os
import unittest

from src.collector import (
    github_raw_candidates,
    parse_dependencies,
)


SAMPLE_CARGO_TOML = """\
[package]
name = "sample"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
rand = "0.8"

[dev-dependencies]
criterion = "0.4"
"""


class TestParseDependencies(unittest.TestCase):
    """Тесты функции parse_dependencies."""

    def test_extracts_dependencies(self):
        """Извлекаются имена из секции [dependencies]."""
        deps = parse_dependencies(SAMPLE_CARGO_TOML)
        self.assertEqual(deps, ["serde", "tokio", "rand"])

    def test_ignores_dev_dependencies(self):
        """Секция [dev-dependencies] игнорируется."""
        deps = parse_dependencies(SAMPLE_CARGO_TOML)
        self.assertNotIn("criterion", deps)

    def test_empty_dependencies(self):
        """Пустая секция [dependencies] даёт пустой список."""
        toml = "[package]\nname = \"x\"\n\n[dependencies]\n"
        self.assertEqual(parse_dependencies(toml), [])

    def test_no_dependencies_section(self):
        """Отсутствие секции даёт пустой список."""
        toml = "[package]\nname = \"x\"\n"
        self.assertEqual(parse_dependencies(toml), [])

    def test_ignores_comments(self):
        """Комментарии в секции игнорируются."""
        toml = (
            "[dependencies]\n"
            "# это комментарий\n"
            "serde = \"1.0\"\n"
        )
        self.assertEqual(parse_dependencies(toml), ["serde"])

    def test_inline_tables_format(self):
        """Inline-таблицы [dependencies.name] распознаются."""
        toml = (
            "[dependencies.aho-corasick]\n"
            "version = \"1.0\"\n"
            "[dependencies.memchr]\n"
            "version = \"2.0\"\n"
        )
        deps = parse_dependencies(toml)
        self.assertEqual(deps, ["aho-corasick", "memchr"])

    def test_mixed_format(self):
        """Смешанный формат: секция и inline-таблицы."""
        toml = (
            "[dependencies]\n"
            "serde = \"1.0\"\n"
            "[dependencies.tokio]\n"
            "version = \"1.0\"\n"
        )
        deps = parse_dependencies(toml)
        self.assertEqual(deps, ["serde", "tokio"])


class TestGithubRawCandidates(unittest.TestCase):
    """Тесты функции github_raw_candidates."""

    def test_github_url_main_master(self):
        """GitHub-URL даёт кандидатов для main и master."""
        url = "https://github.com/serde-rs/serde"
        candidates = github_raw_candidates(url)
        self.assertEqual(len(candidates), 2)
        self.assertIn("main/Cargo.toml", candidates[0])
        self.assertIn("master/Cargo.toml", candidates[1])

    def test_github_url_with_trailing_slash(self):
        """GitHub-URL с завершающим слешем корректно разбирается."""
        url = "https://github.com/owner/repo/"
        candidates = github_raw_candidates(url)
        self.assertEqual(len(candidates), 2)

    def test_non_github_url_returns_empty(self):
        """Не-GitHub URL даёт пустой список кандидатов."""
        url = "https://gitlab.com/owner/repo"
        self.assertEqual(github_raw_candidates(url), [])


class TestEndToEndFile(unittest.TestCase):
    """Сквозные тесты чтения файла Cargo.toml."""

    def test_sample_cargo_toml(self):
        """Файл examples/sample_cargo.toml разбирается корректно."""
        base = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(
            base, "examples", "sample_cargo.toml"
        )
        with open(path, encoding="utf-8") as handle:
            content = handle.read()
        deps = parse_dependencies(content)
        self.assertEqual(
            deps, ["serde", "tokio", "rand", "clap"]
        )


if __name__ == "__main__":
    unittest.main()