"""Построение лексера и парсера конфигурационного языка."""

from __future__ import annotations

from functools import lru_cache

from lark import Lark

from .grammar import GRAMMAR


@lru_cache(maxsize=1)
def build_parser() -> Lark:
    """Вернуть настроенный экземпляр парсера Lark.

    Парсер использует алгоритм Earley, что позволяет работать с
    грамматикой, содержащей левую рекурсию в правилах для
    арифметических выражений. Включён режим propagate_positions,
    чтобы сообщения об ошибках содержали номера строк и столбцов.

    Returns:
        Объект Lark с правилами учебного языка.
    """
    return Lark(
        GRAMMAR,
        start="start",
        parser="earley",
        propagate_positions=True,
        maybe_placeholders=False,
    )
