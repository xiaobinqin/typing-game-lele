import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_divider, draw_badge, draw_rounded_rect)


MODES = [
    (SCENE_FALLING,   "消消乐",   "字从天降，打出拼音来消除",  (56, 132, 255)),
    (SCENE_CHALLENGE, "闯关模式", "20题答题，冲击三星评价",    (255, 155, 35)),
    (SCENE_SPEED,     "竞速模式", "60秒极速，冲击高分排行",    (215, 55, 105)),
    (SCENE_PRACTICE,  "练习模式", "无压力自由练习，打好基础",  (38, 178, 110)),
]

CONTENT_ITEMS = [
    (CONTENT_INITIALS,   "声母"),
    (CONTENT_FINALS,     "韵母"),
    (CONTENT_WHOLE,      "整体认读"),
    (CONTENT_SYLLABLES,  "音节"),
    (CONTENT_CHARACTERS, "汉字"),
    (CONTENT_WORDS,      "词语"),
]


class ModeSelectScene:
    def __init__(self, game):
        self.game = game
        self.hover_mode = -1
        self.hover_content = -1
        self.hover_speed = -1
        self.selected_content = 0
        self.selected_speed = getattr(game, "falling_speed_level", 1)
        self.mode_cards = self._build_mode_cards()
        self.content_btns = self._build_content_btns()
        self.speed_btns = self._build_speed_btns()
        self.back_btn = pygame.Rect(36, 28, 96, 40)

    def _build_mode_cards(self):
        card_w, card_h = 218, 140
        gap = 18
        total_w = len(MODES) * card_w + (len(MODES) - 1) * gap
        sx = (SCREEN_WIDTH - total_w) // 2
        y = 190
        cards = []
        for i, (scene, name, desc, color) in enumerate(MODES):
            x = sx + i * (card_w + gap)
            cards.append({
                "rect": pygame.Rect(x, y, card_w, card_h),
                "scene": scene, "name": name, "desc": desc, "color": color,
            })
        return cards

    def _build_content_btns(self):
        btn_w, btn_h = 112, 38
        gap = 12
        total_w = len(CONTENT_ITEMS) * btn_w + (len(CONTENT_ITEMS) - 1) * gap
        sx = (SCREEN_WIDTH - total_w) // 2
        y = 424
        btns = []
        for i, (ct, name) in enumerate(CONTENT_ITEMS):
            x = sx + i * (btn_w + gap)
            btns.append({"rect": pygame.Rect(x, y, btn_w, btn_h),
                         "content": ct, "name": name})
        return btns

    def _build_speed_btns(self):
        btn_w, btn_h = 106, 38
        gap = 14
        labels = list(FALLING_SPEED_NAMES.values())
        total_w = len(labels) * btn_w + (len(labels) - 1) * gap
        sx = (SCREEN_WIDTH - total_w) // 2
        y = 530
        btns = []
        for i, label in enumerate(labels):
            x = sx + i * (btn_w + gap)
            btns.append({"rect": pygame.Rect(x, y, btn_w, btn_h),
                         "level": i, "name": label,
                         "color": FALLING_SPEED_COLORS[i]})
        return btns

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_mode = -1
            self.hover_content = -1
            self.hover_speed = -1
            for i, c in enumerate(self.mode_cards):
                if c["rect"].collidepoint(mx, my):
                    self.hover_mode = i
            for i, b in enumerate(self.content_btns):
                if b["rect"].collidepoint(mx, my):
                    self.hover_content = i
            for i, b in enumerate(self.speed_btns):
                if b["rect"].collidepoint(mx, my):
                    self.hover_speed = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_GRADE_SELECT)
                return
            for i, b in enumerate(self.content_btns):
                if b["rect"].collidepoint(mx, my):
                    self.selected_content = i
            for i, b in enumerate(self.speed_btns):
                if b["rect"].collidepoint(mx, my):
                    self.selected_speed = i
                    self.game.falling_speed_level = i
            for c in self.mode_cards:
                if c["rect"].collidepoint(mx, my):
                    ct = CONTENT_ITEMS[self.selected_content][0]
                    self.game.selected_content = ct
                    self.game.falling_speed_level = self.selected_speed
                    self.game.change_scene(c["scene"])

    def update(self):
        pass

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        self._draw_header(surface)
        self._draw_mode_cards(surface)
        self._draw_settings(surface)
        draw_button(surface, "← 返回", self.back_btn,
                    (180, 188, 205), WHITE, font_size=17, radius=10, shadow=False)

    def _draw_header(self, surface):
        level_name = LEVEL_NAMES.get(self.game.selected_level, "")
        draw_text(surface, "选择游戏模式", 42, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 86, center=True, bold=True)
        draw_badge(surface, level_name, SCREEN_WIDTH // 2, 126,
                   COLOR_PRIMARY, WHITE, font_size=16)
        draw_divider(surface, 80, 155, SCREEN_WIDTH - 80)

    def _draw_mode_cards(self, surface):
        for i, c in enumerate(self.mode_cards):
            hover = (i == self.hover_mode)
            rect = c["rect"].inflate(0, hover * 6)
            color = c["color"]

            draw_card(surface, rect, bg=WHITE, radius=16, shadow=True)
            # 左侧色条
            bar = pygame.Rect(rect.x, rect.y, 6, rect.height)
            pygame.draw.rect(surface, color, bar,
                             border_radius=16)

            cx = rect.x + rect.width // 2 + 3
            draw_text(surface, c["name"], 24, color,
                      rect.x + 26, rect.y + 36, bold=True)
            draw_text(surface, c["desc"], 16, COLOR_TEXT_SUB,
                      rect.x + 26, rect.y + 72)
            # 底部箭头提示
            draw_text(surface, "点击进入  →", 14,
                      color if hover else (200, 205, 220),
                      rect.right - 16, rect.bottom - 22,
                      center=False)

    def _draw_settings(self, surface):
        # 内容类型
        draw_text(surface, "练习内容", 18, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 396, center=True, bold=True)
        for i, b in enumerate(self.content_btns):
            sel = (i == self.selected_content)
            hover = (i == self.hover_content)
            bg = COLOR_PRIMARY if sel else (WHITE if hover else (240, 242, 248))
            tc = WHITE if sel else (COLOR_TEXT_MAIN if hover else COLOR_TEXT_SUB)
            border = COLOR_PRIMARY if not sel and hover else None
            draw_button(surface, b["name"], b["rect"], bg, tc,
                        font_size=16, radius=10, hover=False,
                        border_color=border, shadow=sel)

        # 消消乐速度
        draw_text(surface, "消消乐速度", 18, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 502, center=True, bold=True)
        for i, b in enumerate(self.speed_btns):
            sel = (i == self.selected_speed)
            hover = (i == self.hover_speed)
            bg = b["color"] if sel else (WHITE if hover else (240, 242, 248))
            tc = WHITE if sel else (COLOR_TEXT_MAIN if hover else COLOR_TEXT_SUB)
            draw_button(surface, b["name"], b["rect"], bg, tc,
                        font_size=16, radius=10, hover=False, shadow=sel)
