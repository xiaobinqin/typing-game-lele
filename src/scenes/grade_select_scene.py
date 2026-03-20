import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_gradient,
                                   draw_rounded_rect)


class GradeSelectScene:
    def __init__(self, game):
        self.game = game
        self.hover_idx = -1
        self.level_buttons = self._build_level_buttons()
        self.back_btn = pygame.Rect(30, 30, 100, 44)

    def _build_level_buttons(self):
        items = [
            (LEVEL_STARTER,  "启蒙级",  "一年级\n拼音起步", (100, 180, 255)),
            (LEVEL_BASIC,    "基础级",  "二年级\n拼音巩固", (80,  200, 140)),
            (LEVEL_MIDDLE,   "进阶级",  "三四年级\n汉字进阶", (255, 180, 60)),
            (LEVEL_ADVANCED, "熟练级",  "五六年级\n词语积累", (220, 80,  120)),
        ]
        buttons = []
        card_w, card_h = 200, 200
        gap = 30
        total_w = 4 * card_w + 3 * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        y = SCREEN_HEIGHT // 2 - card_h // 2 + 30
        for i, (level, name, desc, color) in enumerate(items):
            x = start_x + i * (card_w + gap)
            buttons.append({
                "rect":  pygame.Rect(x, y, card_w, card_h),
                "level": level,
                "name":  name,
                "desc":  desc,
                "color": color,
            })
        return buttons

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_idx = -1
            for i, btn in enumerate(self.level_buttons):
                if btn["rect"].collidepoint(mx, my):
                    self.hover_idx = i
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_MENU)
                return
            for btn in self.level_buttons:
                if btn["rect"].collidepoint(mx, my):
                    self.game.selected_level = btn["level"]
                    self.game.change_scene(SCENE_MODE_SELECT)

    def update(self):
        pass

    def draw(self, surface):
        draw_background_gradient(surface, (230, 245, 255), (255, 245, 220),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_text(surface, "选择年级难度", 52, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 100, center=True, bold=True)
        draw_text(surface, "请选择适合你的难度等级", 26, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 160, center=True)

        for i, btn in enumerate(self.level_buttons):
            hover = (i == self.hover_idx)
            color = btn["color"]
            if hover:
                color = tuple(min(255, c + 20) for c in color)
                rect = btn["rect"].inflate(8, 8)
            else:
                rect = btn["rect"]

            # 卡片阴影
            shadow = rect.move(4, 6)
            pygame.draw.rect(surface, (0, 0, 0, 40), shadow, border_radius=20)
            pygame.draw.rect(surface, color, rect, border_radius=20)

            cx = rect.centerx
            cy = rect.centery
            draw_text(surface, btn["name"], 30, WHITE, cx, cy - 30, center=True, bold=True)
            for j, line in enumerate(btn["desc"].split("\n")):
                draw_text(surface, line, 20, WHITE, cx, cy + 10 + j * 26, center=True)

        # 返回按钮
        draw_button(surface, "← 返回", self.back_btn, GRAY, WHITE, font_size=20)
