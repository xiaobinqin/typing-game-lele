import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_divider, draw_badge)


LEVEL_ITEMS = [
    (LEVEL_STARTER,  "启蒙级",  "一年级",   "拼音起步",   (56, 132, 255),  "🌱"),
    (LEVEL_BASIC,    "基础级",  "二年级",   "拼音巩固",   (40, 185, 115),  "📗"),
    (LEVEL_MIDDLE,   "进阶级",  "三四年级", "汉字进阶",   (255, 160, 30),  "⭐"),
    (LEVEL_ADVANCED, "熟练级",  "五六年级", "词语积累",   (220, 70, 100),  "🏆"),
]


class GradeSelectScene:
    def __init__(self, game):
        self.game = game
        self.hover_idx = -1
        self.cards = self._build_cards()
        self.back_btn = pygame.Rect(36, 28, 96, 40)

    def _build_cards(self):
        card_w, card_h = 210, 220
        gap = 24
        total_w = len(LEVEL_ITEMS) * card_w + (len(LEVEL_ITEMS) - 1) * gap
        sx = (SCREEN_WIDTH - total_w) // 2
        y = SCREEN_HEIGHT // 2 - card_h // 2 + 20
        cards = []
        for i, (level, name, grade, desc, color, icon) in enumerate(LEVEL_ITEMS):
            x = sx + i * (card_w + gap)
            cards.append({
                "rect":  pygame.Rect(x, y, card_w, card_h),
                "level": level, "name": name, "grade": grade,
                "desc":  desc,  "color": color, "icon": icon,
            })
        return cards

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_idx = -1
            for i, c in enumerate(self.cards):
                if c["rect"].collidepoint(mx, my):
                    self.hover_idx = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_MENU)
                return
            for c in self.cards:
                if c["rect"].collidepoint(mx, my):
                    self.game.selected_level = c["level"]
                    self.game.change_scene(SCENE_MODE_SELECT)

    def update(self):
        pass

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        self._draw_header(surface)
        self._draw_cards(surface)
        draw_button(surface, "← 返回", self.back_btn,
                    (180, 188, 205), WHITE, font_size=17, radius=10, shadow=False)

    def _draw_header(self, surface):
        draw_text(surface, "选择年级难度", 44, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 90, center=True, bold=True)
        draw_text(surface, "选择适合你的等级，开始挑战！",
                  20, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 140, center=True)
        draw_divider(surface, 80, 166, SCREEN_WIDTH - 80)

    def _draw_cards(self, surface):
        for i, c in enumerate(self.cards):
            hover = (i == self.hover_idx)
            rect = c["rect"].inflate(0, 8) if hover else c["rect"]
            color = c["color"]

            # 卡片白底
            draw_card(surface, rect, bg=WHITE, radius=20, shadow=True)

            # 顶部色块
            top = pygame.Rect(rect.x, rect.y, rect.width, 80)
            pygame.draw.rect(surface, color, top, border_radius=20)
            pygame.draw.rect(surface, color,
                             (rect.x, rect.y + 60, rect.width, 20))

            cx = rect.centerx
            draw_text(surface, c["name"], 26, WHITE, cx, rect.y + 34,
                      center=True, bold=True)

            # 年级标签
            draw_text(surface, c["grade"], 18, color,
                      cx, rect.y + 112, center=True, bold=True)
            draw_text(surface, c["desc"], 16, COLOR_TEXT_SUB,
                      cx, rect.y + 142, center=True)

            # 底部提示
            draw_text(surface, "点击选择", 15, (190, 196, 216) if not hover else color,
                      cx, rect.bottom - 28, center=True)
