import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_divider, draw_badge, draw_shadow_rect)


LEVEL_ITEMS = [
    (LEVEL_STARTER,  "启蒙级", "一年级",   "拼音起步",     "声母·韵母·认读",   (56, 132, 255)),
    (LEVEL_BASIC,    "基础级", "二年级",   "拼音巩固",     "音节·汉字拼音",    (40, 185, 115)),
    (LEVEL_MIDDLE,   "进阶级", "三四年级", "汉字进阶",     "汉字·词语积累",    (255, 160, 30)),
    (LEVEL_ADVANCED, "熟练级", "五六年级", "词语积累",     "词语·综合练习",    (220, 70, 100)),
]


class GradeSelectScene:
    def __init__(self, game):
        self.game = game
        self.hover_idx = -1
        # 恢复上次选中的年级高亮
        self.selected_idx = self._level_to_idx(game.selected_level)
        self.cards = self._build_cards()
        self.back_btn = pygame.Rect(36, 28, 96, 40)

    def _level_to_idx(self, level):
        for i, (lv, *_) in enumerate(LEVEL_ITEMS):
            if lv == level:
                return i
        return -1

    def _build_cards(self):
        card_w, card_h = 210, 240
        gap = 22
        total_w = len(LEVEL_ITEMS) * card_w + (len(LEVEL_ITEMS) - 1) * gap
        sx = (SCREEN_WIDTH - total_w) // 2
        y = SCREEN_HEIGHT // 2 - card_h // 2 + 28
        cards = []
        for i, (level, name, grade, tag, content, color) in enumerate(LEVEL_ITEMS):
            x = sx + i * (card_w + gap)
            cards.append({
                "rect": pygame.Rect(x, y, card_w, card_h),
                "level": level, "name": name, "grade": grade,
                "tag": tag, "content": content, "color": color,
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
            for i, c in enumerate(self.cards):
                if c["rect"].collidepoint(mx, my):
                    self.selected_idx = i
                    self.game.selected_level = c["level"]
                    # 重置模式选择页的模式选中记录（换年级后重新选）
                    self.game.selected_mode_idx = -1
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
                  SCREEN_WIDTH // 2, 88, center=True, bold=True)
        draw_text(surface, "选择适合你的等级，循序渐进，打好基础！",
                  19, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 138, center=True)
        draw_divider(surface, 80, 164, SCREEN_WIDTH - 80)

    def _draw_cards(self, surface):
        for i, c in enumerate(self.cards):
            hover    = (i == self.hover_idx)
            selected = (i == self.selected_idx)
            color    = c["color"]

            # 选中/悬停时卡片上移
            shift = 10 if selected else (6 if hover else 0)
            rect  = c["rect"].move(0, -shift)

            # 选中态：浅色背景 + 彩色边框
            if selected:
                bg_color = tuple(min(255, v + 195) for v in color)
                draw_card(surface, rect, bg=bg_color, radius=20, shadow=True)
                pygame.draw.rect(surface, color, rect, width=3, border_radius=20)
            else:
                draw_card(surface, rect, bg=WHITE, radius=20, shadow=True)

            cx = rect.centerx

            # ---- 顶部色块 ----
            top_h = 88
            top = pygame.Rect(rect.x, rect.y, rect.width, top_h)
            pygame.draw.rect(surface, color, top, border_radius=20)
            # 色块底部补齐（消除圆角缺口）
            pygame.draw.rect(surface, color,
                             (rect.x, rect.y + top_h - 20, rect.width, 20))

            # 级别名
            draw_text(surface, c["name"], 28, WHITE,
                      cx, rect.y + 42, center=True, bold=True)

            # ---- 卡片内容区 ----
            # 年级 badge
            draw_badge(surface, c["grade"], cx, rect.y + top_h + 26,
                       color, WHITE, font_size=14)

            # 标签文字（如"拼音起步"）
            draw_text(surface, c["tag"], 20, COLOR_TEXT_MAIN,
                      cx, rect.y + top_h + 64, center=True, bold=True)

            # 内容说明（小字）
            draw_text(surface, c["content"], 14, COLOR_TEXT_SUB,
                      cx, rect.y + top_h + 92, center=True)

            # 底部提示
            if selected:
                hint_text  = "当前选择 ✓"
                hint_color = color
            elif hover:
                hint_text  = "点击进入 →"
                hint_color = color
            else:
                hint_text  = "点击选择"
                hint_color = (190, 196, 218)
            draw_text(surface, hint_text, 15, hint_color,
                      cx, rect.bottom - 22, center=True, bold=selected)
