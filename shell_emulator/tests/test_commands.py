"""Тесты команд эмулятора."""
import unittest
import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), '..')
)
from src.commands import CommandHandler


class MockApp:
    """Мок приложения для тестов."""

    def __init__(self):
        """Инициализация мока."""
        self.vfs = None
        self.quit_called = False

    def quit(self):
        """Мок выхода из приложения."""
        self.quit_called = True


class TestCommands(unittest.TestCase):
    """Набор тестов для команд."""

    def test_unknown(self):
        """Тест неизвестной команды."""
        app = MockApp()
        handler = CommandHandler(app)
        result = handler.execute('unknown', [])
        self.assertIn('неизвестная команда', result)

    def test_exit(self):
        """Тест команды exit."""
        app = MockApp()
        handler = CommandHandler(app)
        handler.execute('exit', [])
        self.assertTrue(app.quit_called)

    def test_exit_with_args(self):
        """Тест exit с аргументами."""
        app = MockApp()
        handler = CommandHandler(app)
        result = handler.execute('exit', ['arg'])
        self.assertIn('не принимает', result)

    def test_ls_no_vfs(self):
        """Тест ls без загруженной VFS."""
        app = MockApp()
        handler = CommandHandler(app)
        result = handler.execute('ls', [])
        self.assertIn('не загружена', result)

    def test_cd_no_vfs(self):
        """Тест cd без загруженной VFS."""
        app = MockApp()
        handler = CommandHandler(app)
        result = handler.execute('cd', ['dir'])
        self.assertIn('не загружена', result)

    def test_cd_no_args(self):
        """Тест cd без аргументов."""
        app = MockApp()
        app.vfs = type('MockVFS', (), {
            'root': type('MockRoot', (), {'is_dir': True})(),
            'cwd': type('MockCwd', (), {'is_dir': True})()
        })()
        handler = CommandHandler(app)
        result = handler.execute('cd', [])
        self.assertIn('не указан', result)


if __name__ == '__main__':
    unittest.main()