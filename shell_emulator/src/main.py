"""Главный модуль приложения."""
import sys
import argparse
from PyQt6.QtWidgets import QApplication
from .app import EmulatorWindow
from .config import Config
from .script_runner import ScriptRunner


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description='Эмулятор оболочки ОС'
    )
    parser.add_argument('--vfs', help='Путь к VFS')
    parser.add_argument(
        '--script', help='Путь к стартовому скрипту'
    )
    return parser.parse_args()


def main():
    """Точка входа в приложение."""
    args = parse_args()
    config = Config()
    config.load_from_args(args)

    app = QApplication(sys.argv)
    window = EmulatorWindow()
    window.config = config
    window.append_text(config.dump())

    runner = ScriptRunner(window)
    runner.run(config.script_path)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()