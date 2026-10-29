"""Модуль GUI приложения на PyQt6."""
import os
import socket
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QLineEdit, QLabel, QHBoxLayout
)
from PyQt6.QtGui import QFont
from .parser import parse_command
from .commands import CommandHandler
from .vfs import VFS


class EmulatorWindow(QMainWindow):
    """Главное окно эмулятора."""

    def __init__(self):
        """Инициализация окна."""
        super().__init__()
        self.config = None
        self.vfs = VFS()
        self._setup_window()
        self._setup_ui()
        self.handler = CommandHandler(self)

    def _setup_window(self):
        """Настройка заголовка и размеров окна."""
        username = os.getlogin()
        hostname = socket.gethostname()
        title = f"Эмулятор-[{username}@{hostname}]"
        self.setWindowTitle(title)
        self.resize(800, 600)

    def _setup_ui(self):
        """Настройка пользовательского интерфейса."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        layout.addWidget(self.output)

        input_layout = QHBoxLayout()
        self.prompt = QLabel("$")
        self.prompt.setFont(QFont("Consolas", 10))
        input_layout.addWidget(self.prompt)

        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Consolas", 10))
        self.input_field.returnPressed.connect(
            self._on_enter
        )
        input_layout.addWidget(self.input_field)

        layout.addLayout(input_layout)
        self.input_field.setFocus()

    def _on_enter(self):
        """Обработка нажатия Enter."""
        text = self.input_field.text()
        self.input_field.clear()
        self._process_input(text)

    def _process_input(self, text):
        """Обрабатывает ввод пользователя."""
        self.output.append(f"$ {text}")
        command, args = parse_command(text)
        if command is None:
            return
        result = self.handler.execute(command, args)
        if result is not None:
            self.output.append(result)

    def append_text(self, text):
        """Добавляет текст в область вывода."""
        self.output.append(text)

    def process_command(self, text):
        """Обрабатывает команду из скрипта."""
        self._process_input(text)

    def quit(self):
        """Завершение работы приложения."""
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()