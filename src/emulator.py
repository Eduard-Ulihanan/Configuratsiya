"""Ядро командной оболочки эмулятора."""

import argparse
import getpass
import socket
import sys
from typing import Optional

from src.parser import parse_line
from src.vfs import VirtualFileSystem


class ShellEmulator:
    """Консольный эмулятор командной оболочки UNIX."""

    def __init__(
        self,
        vfs_path: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        script_path: Optional[str] = None,
    ):
        self.vfs_path = vfs_path
        self.custom_prompt = custom_prompt
        self.script_path = script_path
        self.vfs = VirtualFileSystem(vfs_path)
        self.cwd = "/"
        self.running = True

    def get_prompt(self) -> str:
        """Формирование строки приглашения к вводу."""
        if self.custom_prompt:
            return self.custom_prompt
        user = getpass.getuser()
        host = socket.gethostname()
        return f"{user}@{host}:{self.cwd}$ "

    def resolve_path(self, path: str) -> str:
        """Преобразование относительного пути VFS в абсолютный."""
        if path.startswith("/"):
            resolved = path
        else:
            resolved = (self.cwd.rstrip("/") + "/" + path)
        parts = [p for p in resolved.split("/") if p and p != "."]
        stack: list[str] = []
        for part in parts:
            if part == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(part)
        return "/" + "/".join(stack)

    def execute_command(self, cmd: str, args: list[str]) -> None:
        """Маршрутизация и выполнение команды эмулятора."""
        if not cmd:
            return
        if cmd == "exit":
            self.running = False
        elif cmd == "conf-dump":
            print(f"vfs_path: {self.vfs_path}")
            print(f"custom_prompt: {self.custom_prompt}")
            print(f"script_path: {self.script_path}")
        elif cmd == "echo":
            print(" ".join(args))
        elif cmd == "ls":
            target = self.resolve_path(args[0]) if args else self.cwd
            if self.vfs.dir_exists(target):
                items = self.vfs.list_dir(target)
                if items:
                    print("  ".join(items))
            else:
                print(f"ls: cannot access '{target}': No such directory")
        elif cmd == "cd":
            target = self.resolve_path(args[0]) if args else "/"
            if self.vfs.dir_exists(target):
                self.cwd = target
            else:
                print(f"cd: no such file or directory: {target}")
        elif cmd == "touch":
            if not args:
                print("touch: missing file operand")
                return
            target = self.resolve_path(args[0])
            self.vfs.create_empty_file(target)
        elif cmd == "wc":
            if not args:
                print("wc: missing file operand")
                return
            target = self.resolve_path(args[0])
            if self.vfs.file_exists(target):
                data = self.vfs.files[target]
                lines = len(data.split(b"\n")) - (
                    1 if data.endswith(b"\n") else 0
                )
                words = len(data.split())
                bytes_cnt = len(data)
                print(f" {lines}  {words} {bytes_cnt} {args[0]}")
            else:
                print(f"wc: {args[0]}: No such file or directory")
        else:
            print(f"{cmd}: command not found")

    def run_script(self, script_path: str) -> None:
        """Исполнение стартового скрипта с пропуском строк при ошибках."""
        try:
            with open(script_path, "r", encoding="utf-8") as script:
                for raw_line in script:
                    line = raw_line.strip()
                    if not line:
                        continue
                    print(f"{self.get_prompt()}{line}")
                    try:
                        cmd, args = parse_line(line)
                        self.execute_command(cmd, args)
                    except Exception as err:
                        print(f"Error executing command '{line}': {err}")
        except FileNotFoundError:
            print(f"Start script not found: {script_path}")

    def run(self) -> None:
        """Главный цикл REPL."""
        print("=== Debug: Loaded Parameters ===")
        print(f"VFS: {self.vfs_path}")
        print(f"Prompt: {self.custom_prompt}")
        print(f"Script: {self.script_path}")
        print("================================")

        if self.script_path:
            self.run_script(self.script_path)

        while self.running:
            try:
                line = input(self.get_prompt())
                cmd, args = parse_line(line)
                self.execute_command(cmd, args)
            except (EOFError, KeyboardInterrupt):
                print()
                break


def main() -> None:
    """Точка входа с обработкой CLI параметров."""
    parser = argparse.ArgumentParser(description="UNIX-like Shell Emulator")
    parser.add_argument("--vfs", help="Path to VFS zip archive")
    parser.add_argument("--prompt", help="Custom REPL prompt")
    parser.add_argument("--script", help="Path to startup script")
    args = parser.parse_args()

    app = ShellEmulator(
        vfs_path=args.vfs,
        custom_prompt=args.prompt,
        script_path=args.script,
    )
    app.run()


if __name__ == "__main__":
    main()