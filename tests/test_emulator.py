"""Модульные тесты для эмулятора оболочки UNIX (Вариант №23)."""

import os
import unittest
from src.parser import expand_env_vars, parse_line
from src.vfs import VirtualFileSystem


class TestParser(unittest.TestCase):
    """Тестирование разбора команд и переменных окружения."""

    def test_parse_simple_command(self):
        """Проверка разбора команды без аргументов."""
        cmd, args = parse_line("ls")
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, [])

    def test_parse_command_with_arguments(self):
        """Проверка разбора команды с несколькими аргументами."""
        cmd, args = parse_line("echo hello world 123")
        self.assertEqual(cmd, "echo")
        self.assertEqual(args, ["hello", "world", "123"])

    def test_env_variable_expansion(self):
        """Проверка раскрытия переменной окружения."""
        os.environ["TEST_USER_VAR"] = "student"
        result = expand_env_vars("echo $TEST_USER_VAR")
        self.assertEqual(result, "echo student")

    def test_empty_input(self):
        """Проверка обработки пустой строки."""
        cmd, args = parse_line("   ")
        self.assertEqual(cmd, "")
        self.assertEqual(args, [])


class TestVFS(unittest.TestCase):
    """Тестирование виртуальной файловой системы в памяти."""

    def setUp(self):
        """Создание чистого экземпляра VFS перед каждым тестом."""
        self.vfs = VirtualFileSystem()

    def test_root_directory_exists(self):
        """Корневой каталог должен существовать всегда."""
        self.assertTrue(self.vfs.dir_exists("/"))

    def test_touch_creates_file_in_memory(self):
        """Проверка создания пустого файла в памяти."""
        self.vfs.create_empty_file("/test.txt")
        self.assertTrue(self.vfs.file_exists("/test.txt"))
        self.assertEqual(self.vfs.files["/test.txt"], b"")

    def test_file_not_found(self):
        """Проверка запроса несуществующего файла."""
        self.assertFalse(self.vfs.file_exists("/unknown.txt"))


if __name__ == "__main__":
    unittest.main()