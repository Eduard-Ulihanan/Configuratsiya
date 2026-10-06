"""Парсер команд эмулятора."""

import os
import re
import shlex
from typing import List, Tuple


def expand_env_vars(text: str) -> str:
    """Раскрытие переменных окружения ОС ($VAR или ${VAR})."""
    pattern = re.compile(r"\$(\w+)|\$\{(\w+)\}")

    def _replace(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    return pattern.sub(_replace, text)


def parse_line(line: str) -> Tuple[str, List[str]]:
    """Разбор строки ввода на имя команды и аргументы."""
    expanded = expand_env_vars(line.strip())
    tokens = shlex.split(expanded)
    if not tokens:
        return "", []
    return tokens[0], tokens[1:]