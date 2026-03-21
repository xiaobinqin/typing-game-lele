import math
import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_star, draw_divider, draw_badge)


class MenuScene:
    def __init__(self, game):
        self.game = game
        self.hover_idx = -1
        self.anim_tick = 0
        self.buttons = self._build_buttons()

    def _build_buttons(self):
        cx = SCREEN_WIDTH // 2
        btn_w, btn_h = 280, 60
        gap = 16
        start_y = 390
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
        self._draw_buttons(surface)
        self._draw_footer(surface)

    def _draw_top_band(self, surface):
        """顶部蓝色装饰带"""
        band_h = 260
        pygame.draw.rect(surface, COLOR_PRIMARY,
                         (0, 0, SCREEN_WIDTH, band_h), border_radius=0)
        # 底部弧形
        pygame.draw.ellipse(surface, COLOR_PRIMARY,
                            (-60, band_h - 60, SCREEN_WIDTH + 120, 120))

        # 右上角淡色圆形装饰
        t = self.anim_tick * 0.018
        for i, (ox, oy, r, alpha) in enumerate([
            (880, 50, 90, 22), (940, 160, 60, 16), (820, 200, 40, 12),
        ]):
            dy = int(8 * math.sin(t + i * 1.3))
            circ_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(circ_surf, (255, 255, 255, alpha), (r, r), r)
            surface.blit(circ_surf, (ox - r, oy + dy - r))

    def _draw_title(self, surface):
        cx = SCREEN_WIDTH // 2
        # 主标题（白色，在蓝色带上）
        draw_text(surface, "打字大挑战", 72, WHITE, cx, 110, center=True, bold=True)
        draw_text(surface, "乐  乐  版", 34, (200, 225, 255), cx, 188, center=True, bold=True)

        # 副标题（蓝色带下方）
        draw_text(surface, "学拼音  ·  认汉字  ·  打字快手",
                  22, COLOR_TEXT_SUB, cx, 310, center=True)

    def _draw_buttons(self, surface):
        for i, btn in enumerate(self.buttons):
            hover = (i == self.hover_idx)
            draw_button(surface, btn["label"], btn["rect"],
                        btn["color"], WHITE, font_size=26,
                        radius=14, hover=hover, shadow=True)

    def _draw_footer(self, surface):
        draw_text(surface, "适合小学 1 — 6 年级  ·  人教版教材同步",
                  17, COLOR_TEXT_SUB, SCREEN_WIDTH // 2,
                  SCREEN_HEIGHT - 36, center=True)

        # 底部装饰星星（平静漂浮）
        t = self.anim_tick * 0.025
        star_positions = [(160, 530), (280, 570), (744, 570), (864, 530)]
        for j, (sx, sy) in enumerate(star_positions):
            dy = int(6 * math.sin(t + j * 0.9))
            alpha_v = 160 + int(60 * math.sin(t + j))
            s = pygame.Surface((40, 40), pygame.SRCALPHA)
            pts = []
            sz = 14
            for k in range(10):
                ang = math.pi / 2 + k * math.pi / 5
                r = sz if k % 2 == 0 else sz * 4 // 9
                pts.append((20 + r * math.cos(ang), 20 - r * math.sin(ang)))
            pygame.draw.polygon(s, (255, 195, 0, alpha_v), pts)
            surface.blit(s, (sx - 20, sy + dy - 20))
