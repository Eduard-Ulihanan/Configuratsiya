"""Виртуальная файловая система (VFS) в памяти."""

import zipfile
from typing import Dict, List, Optional, Set


class VirtualFileSystem:
    """Файловая система в оперативной памяти."""

    def __init__(self, zip_path: Optional[str] = None):
        self.files: Dict[str, bytes] = {}
        self.directories: Set[str] = {"/"}
        if zip_path:
            self._load_from_zip(zip_path)

    def _load_from_zip(self, zip_path: str) -> None:
        """Загрузка файлов из ZIP-архива в ОЗУ."""
        with zipfile.ZipFile(zip_path, "r") as archive:
            for item in archive.infolist():
                norm_name = "/" + item.filename.rstrip("/")
                if item.is_dir():
                    self.directories.add(norm_name)
                else:
                    self.files[norm_name] = archive.read(item.filename)
                    parts = [p for p in item.filename.split("/")[:-1] if p]
                    parent = "/" + "/".join(parts) if parts else "/"
                    self.directories.add(parent)

    def file_exists(self, path: str) -> bool:
        """Существует ли файл."""
        return path in self.files

    def dir_exists(self, path: str) -> bool:
        """Существует ли директория."""
        return path in self.directories

    def list_dir(self, path: str) -> List[str]:
        """Получить содержимое директории."""
        target = path.rstrip("/")
        prefix = target + "/" if target != "/" else "/"
        results: Set[str] = set()

        for directory in self.directories:
            if directory.startswith(prefix) and directory != target:
                item_name = directory[len(prefix):].split("/")[0]
                if item_name:
                    results.add(item_name)

        for filename in self.files:
            if filename.startswith(prefix):
                item_name = filename[len(prefix):].split("/")[0]
                if item_name:
                    results.add(item_name)

        return sorted(list(results))

    def create_empty_file(self, path: str) -> None:
        """Создание пустого файла для команды touch в памяти."""
        if path not in self.files:
            self.files[path] = b""