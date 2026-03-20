import pygame
import os
import sys
from src.utils.constants import FONT_PATH_CN


_cache = {}


def _get_base_path():
    """兼容 PyInstaller 打包后的资源路径"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_system_cn_font():
    """获取系统中文字体路径，打包环境优先使用捆绑字体"""
    base = _get_base_path()

    # 打包时捆绑的字体
    bundled = os.path.join(base, "system_fonts", "STHeiti Light.ttc")
    if os.path.exists(bundled):
        return bundled

    # 开发环境：尝试系统字体
    candidates = []
    if sys.platform == "darwin":
        candidates = [
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/PingFang.ttc",
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

    # 1. 优先使用 assets/fonts 里的自定义字体
    font_path = os.path.join(_get_base_path(), "assets", "fonts", "chinese.ttf")
    if os.path.exists(font_path):
        try:
            font = pygame.font.Font(font_path, size)
        except Exception:
            font = None

    # 2. 捆绑/系统中文字体
    if font is None:
        sys_font = _get_system_cn_font()
        if sys_font:
            try:
                font = pygame.font.Font(sys_font, size)
            except Exception:
                font = None

    # 3. 兜底：pygame 内置 SysFont
    if font is None:
        font = pygame.font.SysFont("Arial", size, bold=bold)

    _cache[key] = font
    return font
