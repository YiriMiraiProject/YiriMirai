# -*- coding: utf-8 -*-
import logging
from enum import IntEnum

__all__ = ['ConsoleColor', 'ColoredFormatter']


class ConsoleColor(IntEnum):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, \
    BLACK_BOLD, RED_BOLD, GREEN_BOLD, YELLOW_BOLD, \
    BLUE_BOLD, MAGENTA_BOLD, CYAN_BOLD, WHITE_BOLD = range(16)

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
    def __init__(self, *args, colors: dict = COLORS, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def format(self, record):
        formatted = super().format(record)
        levelname = record.levelname
        if levelname in self.colors:
            formatted = self.colors[levelname].seq() + formatted + "\033[0m"
        return formatted
