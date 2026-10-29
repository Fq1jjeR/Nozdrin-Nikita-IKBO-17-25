"""Модуль запуска стартового скрипта."""
import os


class ScriptRunner:
    """Запуск стартового скрипта эмулятора."""

    def __init__(self, app):
        """Инициализация раннера скриптов."""
        self.app = app

    def run(self, path):
        """Запускает скрипт по указанному пути."""
        if not path:
            return
        if not os.path.exists(path):
            self.app.append_text(
                f"Ошибка: скрипт '{path}' не найден"
            )
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    self._process_line(line)
        except OSError as e:
            self.app.append_text(f"Ошибка чтения: {e}")

    def _process_line(self, line):
        """Обрабатывает одну строку скрипта."""
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            return
        self.app.append_text(f"$ {stripped}")
        self.app.process_command(stripped)