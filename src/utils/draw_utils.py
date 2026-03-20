import pygame
from src.utils.constants import WHITE, BLACK, COLOR_PRIMARY, COLOR_BG_PANEL
from src.utils.font_manager import get_font


def draw_rounded_rect(surface, color, rect, radius=16, border=0, border_color=None):
    """绘制圆角矩形"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_text(surface, text, size, color, x, y, center=False, bold=False):
    font = get_font(size, bold)
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)
    return rect


def draw_button(surface, text, rect, bg_color, text_color=WHITE,
                font_size=24, radius=14, hover=False, border_color=None):
    """绘制按钮，hover时略微变亮"""
    color = tuple(min(255, c + 20) for c in bg_color) if hover else bg_color
    draw_rounded_rect(surface, color, rect, radius=radius,
                      border=2 if border_color else 0, border_color=border_color)
    cx = rect[0] + rect[2] // 2
    cy = rect[1] + rect[3] // 2
    draw_text(surface, text, font_size, text_color, cx, cy, center=True, bold=True)


def draw_input_box(surface, text, rect, active=True, font_size=32):
    """绘制输入框"""
    bg = (230, 242, 255) if active else (245, 245, 245)
    border_color = COLOR_PRIMARY if active else (180, 180, 180)
    draw_rounded_rect(surface, bg, rect, radius=12, border=3, border_color=border_color)
    if text:
        draw_text(surface, text, font_size, (40, 40, 80),
                  rect[0] + rect[2] // 2, rect[1] + rect[3] // 2, center=True)
    else:
        draw_text(surface, "请输入拼音...", font_size - 4, (180, 180, 200),
                  rect[0] + rect[2] // 2, rect[1] + rect[3] // 2, center=True)


def draw_progress_bar(surface, x, y, w, h, value, max_value,
                      color_bg=(200, 210, 230), color_fill=(72, 154, 255), radius=8):
    """绘制进度条"""
    pygame.draw.rect(surface, color_bg, (x, y, w, h), border_radius=radius)
    fill_w = int(w * min(value, max_value) / max_value) if max_value else 0
    if fill_w > 0:
        pygame.draw.rect(surface, color_fill, (x, y, fill_w, h), border_radius=radius)


def draw_heart(surface, x, y, filled=True, size=24):
    """绘制爱心（用圆形+矩形模拟）"""
    color = (220, 60, 60) if filled else (200, 200, 200)
    r = size // 4
    pygame.draw.circle(surface, color, (x - r, y), r)
    pygame.draw.circle(surface, color, (x + r, y), r)
    points = [(x - size // 2, y), (x, y + size // 2), (x + size // 2, y)]
    pygame.draw.polygon(surface, color, points)


def draw_star(surface, x, y, filled=True, size=20):
    """绘制五角星"""
    import math
    color = (255, 200, 0) if filled else (200, 200, 200)
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size // 2
        points.append((x + r * math.cos(angle), y - r * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)


def draw_background_gradient(surface, color_top, color_bottom, w, h):
    """绘制渐变背景"""
    for i in range(h):
        t = i / h
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, i), (w, i))
