"""Главный модуль приложения."""
import sys
from PyQt6.QtWidgets import QApplication
from app import EmulatorWindow


def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    window = EmulatorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()