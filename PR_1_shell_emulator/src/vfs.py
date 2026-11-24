"""Модуль виртуальной файловой системы."""
import os


class VFSNode:
    """Узел виртуальной файловой системы."""

    def __init__(self, name, is_dir, content=None):
        """Инициализация узла VFS."""
        self.name = name
        self.is_dir = is_dir
        self.content = content or b''
        self.children = {}


class VFS:
    """Виртуальная файловая система на основе директории."""

    def __init__(self):
        """Инициализация VFS."""
        self.root = None
        self.cwd = None
        self.path = None

    def load(self, path):
        """Загружает VFS из директории на диске.

        Raises:
            ValueError: если путь не указан или не директория.
            FileNotFoundError: если путь не существует.
        """
        if not path:
            raise ValueError("Путь не указан")
        if not os.path.exists(path):
            raise FileNotFoundError(f"VFS не найдена: {path}")
        if not os.path.isdir(path):
            raise ValueError(f"Не директория: {path}")
        self.path = path
        name = os.path.basename(path) or path
        self.root = self._build_tree(path, name)
        self.cwd = self.root

    def _build_tree(self, path, name):
        """Рекурсивно строит дерево VFS в памяти."""
        node = VFSNode(name, True)
        try:
            for entry in os.listdir(path):
                full = os.path.join(path, entry)
                if os.path.isdir(full):
                    child = self._build_tree(full, entry)
                else:
                    with open(full, 'rb') as f:
                        content = f.read()
                    child = VFSNode(entry, False, content)
                node.children[entry] = child
        except OSError as e:
            raise OSError(f"Ошибка чтения: {e}")
        return node

    def list_dir(self, node=None):
        """Возвращает список имён в директории."""
        node = node or self.cwd
        if not node.is_dir:
            raise ValueError("Не директория")
        return list(node.children.keys())

    def change_dir(self, path_arg):
        """Меняет текущую рабочую директорию."""
        if not path_arg:
            raise ValueError("Не указан путь")
        target = self._resolve(path_arg)
        if target is None:
            raise FileNotFoundError(
                f"Путь не найден: {path_arg}"
            )
        if not target.is_dir:
            raise ValueError("Не директория")
        self.cwd = target

    def _resolve(self, path_arg):
        """Разрешает путь относительно cwd."""
        if path_arg == '/':
            return self.root
        parts = self._split_path(path_arg)
        node = self.cwd
        for part in parts:
            if part == '' or part == '.':
                continue
            if part == '..':
                node = self._parent(node)
                continue
            if part not in node.children:
                return None
            node = node.children[part]
        return node

    def _split_path(self, path_arg):
        """Разделяет путь на компоненты."""
        if '/' in path_arg:
            return path_arg.split('/')
        return [path_arg]

    def _parent(self, node):
        """Находит родителя узла."""
        if node is self.root:
            return self.root
        return self._find_parent(self.root, node)

    def _find_parent(self, current, target):
        """Рекурсивно ищет родителя узла."""
        for child in current.children.values():
            if child is target:
                return current
            if child.is_dir:
                result = self._find_parent(child, target)
                if result is not None:
                    return result
        return None
