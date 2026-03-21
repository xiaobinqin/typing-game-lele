import pygame
import math
from src.utils.constants import WHITE, BLACK, COLOR_PRIMARY, COLOR_TEXT_MAIN, COLOR_TEXT_SUB
from src.utils.font_manager import get_font


# ---------- 缓存渐变背景，避免每帧逐行绘制 ----------
_bg_cache: dict = {}


def get_bg_surface(color_top, color_bottom, w, h):
    key = (color_top, color_bottom, w, h)
    if key not in _bg_cache:
        surf = pygame.Surface((w, h))
        for i in range(h):
            t = i / h
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, i), (w, i))
        _bg_cache[key] = surf
    return _bg_cache[key]


def draw_background_gradient(surface, color_top, color_bottom, w, h):
    surface.blit(get_bg_surface(color_top, color_bottom, w, h), (0, 0))


def draw_background_solid(surface, color):
    surface.fill(color)


# ---------- 阴影矩形 ----------
def draw_shadow_rect(surface, rect, radius=16, shadow_offset=4, shadow_alpha=40):
    shadow_surf = pygame.Surface((rect[2] + shadow_offset * 2,
                                  rect[3] + shadow_offset * 2), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha),
                     (0, 0, rect[2] + shadow_offset * 2, rect[3] + shadow_offset * 2),
                     border_radius=radius + 2)
    surface.blit(shadow_surf, (rect[0] - shadow_offset, rect[1]))


def draw_rounded_rect(surface, color, rect, radius=16, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


# ---------- 文字 ----------
def draw_text(surface, text, size, color, x, y, center=False, bold=False, alpha=255):
    font = get_font(size, bold)
    surf = font.render(str(text), True, color)
    if alpha < 255:
        surf.set_alpha(alpha)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)
    return rect


# ---------- 按钮 ----------
def draw_button(surface, text, rect, bg_color, text_color=WHITE,
                font_size=22, radius=12, hover=False, border_color=None, shadow=True):
    r = pygame.Rect(rect)
    if hover:
        r = r.inflate(0, 4)
        bg = tuple(min(255, c + 18) for c in bg_color)
    else:
        bg = bg_color

    if shadow and not hover:
        draw_shadow_rect(surface, r, radius=radius, shadow_offset=3, shadow_alpha=35)

    pygame.draw.rect(surface, bg, r, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, r, 2, border_radius=radius)

    cx = r.x + r.width // 2
    cy = r.y + r.height // 2
    draw_text(surface, text, font_size, text_color, cx, cy, center=True, bold=True)


# ---------- 输入框 ----------
def draw_input_box(surface, text, rect, active=True, font_size=34):
    r = pygame.Rect(rect)
    bg = (248, 252, 255) if active else (246, 246, 246)
    border_color = COLOR_PRIMARY if active else (200, 200, 210)
    border_w = 3 if active else 2

    draw_shadow_rect(surface, r, radius=14, shadow_offset=3, shadow_alpha=25)
    pygame.draw.rect(surface, bg, r, border_radius=14)
    pygame.draw.rect(surface, border_color, r, border_w, border_radius=14)

    if text:
        draw_text(surface, text, font_size, COLOR_TEXT_MAIN,
                  r.x + r.width // 2, r.y + r.height // 2, center=True, bold=True)
    else:
        draw_text(surface, "输入拼音…", font_size - 6, (190, 195, 215),
                  r.x + r.width // 2, r.y + r.height // 2, center=True)

    # 光标竖线（active时）
    if active:
        cursor_x = r.x + r.width // 2 + (len(text) * font_size // 3 if text else 0)
        cursor_x = min(cursor_x, r.right - 18)
        pygame.draw.line(surface, COLOR_PRIMARY,
                         (cursor_x, r.y + 10), (cursor_x, r.bottom - 10), 2)


# ---------- 进度条 ----------
def draw_progress_bar(surface, x, y, w, h, value, max_value,
                      color_bg=(220, 228, 240), color_fill=(72, 154, 255), radius=6):
    pygame.draw.rect(surface, color_bg, (x, y, w, h), border_radius=radius)
    fill_w = int(w * min(value, max_value) / max_value) if max_value else 0
    if fill_w > 2:
        pygame.draw.rect(surface, color_fill, (x, y, fill_w, h), border_radius=radius)


# ---------- 爱心 ----------
def draw_heart(surface, x, y, filled=True, size=22):
    color = (235, 65, 65) if filled else (210, 210, 220)
    r = size // 4
    pygame.draw.circle(surface, color, (x - r, y - 1), r)
    pygame.draw.circle(surface, color, (x + r, y - 1), r)
    points = [(x - size // 2, y + 1), (x, y + size // 2 + 2), (x + size // 2, y + 1)]
    pygame.draw.polygon(surface, color, points)


# ---------- 五角星 ----------
def draw_star(surface, x, y, filled=True, size=18):
    color = (255, 195, 0) if filled else (210, 214, 225)
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 4 // 9
        points.append((x + r * math.cos(angle), y - r * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)
    if filled:
        pygame.draw.polygon(surface, (255, 215, 30), points, 1)


# ---------- 分割线 ----------
def draw_divider(surface, x1, y, x2, color=(220, 226, 238), thickness=1):
    pygame.draw.line(surface, color, (x1, y), (x2, y), thickness)


# ---------- 卡片（带阴影） ----------
def draw_card(surface, rect, bg=(255, 255, 255), radius=18,
              border_color=None, shadow=True):
    r = pygame.Rect(rect)
    if shadow:
        draw_shadow_rect(surface, r, radius=radius, shadow_offset=4, shadow_alpha=28)
    pygame.draw.rect(surface, bg, r, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, r, 2, border_radius=radius)


# ---------- 胶囊标签 ----------
def draw_badge(surface, text, cx, cy, bg_color, text_color=WHITE, font_size=16, px=14, py=6):
    font = get_font(font_size, bold=True)
    tw = font.size(text)[0]
    w = tw + px * 2
    h = font_size + py * 2
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surface, bg_color, rect, border_radius=h // 2)
    draw_text(surface, text, font_size, text_color, cx, cy, center=True, bold=True)
