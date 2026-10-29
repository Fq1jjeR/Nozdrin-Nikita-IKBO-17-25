"""Модуль команд эмулятора."""


class CommandHandler:
    """Обработчик команд эмулятора."""

    def __init__(self, app):
        """Инициализация обработчика."""
        self.app = app

    def execute(self, command, args):
        """Выполняет команду и возвращает результат."""
        handlers = {
            'ls': self._cmd_ls,
            'cd': self._cmd_cd,
            'exit': self._cmd_exit,
        }
        handler = handlers.get(command)
        if handler is None:
            return f"Ошибка: неизвестная команда '{command}'"
        return handler(args)

    def _cmd_ls(self, args):
        """Заглушка команды ls."""
        return f"ls: {args}"

    def _cmd_cd(self, args):
        """Заглушка команды cd."""
        if not args:
            return "Ошибка: cd требует аргумент"
        return f"cd: {args}"

    def _cmd_exit(self, args):
        """Команда выхода из эмулятора."""
        if args:
            return "Ошибка: exit не принимает аргументов"
        self.app.quit()
        return None