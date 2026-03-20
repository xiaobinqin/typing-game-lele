import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_gradient,
                                   draw_rounded_rect)


MODES = [
    {
        "scene":  SCENE_FALLING,
        "name":   "消消乐",
        "desc":   "汉字从天而降\n快速打出拼音消除",
        "color":  (72, 154, 255),
    },
    {
        "scene":  SCENE_CHALLENGE,
        "name":   "闯关模式",
        "desc":   "20题闯关\n全力冲击三星评价",
        "color":  (255, 150, 50),
    },
    {
        "scene":  SCENE_SPEED,
        "name":   "竞速模式",
        "desc":   "60秒极速挑战\n冲击高分排行",
        "color":  (220, 60, 120),
    },
    {
        "scene":  SCENE_PRACTICE,
        "name":   "练习模式",
        "desc":   "无压力自由练习\n巩固拼音汉字",
        "color":  (60, 185, 120),
    },
]

CONTENT_ITEMS = [
    (CONTENT_INITIALS,   "声母练习"),
    (CONTENT_FINALS,     "韵母练习"),
    (CONTENT_WHOLE,      "整体认读"),
    (CONTENT_SYLLABLES,  "拼音音节"),
    (CONTENT_CHARACTERS, "汉字拼音"),
    (CONTENT_WORDS,      "词语练习"),
]


class ModeSelectScene:
    def __init__(self, game):
        self.game = game
        self.hover_mode = -1
        self.hover_content = -1
        self.hover_speed = -1
        self.selected_content = 0
        self.selected_speed = getattr(game, "falling_speed_level", 1)
        self.mode_buttons = self._build_mode_buttons()
        self.content_buttons = self._build_content_buttons()
        self.speed_buttons = self._build_speed_buttons()
        self.back_btn = pygame.Rect(30, 30, 100, 44)

    def _build_mode_buttons(self):
        card_w, card_h = 210, 160
        gap = 20
        total_w = len(MODES) * card_w + (len(MODES) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        y = 270
        buttons = []
        for i, m in enumerate(MODES):
            x = start_x + i * (card_w + gap)
            buttons.append({**m, "rect": pygame.Rect(x, y, card_w, card_h)})
        return buttons

    def _build_content_buttons(self):
        btn_w, btn_h = 140, 42
        gap = 12
        total_w = len(CONTENT_ITEMS) * btn_w + (len(CONTENT_ITEMS) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        y = 508
        buttons = []
        for i, (ct, name) in enumerate(CONTENT_ITEMS):
            x = start_x + i * (btn_w + gap)
            buttons.append({
                "rect":    pygame.Rect(x, y, btn_w, btn_h),
                "content": ct,
                "name":    name,
            })
        return buttons

    def _build_speed_buttons(self):
        btn_w, btn_h = 110, 40
        gap = 16
        labels = list(FALLING_SPEED_NAMES.values())
        total_w = len(labels) * btn_w + (len(labels) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        y = 620
        buttons = []
        for i, label in enumerate(labels):
            x = start_x + i * (btn_w + gap)
            buttons.append({
                "rect":  pygame.Rect(x, y, btn_w, btn_h),
                "level": i,
                "name":  label,
                "color": FALLING_SPEED_COLORS[i],
            })
        return buttons

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_mode = -1
            self.hover_content = -1
            self.hover_speed = -1
            for i, btn in enumerate(self.mode_buttons):
                if btn["rect"].collidepoint(mx, my):
                    self.hover_mode = i
            for i, btn in enumerate(self.content_buttons):
                if btn["rect"].collidepoint(mx, my):
                    self.hover_content = i
            for i, btn in enumerate(self.speed_buttons):
                if btn["rect"].collidepoint(mx, my):
                    self.hover_speed = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_GRADE_SELECT)
                return
            for i, btn in enumerate(self.content_buttons):
                if btn["rect"].collidepoint(mx, my):
                    self.selected_content = i
            for i, btn in enumerate(self.speed_buttons):
                if btn["rect"].collidepoint(mx, my):
                    self.selected_speed = i
                    self.game.falling_speed_level = i
            for btn in self.mode_buttons:
                if btn["rect"].collidepoint(mx, my):
                    content_type = CONTENT_ITEMS[self.selected_content][0]
                    self.game.selected_content = content_type
                    self.game.falling_speed_level = self.selected_speed
                    self.game.change_scene(btn["scene"])

    def update(self):
        pass

    def draw(self, surface):
        draw_background_gradient(surface, (220, 240, 255), (255, 240, 220),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)
        level_name = LEVEL_NAMES.get(self.game.selected_level, "")
        draw_text(surface, f"选择游戏模式  [{level_name}]", 44, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 90, center=True, bold=True)

        # 模式卡片
        for i, btn in enumerate(self.mode_buttons):
            hover = (i == self.hover_mode)
            color = btn["color"]
            rect = btn["rect"].inflate(8, 8) if hover else btn["rect"]
            pygame.draw.rect(surface, color, rect, border_radius=18)
            cx, cy = rect.centerx, rect.centery
            draw_text(surface, btn["name"], 28, WHITE, cx, cy - 34, center=True, bold=True)
            for j, line in enumerate(btn["desc"].split("\n")):
                draw_text(surface, line, 17, WHITE, cx, cy + 4 + j * 22, center=True)

        # 内容类型
        draw_text(surface, "选择练习内容类型：", 22, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 472, center=True)
        for i, btn in enumerate(self.content_buttons):
            selected = (i == self.selected_content)
            hover = (i == self.hover_content)
            bg = COLOR_PRIMARY if selected else (200, 215, 240)
            tc = WHITE if selected else COLOR_TEXT_MAIN
            draw_button(surface, btn["name"], btn["rect"], bg, tc,
                        font_size=18, hover=hover and not selected)

        # 消消乐速度选择
        draw_text(surface, "消消乐下落速度：", 22, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 588, center=True)
        for i, btn in enumerate(self.speed_buttons):
            selected = (i == self.selected_speed)
            hover = (i == self.hover_speed)
            bg = btn["color"] if selected else (210, 220, 230)
            tc = WHITE if selected else COLOR_TEXT_MAIN
            border = btn["color"] if not selected else None
            draw_button(surface, btn["name"], btn["rect"], bg, tc,
                        font_size=18, hover=hover and not selected,
                        border_color=border)

        # 返回
        draw_button(surface, "← 返回", self.back_btn, GRAY, WHITE, font_size=20)
