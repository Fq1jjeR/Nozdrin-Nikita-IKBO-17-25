"""Визуализация графа зависимостей средствами Graphviz.

Этап 5: формирование текстового описания графа на языке DOT
и сохранение изображения в формате PNG через утилиту dot.
"""

import subprocess

from .config import AppConfig
from .graph import get_graph


DOT_HEADER = "digraph dependencies {"
DOT_RANKDIR = "    rankdir=LR;"
DOT_NODE_STYLE = '    node [shape=box, fontname="Arial"];'
DOT_FOOTER = "}"
ROOT_FILL = "lightblue"


def to_dot(graph: dict, root: str) -> str:
    """Сформировать описание графа на языке DOT (Graphviz).

    Корневой пакет выделяется цветом. Рёбра направлены от пакета
    к его зависимостям. Циклы отображаются естественно (DOT
    поддерживает цикличные графы).

    Args:
        graph: словарь {пакет: [зависимости]}.
        root: корневой пакет.

    Returns:
        Строка с описанием графа на языке DOT.
    """
    lines = [DOT_HEADER, DOT_RANKDIR, DOT_NODE_STYLE]
    lines.append(
        f'    "{root}" [style=filled, fillcolor={ROOT_FILL}];'
    )
    for node in sorted(graph):
        for dep in graph[node]:
            lines.append(f'    "{node}" -> "{dep}";')
    lines.append(DOT_FOOTER)
    return "\n".join(lines)


def render_png(dot_text: str, output_file: str) -> bool:
    """Сохранить изображение графа в файл PNG через утилиту dot.

    Args:
        dot_text: описание графа на языке DOT.
        output_file: имя выходного файла PNG.

    Returns:
        True при успешной генерации, False если утилита dot
        недоступна или завершилась с ошибкой.
    """
    try:
        subprocess.run(
            ["dot", "-Tpng", "-o", output_file],
            input=dot_text.encode("utf-8"),
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False
    return True


def build_visualization(config: AppConfig) -> tuple:
    """Построить граф, сформировать DOT и сохранить PNG.

    Args:
        config: конфигурация приложения.

    Returns:
        Кортеж (dot_text, success) где dot_text — описание графа
        на языке DOT, success — флаг успешного сохранения PNG.

    Raises:
        RuntimeError: при ошибке построения графа.
        ValueError: если пакет не найден.
    """
    graph = get_graph(config)
    dot_text = to_dot(graph, config.package)
    success = render_png(dot_text, config.output)
    return dot_text, success