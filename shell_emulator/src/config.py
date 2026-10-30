"""Модуль конфигурации эмулятора."""


class Config:
    """Класс конфигурации эмулятора."""

    def __init__(self):
        """Инициализация конфигурации."""
        self.vfs_path = None
        self.script_path = None

    def load_from_args(self, args):
        """Загрузка параметров из аргументов CLI."""
        if args.vfs:
            self.vfs_path = args.vfs
        if args.script:
            self.script_path = args.script

    def dump(self):
        """Вывод параметров в формате ключ-значение."""
        lines = [
            f"vfs_path: {self.vfs_path}",
            f"script_path: {self.script_path}",
        ]
        return '\n'.join(lines)
