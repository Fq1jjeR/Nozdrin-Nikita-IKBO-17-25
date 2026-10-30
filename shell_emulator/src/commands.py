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
        """Команда ls — вывод содержимого директории."""
        vfs = self.app.vfs
        if vfs is None or vfs.root is None:
            return "ls: VFS не загружена"
        try:
            if args:
                target = vfs._resolve(args[0])
                items = vfs.list_dir(target)
            else:
                items = vfs.list_dir()
            return ' '.join(items)
        except (ValueError, FileNotFoundError) as e:
            return f"ls: {e}"

    def _cmd_cd(self, args):
        """Команда cd — смена текущей директории."""
        vfs = self.app.vfs
        if vfs is None or vfs.root is None:
            return "cd: VFS не загружена"
        if not args:
            return "cd: не указан путь"
        try:
            vfs.change_dir(args[0])
            return None
        except (ValueError, FileNotFoundError) as e:
            return f"cd: {e}"

    def _cmd_exit(self, args):
        """Команда выхода из эмулятора."""
        if args:
            return "Ошибка: exit не принимает аргументов"
        self.app.quit()
        return None
