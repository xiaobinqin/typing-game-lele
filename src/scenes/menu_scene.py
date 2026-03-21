import math
import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_divider, draw_badge, draw_shadow_rect)


class MenuScene:
    def __init__(self, game):
        self.game = game
        self.hover_idx = -1
        self.anim_tick = 0
        self.buttons = self._build_buttons()

    def _build_buttons(self):
        cx = SCREEN_WIDTH // 2
        btn_w, btn_h = 300, 62
        gap = 18
        start_y = 400
        items = [
            ("开始游戏", SCENE_GRADE_SELECT, COLOR_PRIMARY),
            ("排  行  榜", SCENE_LEADERBOARD, (100, 116, 155)),
        ]
        btns = []
        for i, (label, scene, color) in enumerate(items):
            y = start_y + i * (btn_h + gap)
            btns.append({
                "rect":  pygame.Rect(cx - btn_w // 2, y, btn_w, btn_h),
                "label": label,
                "scene": scene,
                "color": color,
            })
        return btns

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_idx = -1
            for i, btn in enumerate(self.buttons):
                if btn["rect"].collidepoint(mx, my):
                    self.hover_idx = i
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for btn in self.buttons:
                if btn["rect"].collidepoint(mx, my):
                    self.game.change_scene(btn["scene"])

    def update(self):
        self.anim_tick += 1

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        self._draw_top_band(surface)
        self._draw_title(surface)
        self._draw_feature_strip(surface)
        self._draw_buttons(surface)
        self._draw_footer(surface)

    # ------------------------------------------------------------------ #
    #  顶部大色块 + 浮动气泡
    # ------------------------------------------------------------------ #
    def _draw_top_band(self, surface):
        band_h = 310
        # 主色块
        pygame.draw.rect(surface, COLOR_PRIMARY,
                         (0, 0, SCREEN_WIDTH, band_h))
        # 底部平滑椭圆过渡
        pygame.draw.ellipse(surface, COLOR_PRIMARY,
                            (-80, band_h - 56, SCREEN_WIDTH + 160, 112))

        t = self.anim_tick * 0.016
        # 大装饰圆（右上区域）
        bubbles = [
            (SCREEN_WIDTH - 80,  -30,  110, 18),
            (SCREEN_WIDTH - 200,  60,   70, 12),
            (SCREEN_WIDTH - 100, 180,   50,  9),
            (60,                 -20,   80, 14),
            (30,                 130,   45,  8),
        ]
        for i, (bx, by, r, alpha) in enumerate(bubbles):
            dy = int(10 * math.sin(t + i * 1.2))
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 255, alpha), (r, r), r)
            surface.blit(surf, (bx - r, by + dy))

    # ------------------------------------------------------------------ #
    #  标题区
    # ------------------------------------------------------------------ #
    def _draw_title(self, surface):
        cx = SCREEN_WIDTH // 2
        t = self.anim_tick * 0.022

        # 主标题轻微浮动
        dy = int(4 * math.sin(t))
        draw_text(surface, "打字大挑战", 78, WHITE,
                  cx, 110 + dy, center=True, bold=True)

        # 副标题
        draw_text(surface, "乐  乐  版", 36, (205, 228, 255),
                  cx, 196, center=True, bold=True)

        # 小说明文字（色带下方）
        draw_text(surface, "学拼音  ·  认汉字  ·  打字快手",
                  21, COLOR_TEXT_SUB, cx, 346, center=True)

    # ------------------------------------------------------------------ #
    #  三个特性小标签条（标题区与按钮之间）
    # ------------------------------------------------------------------ #
    def _draw_feature_strip(self, surface):
        features = [
            ("📚", "人教版同步"),
            ("🎯", "6大练习模式"),
            ("🏆", "排行榜对战"),
        ]
        total_w = 660
        sx = (SCREEN_WIDTH - total_w) // 2
        y = 372
        item_w = total_w // len(features)

        for i, (icon, label) in enumerate(features):
            cx = sx + i * item_w + item_w // 2
            # 小胶囊背景
            cap_w, cap_h = 190, 34
            cap = pygame.Rect(cx - cap_w // 2, y - cap_h // 2, cap_w, cap_h)
            pygame.draw.rect(surface, WHITE, cap, border_radius=17)
            # 文字
            draw_text(surface, f"{icon}  {label}", 16, COLOR_TEXT_MAIN,
                      cx, y, center=True, bold=True)

    # ------------------------------------------------------------------ #
    #  主操作按钮
    # ------------------------------------------------------------------ #
    def _draw_buttons(self, surface):
        for i, btn in enumerate(self.buttons):
            hover = (i == self.hover_idx)
            # "开始游戏"按钮加发光效果
            if i == 0 and hover:
                glow = btn["rect"].inflate(12, 12)
                glow_surf = pygame.Surface((glow.width, glow.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*COLOR_PRIMARY, 50),
                                 (0, 0, glow.width, glow.height), border_radius=20)
                surface.blit(glow_surf, glow.topleft)
            draw_button(surface, btn["label"], btn["rect"],
                        btn["color"], WHITE, font_size=26,
                        radius=16, hover=hover, shadow=True)

    # ------------------------------------------------------------------ #
    #  底部版权 + 漂浮星星
    # ------------------------------------------------------------------ #
    def _draw_footer(self, surface):
        draw_text(surface, "适合小学 1 — 6 年级  ·  人教版教材同步",
                  16, COLOR_TEXT_SUB, SCREEN_WIDTH // 2,
                  SCREEN_HEIGHT - 32, center=True)

        t = self.anim_tick * 0.022
        star_pos = [(140, 540), (260, 576), (SCREEN_WIDTH - 260, 576), (SCREEN_WIDTH - 140, 540)]
        for j, (sx, sy) in enumerate(star_pos):
            dy = int(7 * math.sin(t + j * 0.85))
            alpha = 140 + int(70 * math.sin(t + j * 1.1))
            s = pygame.Surface((32, 32), pygame.SRCALPHA)
            sz = 11
            pts = []
            for k in range(10):
                ang = math.pi / 2 + k * math.pi / 5
                r = sz if k % 2 == 0 else sz * 4 // 9
                pts.append((16 + r * math.cos(ang), 16 - r * math.sin(ang)))
            pygame.draw.polygon(s, (255, 200, 0, alpha), pts)
            surface.blit(s, (sx - 16, sy + dy - 16))

        # 版本号
        draw_text(surface, "v1.0", 13, (185, 192, 215),
                  SCREEN_WIDTH - 24, SCREEN_HEIGHT - 20)
