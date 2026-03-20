import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_gradient,
                                   draw_rounded_rect, draw_star)


class MenuScene:
    def __init__(self, game):
        self.game = game
        self.buttons = self._build_buttons()
        self.hover_idx = -1
        self.anim_tick = 0
        self.particles = []

    def _build_buttons(self):
        cx = SCREEN_WIDTH // 2
        btn_w, btn_h = 260, 58
        gap = 18
        start_y = 340
        labels = [
            ("开始游戏", SCENE_GRADE_SELECT),
            ("排行榜",   SCENE_LEADERBOARD),
        ]
        buttons = []
        for i, (label, scene) in enumerate(labels):
            y = start_y + i * (btn_h + gap)
            buttons.append({
                "rect": pygame.Rect(cx - btn_w // 2, y, btn_w, btn_h),
                "label": label,
                "scene": scene,
                "color": COLOR_PRIMARY if i == 0 else COLOR_SECONDARY,
            })
        return buttons

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
        draw_background_gradient(surface, (200, 230, 255), (255, 240, 200),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)
        self._draw_decorations(surface)

        # 标题
        draw_text(surface, "打字大挑战", 72, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 140, center=True, bold=True)
        draw_text(surface, "乐乐版", 40, COLOR_SECONDARY,
                  SCREEN_WIDTH // 2, 220, center=True, bold=True)
        draw_text(surface, "学拼音 · 认汉字 · 打字快手", 26, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 280, center=True)

        # 按钮
        for i, btn in enumerate(self.buttons):
            draw_button(surface, btn["label"], btn["rect"],
                        btn["color"], font_size=28,
                        hover=(i == self.hover_idx))

        # 底部提示
        draw_text(surface, "适合小学 1-6 年级  ·  人教版教材同步",
                  18, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, center=True)

    def _draw_decorations(self, surface):
        import math
        t = self.anim_tick * 0.03
        # 左侧星星装饰
        for i in range(5):
            x = 80 + i * 30
            y = 100 + int(20 * math.sin(t + i))
            draw_star(surface, x, y, filled=True, size=14 + i * 2)
        # 右侧星星装饰
        for i in range(5):
            x = SCREEN_WIDTH - 80 - i * 30
            y = 100 + int(20 * math.sin(t + i + 2))
            draw_star(surface, x, y, filled=True, size=14 + i * 2)
