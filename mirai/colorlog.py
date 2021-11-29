# -*- coding: utf-8 -*-
"""
此模块提供带颜色的格式化日志输出的功能。

这是一个辅助模块，与机器人功能无关。如果你喜欢这一功能，也可以把它复制到你的项目中.
"""
import logging
from enum import IntEnum
from typing import Dict, Iterable, Mapping, Optional, cast

__all__ = ['ConsoleColor', 'ColoredFormatter']


class ConsoleColor(IntEnum):
    """各种颜色。"""
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, \
        BLACK_BOLD, RED_BOLD, GREEN_BOLD, YELLOW_BOLD, \
        BLUE_BOLD, MAGENTA_BOLD, CYAN_BOLD, WHITE_BOLD = cast(Iterable['ConsoleColor'], range(16))

    def seq(self):
        s = '\033[1;' if self.value >= 8 else '\033['
        s += f'{30 + self.value % 8}m'
        return s


COLORS = {
    'DEBUG': ConsoleColor.GREEN,
    'INFO': ConsoleColor.WHITE,
    'WARNING': ConsoleColor.YELLOW,
    'ERROR': ConsoleColor.RED,
    'CRITICAL': ConsoleColor.RED_BOLD,
}


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器。"""
    colors: Dict[str, ConsoleColor]

    def __init__(
        self,
        *args,
        colors: Optional[Mapping[str, ConsoleColor]] = None,
        **kwargs
    ):
        """
        Args:
            colors: 一个字典，键是日志级别名称，值是颜色。
        """
        super().__init__(*args, **kwargs)
        if colors is None:
            self.colors = COLORS
        else:
            self.colors = {**colors}

    def format(self, record):
        formatted = super().format(record)
        levelname = record.levelname
        if levelname in self.colors:
            formatted = self.colors[levelname].seq() + formatted + "\033[0m"
        return formatted
