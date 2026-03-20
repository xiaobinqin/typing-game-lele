import pygame
import os
import sys
from src.utils.constants import FONT_PATH_CN

_cache = {}

def _get_system_cn_font():
    """获取系统中文字体路径"""
    candidates = []
    if sys.platform == "darwin":
        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode MS.ttf",
        ]
    elif sys.platform.startswith("win"):
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key in _cache:
        return _cache[key]

    font = None
    # 优先用内置字体资源
    if os.path.exists(FONT_PATH_CN):
        try:
            font = pygame.font.Font(FONT_PATH_CN, size)
        except Exception:
            font = None

    # 其次用系统字体
    if font is None:
        sys_font = _get_system_cn_font()
        if sys_font:
            try:
                font = pygame.font.Font(sys_font, size)
            except Exception:
                font = None

    # 兜底
    if font is None:
        font = pygame.font.SysFont("Arial", size, bold=bold)

    _cache[key] = font
    return font
