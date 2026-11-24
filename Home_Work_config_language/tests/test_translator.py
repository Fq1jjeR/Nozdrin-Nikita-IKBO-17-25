"""Тесты транслятора

Тесты покрывают все конструкции языка: числа, словари,
многострочные комментарии, объявления констант, константные
выражения с арифметическими операциями и функциями ``min()``
и ``abs()``, а также вложенные структуры и сообщения об ошибках.
"""

from __future__ import annotations

import pytest
import yaml

from config_lang import Translator, TranslationError


def _translate(source: str) -> object:
    """Транслировать исходный текст и разобрать YAML в объект.

    Args:
        source: Входной текст учебного языка.

    Returns:
        Python-объект, эквивалентный YAML-результату.
    """
    text = Translator().translate(source)
    return yaml.safe_load(text)


# --- Числа и базовые словари -----------------------------------------


def test_simple_number_entry() -> None:
    """Одиночное поле с числовым значением транслируется."""
    result = _translate("{ a -> 1.0. }")
    assert result == {"a": 1.0}


def test_multiple_entries() -> None:
    """Несколько полей сохраняют порядок объявления."""
    result = _translate("{ a -> 1.0. b -> 2.5. c -> 3.14. }")
    assert result == {"a": 1.0, "b": 2.5, "c": 3.14}


def test_signed_numbers() -> None:
    """Знаковые числа разбираются как положительные и отрицательные."""
    result = _translate("{ a -> -1.5. b -> +2.0. }")
    assert result == {"a": -1.5, "b": 2.0}


def test_empty_dict() -> None:
    """Пустой словарь транслируется в пустой словарь YAML."""
    result = _translate("{ }")
    assert result == {}


# --- Многострочные комментарии ---------------------------------------


def test_multiline_comment_ignored() -> None:
    """Многострочный комментарий полностью игнорируется."""
    source = """
    /* Это многострочный
       комментарий из двух строк */
    { a -> 1.0. }
    """
    assert _translate(source) == {"a": 1.0}


def test_comment_inside_dict() -> None:
    """Комментарий между записями словаря игнорируется."""
    source = "{ a -> 1.0. /* c -> 2.0. */ b -> 3.0. }"
    assert _translate(source) == {"a": 1.0, "b": 3.0}


# --- Вложенные словари -----------------------------------------------


def test_nested_dict_one_level() -> None:
    """Словарь внутри значения поля раскрывается в YAML."""
    source = "{ outer -> { inner -> 5.0. }. }"
    assert _translate(source) == {"outer": {"inner": 5.0}}


def test_nested_dict_deep() -> None:
    """Глубоко вложенные словари транслируются корректно."""
    source = (
        "{ a -> { b -> { c -> { d -> 1.0. }. }. }. }"
    )
    assert _translate(source) == {
        "a": {"b": {"c": {"d": 1.0}}}
    }


def test_nested_dict_multiple_keys() -> None:
    """Вложенный словарь с несколькими ключами сохраняет их."""
    source = (
        "{ db -> { host -> 0.0. port -> 1.0. }. }"
    )
    assert _translate(source) == {
        "db": {"host": 0.0, "port": 1.0}
    }


# --- Объявления констант ---------------------------------------------


def test_constant_declaration() -> None:
    """Константа используется в значении поля."""
    source = "x is 2.0;\n{ a -> x. }"
    assert _translate(source) == {"a": 2.0}


def test_constant_redeclaration() -> None:
    """Последнее объявление константы перекрывает прежнее."""
    source = "x is 1.0;\nx is 9.0;\n{ a -> x. }"
    assert _translate(source) == {"a": 9.0}


def test_undeclared_constant_error() -> None:
    """Ссылка на необъявленную константу вызывает ошибку."""
    with pytest.raises(TranslationError, match="Необъявленная"):
        _translate("{ a -> unknown. }")


# --- Константные выражения -------------------------------------------


def test_const_expr_addition() -> None:
    """Сложение в константном выражении вычисляется."""
    source = "x is 1.0;\n{ a -> .(x + 1.0). }"
    assert _translate(source) == {"a": 2.0}


def test_const_expr_subtraction() -> None:
    """Вычитание в константном выражении вычисляется."""
    source = "{ a -> .(5.0 - 2.0). }"
    assert _translate(source) == {"a": 3.0}


def test_const_expr_multiplication() -> None:
    """Умножение в константном выражении вычисляется."""
    source = "{ a -> .(4.0 * 3.0). }"
    assert _translate(source) == {"a": 12.0}


def test_const_expr_division() -> None:
    """Деление в константном выражении вычисляется."""
    source = "{ a -> .(10.0 / 4.0). }"
    assert _translate(source) == {"a": 2.5}


def test_const_expr_precedence() -> None:
    """Приоритет операций соблюдается: умножение раньше сложения."""
    source = "{ a -> .(2.0 + 3.0 * 4.0). }"
    assert _translate(source) == {"a": 14.0}


def test_const_expr_parentheses() -> None:
    """Скобки изменяют порядок вычисления."""
    source = "{ a -> .((2.0 + 3.0) * 4.0). }"
    assert _translate(source) == {"a": 20.0}


def test_const_expr_with_constant() -> None:
    """Константное выражение ссылается на объявленную константу."""
    source = "pi is 3.14;\nr is 2.0;\n{ a -> .(pi * r * r). }"
    assert _translate(source) == pytest.approx({"a": 12.56})


# --- Функции abs() и min() -------------------------------------------


def test_abs_function() -> None:
    """Функция abs() возвращает модуль аргумента."""
    source = "{ a -> .(abs(-7.0)). }"
    assert _translate(source) == {"a": 7.0}


def test_abs_function_nested() -> None:
    """abs() от выражения вычисляется после вложенного выражения."""
    source = "{ a -> .(abs(3.0 - 10.0)). }"
    assert _translate(source) == {"a": 7.0}


def test_min_function_two_args() -> None:
    """min() с двумя аргументами возвращает минимум."""
    source = "{ a -> .(min(1.0, 2.0)). }"
    assert _translate(source) == {"a": 1.0}


def test_min_function_many_args() -> None:
    """min() с переменным числом аргументов."""
    source = "{ a -> .(min(5.0, 3.0, 8.0, 1.0, 9.0)). }"
    assert _translate(source) == {"a": 1.0}


def test_min_function_with_constants() -> None:
    """min() может использовать значения объявленных констант."""
    source = (
        "a is -5.0;\nb is 3.0;\n{ r -> .(min(a, b, 0.0)). }"
    )
    assert _translate(source) == {"r": -5.0}


# --- Ошибки трансляции -----------------------------------------------


def test_division_by_zero_error() -> None:
    """Деление на ноль вызывает ошибку трансляции."""
    with pytest.raises(TranslationError, match="Деление на ноль"):
        _translate("{ a -> .(1.0 / 0.0). }")


def test_syntax_error_unclosed_dict() -> None:
    """Незакрытый словарь вызывает синтаксическую ошибку."""
    with pytest.raises(TranslationError, match="Синтаксическая"):
        _translate("{ a -> 1.0. ")


def test_syntax_error_invalid_name() -> None:
    """Имя с заглавной буквой вызывает синтаксическую ошибку."""
    with pytest.raises(TranslationError, match="Синтаксическая"):
        _translate("{ A -> 1.0. }")


def test_syntax_error_integer_number() -> None:
    """Целое число без точки не соответствует правилу NUMBER."""
    with pytest.raises(TranslationError, match="Синтаксическая"):
        _translate("{ a -> 1. }")


# --- Несколько элементов верхнего уровня ----------------------------


def test_multiple_top_level_dicts() -> None:
    """Несколько словарей верхнего уровня дают YAML-список."""
    source = "{ a -> 1.0. }\n{ b -> 2.0. }"
    result = _translate(source)
    assert result == [{"a": 1.0}, {"b": 2.0}]


def test_constants_and_dict_mixed() -> None:
    """Константы и словарь могут чередоваться."""
    source = (
        "x is 1.0;\n{ a -> x. }\n"
        "y is 2.0;\n{ b -> y. }"
    )
    result = _translate(source)
    assert result == [{"a": 1.0}, {"b": 2.0}]


# --- Формат вывода ---------------------------------------------------


def test_output_is_valid_yaml() -> None:
    """Результат трансляции — корректный YAML."""
    text = Translator().translate("{ a -> 1.0. b -> 2.0. }")
    assert yaml.safe_load(text) == {"a": 1.0, "b": 2.0}


def test_single_dict_no_sequence_wrapper() -> None:
    """Одиночный словарь выводится без обёртки в YAML-список."""
    text = Translator().translate("{ a -> 1.0. }")
    assert text.lstrip().startswith("a:")
    assert text.lstrip()[0] != "-"
