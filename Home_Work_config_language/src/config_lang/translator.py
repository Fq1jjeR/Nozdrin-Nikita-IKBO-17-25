"""Транслятор конфигурационного языка в YAML."""

from __future__ import annotations

from typing import Any

import yaml
from lark import Token, Tree
from lark.exceptions import LarkError

from .parser import build_parser


class TranslationError(Exception):
    """Ошибка трансляции входного текста.

    Атрибут line и column содержат координаты ошибки в
    исходном тексте, если их удалось определить.
    """

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        """Инициализировать исключение с сообщением и позицией.

        Args:
            message: Текст сообщения об ошибке.
            line: Номер строки исходного текста (если известен).
            column: Номер колонки исходного текста (если известен).
        """
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        """Вернуть человеко-читаемое представление ошибки."""
        prefix = ""
        if self.line is not None and self.column is not None:
            prefix = f"Строка {self.line}, колонка {self.column}: "
        return f"{prefix}{self.message}"


class Translator:
    """Преобразует входной текст в YAML.

    Транслятор выполняет разбор входной строки, построение AST
    с вычислением констант и константных выражений, а затем
    сериализацию результата в текст формата YAML.

    Examples:
        >>> tr = Translator()
        >>> tr.translate("x is 2.0;\\n{ a -> x. }")
        'a: 2.0\\n'
    """

    def __init__(self) -> None:
        """Создать транслятор с пустой таблицей констант.

        Парсер Lark создаётся один раз и переиспользуется для
        последующих вызовов :meth:`translate`.
        """
        self._parser = build_parser()
        self._constants: dict[str, float] = {}

    def translate(self, source: str) -> str:
        """Преобразовать исходный текст в строку YAML.

        Args:
            source: Входной текст на учебном языке.

        Returns:
            Строка с YAML-представлением входной конфигурации.

        Raises:
            TranslationError: При синтаксической ошибке или ошибке
                вычисления константного выражения.
        """
        tree = self._parse(source)
        self._constants = {}
        items: list[Any] = []
        for child in tree.children:
            items.append(self._visit_config_item(child))
        return self._dump_yaml(items)

    def _parse(self, source: str) -> Tree:
        """Разобрать исходный текст в дерево Lark.

        Args:
            source: Входной текст.

        Returns:
            Дерево разбора.

        Raises:
            TranslationError: При синтаксической ошибке.
        """
        try:
            return self._parser.parse(source)
        except LarkError as exc:
            line = getattr(exc, "line", None)
            column = getattr(exc, "column", None)
            raise TranslationError(
                f"Синтаксическая ошибка: {exc}",
                line=line,
                column=column,
            ) from exc

    def _visit_config_item(self, tree: Tree) -> Any:
        """Обработать один элемент верхнего уровня конфигурации.

        Элементом может быть объявление константы или словарь.
        Объявление константы возвращает None (оно не попадает в
        вывод), а словарь возвращает построенную структуру.

        Args:
            tree: Узел дерева config_item.

        Returns:
            Структуру словаря или None для константы.
        """
        inner = tree.children[0]
        if inner.data == "const_decl":
            self._visit_const_decl(inner)
            return None
        if inner.data == "dict":
            return self._visit_dict(inner)
        raise TranslationError(
            f"Неизвестный элемент конфигурации: {inner.data}"
        )

    def _visit_const_decl(self, tree: Tree) -> None:
        """Обработать объявление константы имя is значение;.

        Вычисляет значение константы и сохраняет его в таблице
        констант. Если константа уже объявлена, ошибка не
        возбуждается: последнее объявление перекрывает прежнее.

        Args:
            tree: Узел дерева const_decl.
        """
        name = self._token_text(tree.children[0])
        value_tree = tree.children[1]
        value = self._visit_const_value(value_tree)
        self._constants[name] = value

    def _visit_const_value(self, tree: Tree) -> float:
        """Вычислить значение правой части объявления константы.

        Args:
            tree: Узел number или const_expr.

        Returns:
            Числовое значение константы.
        """
        if tree.data == "number":
            return self._parse_number(tree.children[0])
        if tree.data == "const_expr":
            return self._visit_expr(tree.children[0])
        raise TranslationError(
            f"Неизвестное значение константы: {tree.data}"
        )

    def _visit_expr(self, tree: Tree) -> float:
        """Вычислить константное выражение и вернуть число.

        Поддерживаются арифметические операции +, -,
        *, / и функции abs(...) и min(...).

        Args:
            tree: Узел выражения.

        Returns:
            Результат вычисления выражения.

        Raises:
            TranslationError: При делении на ноль или ссылке на
                неизвестную константу.
        """
        if isinstance(tree, Token):
            if tree.type == "NUMBER":
                return self._parse_number(tree)
            raise TranslationError(f"Неожиданный токен: {tree}")
        data = tree.data
        if data == "number":
            return self._parse_number(tree.children[0])
        if data == "var":
            return self._visit_var(tree)
        if data in ("add", "sub", "mul", "div"):
            return self._visit_binop(tree, data)
        if data == "abs_fn":
            arg = self._visit_expr(tree.children[0])
            return float(abs(arg))
        if data == "min_fn":
            args = [self._visit_expr(c) for c in tree.children]
            return float(min(args))
        raise TranslationError(
            f"Неизвестная операция выражения: {data}"
        )

    def _visit_var(self, tree: Tree) -> float:
        """Вернуть значение объявленной константы по имени.

        Args:
            tree: Узел var.

        Returns:
            Числовое значение константы.

        Raises:
            TranslationError: Если константа не объявлена.
        """
        name = self._token_text(tree.children[0])
        if name not in self._constants:
            line, col = self._pos(tree)
            raise TranslationError(
                f"Необъявленная константа: {name}",
                line=line,
                column=col,
            )
        return self._constants[name]

    def _visit_binop(self, tree: Tree, op: str) -> float:
        """Вычислить бинарную арифметическую операцию.

        Args:
            tree: Узел операции (add, sub, mul, div).
            op: Имя операции.

        Returns:
            Результат применения операции к операндам.
        """
        left = self._visit_expr(tree.children[0])
        right = self._visit_expr(tree.children[1])
        return self._apply_op(op, left, right, tree)

    def _apply_op(
        self,
        op: str,
        left: float,
        right: float,
        tree: Tree,
    ) -> float:
        """Применить бинарную арифметическую операцию.

        Args:
            op: Имя операции (add, sub, mul, div).
            left: Левый операнд.
            right: Правый операнд.
            tree: Узел дерева для сообщения об ошибке.

        Returns:
            Результат операции.

        Raises:
            TranslationError: При делении на ноль.
        """
        if op == "add":
            return left + right
        if op == "sub":
            return left - right
        if op == "mul":
            return left * right
        if op == "div":
            if right == 0:
                line, col = self._pos(tree)
                raise TranslationError(
                    "Деление на ноль в константном выражении",
                    line=line,
                    column=col,
                )
            return left / right
        raise TranslationError(f"Неизвестная операция: {op}")

    def _visit_dict(self, tree: Tree) -> dict[str, Any]:
        """Построить словарь из узла dict.

        Args:
            tree: Узел дерева dict.

        Returns:
            Словарь с именами полей в порядке объявления.
        """
        result: dict[str, Any] = {}
        for entry in tree.children:
            name = self._token_text(entry.children[0])
            value = self._visit_value(entry.children[1])
            result[name] = value
        return result

    def _visit_value(self, tree: Tree) -> Any:
        """Вычислить значение поля словаря.

        Значением может быть число, вложенный словарь,
        константное выражение или ссылка на объявленную константу.

        Args:
            tree: Узел значения.

        Returns:
            Число или словарь.
        """
        if tree.data == "number":
            return self._parse_number(tree.children[0])
        if tree.data == "dict":
            return self._visit_dict(tree)
        if tree.data == "const_expr":
            return self._visit_expr(tree.children[0])
        if tree.data == "var":
            name = self._token_text(tree.children[0])
            if name not in self._constants:
                line, col = self._pos(tree)
                raise TranslationError(
                    f"Необъявленная константа: {name}",
                    line=line,
                    column=col,
                )
            return self._constants[name]
        raise TranslationError(
            f"Неизвестное значение поля: {tree.data}"
        )

    def _parse_number(self, token: Token) -> float:
        """Преобразовать токен числа в float.

        Args:
            token: Токен типа NUMBER.

        Returns:
            Числовое значение.
        """
        return float(str(token))

    def _token_text(self, node: Any) -> str:
        """Извлечь текст из токена или узла дерева.

        Args:
            node: Токен Lark или дочерний узел.

        Returns:
            Строковое представление.
        """
        return str(node)

    def _pos(self, tree: Any) -> tuple[int | None, int | None]:
        """Вернуть позицию узла в исходном тексте.

        Args:
            tree: Узел дерева.

        Returns:
            Кортеж (строка, колонка); значения None, если
            позиция неизвестна.
        """
        meta = getattr(tree, "meta", None)
        if meta is None:
            return (None, None)
        return (getattr(meta, "line", None),
                getattr(meta, "column", None))

    def _dump_yaml(self, items: list[Any]) -> str:
        """Сериализовать список элементов в строку YAML.

        Если на верхнем уровне ровно один словарь, он выводится
        напрямую (без обёртки в последовательность). Иначе
        элементы выводятся как YAML-последовательность.

        Args:
            items: Список результатов верхнего уровня.

        Returns:
            Строка YAML.
        """
        non_none = [it for it in items if it is not None]
        if len(non_none) == 1 and isinstance(non_none[0], dict):
            data: Any = non_none[0]
        else:
            data = non_none
        return yaml.safe_dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )
