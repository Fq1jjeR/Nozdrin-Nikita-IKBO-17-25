"""Модуль парсера команд."""


def parse_command(input_string):
    """Разделяет ввод на команду и аргументы по пробелам.

    Args:
        input_string: строка ввода пользователя.

    Returns:
        Кортеж (command, args). Если ввод пустой — (None, []).
    """
    parts = input_string.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]