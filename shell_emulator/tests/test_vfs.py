"""Тесты виртуальной файловой системы."""
import unittest
import tempfile
import os
import shutil
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), '..')
)
from src.vfs import VFS


class TestVFS(unittest.TestCase):
    """Набор тестов для VFS."""

    def setUp(self):
        """Создание тестовой структуры директорий."""
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, 'dir1'))
        with open(
            os.path.join(self.tmp, 'file1.txt'), 'w'
        ) as f:
            f.write('hello')
        with open(
            os.path.join(self.tmp, 'dir1', 'file2.txt'),
            'w'
        ) as f:
            f.write('world')

    def tearDown(self):
        """Удаление тестовой структуры."""
        shutil.rmtree(self.tmp)

    def test_load(self):
        """Тест успешной загрузки VFS."""
        vfs = VFS()
        vfs.load(self.tmp)
        self.assertIsNotNone(vfs.root)
        self.assertIsNotNone(vfs.cwd)

    def test_list(self):
        """Тест получения списка файлов."""
        vfs = VFS()
        vfs.load(self.tmp)
        items = vfs.list_dir()
        self.assertIn('dir1', items)
        self.assertIn('file1.txt', items)

    def test_cd(self):
        """Тест смены директории."""
        vfs = VFS()
        vfs.load(self.tmp)
        vfs.change_dir('dir1')
        items = vfs.list_dir()
        self.assertIn('file2.txt', items)

    def test_cd_back(self):
        """Тест возврата в родительскую директорию."""
        vfs = VFS()
        vfs.load(self.tmp)
        vfs.change_dir('dir1')
        vfs.change_dir('..')
        items = vfs.list_dir()
        self.assertIn('dir1', items)
        self.assertIn('file1.txt', items)

    def test_not_found(self):
        """Тест ошибки при несуществующем пути."""
        vfs = VFS()
        with self.assertRaises(FileNotFoundError):
            vfs.load('/nonexistent/path/xyz')

    def test_empty_path(self):
        """Тест ошибки при пустом пути."""
        vfs = VFS()
        with self.assertRaises(ValueError):
            vfs.load('')

    def test_cd_nonexistent(self):
        """Тест ошибки при переходе в несуществующую
        директорию."""
        vfs = VFS()
        vfs.load(self.tmp)
        with self.assertRaises(FileNotFoundError):
            vfs.change_dir('nonexistent')


if __name__ == '__main__':
    unittest.main()