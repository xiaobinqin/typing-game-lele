import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_divider, draw_badge, draw_rounded_rect)
from src.utils.save_manager import get_best_record


MODES = [
    (SCENE_FALLING,   "消消乐",   "字从天降，打出拼音来消除",  (56, 132, 255)),
    (SCENE_CHALLENGE, "闯关模式", "20题答题，冲击三星评价",    (255, 155, 35)),
    (SCENE_SPEED,     "竞速模式", "60秒极速，冲击高分排行",    (215, 55, 105)),
    (SCENE_PRACTICE,  "练习模式", "无压力自由练习，打好基础",  (38, 178, 110)),
]

# 每组：(组标题, [(content_type, 按钮名), ...])
CONTENT_GROUPS = [
    ("拼音基础", [
        (CONTENT_INITIALS,  "声母"),
        (CONTENT_FINALS,    "韵母"),
    ]),
    ("拼读练习", [
        (CONTENT_WHOLE,     "整体认读"),
        (CONTENT_SYLLABLES, "音节"),
    ]),
    ("字词学习", [
        (CONTENT_CHARACTERS, "汉字"),
        (CONTENT_WORDS,      "词语"),
    ]),
]

# 展开为顺序列表（与原 selected_content 索引对齐）
CONTENT_ITEMS = [item for _, items in CONTENT_GROUPS for item in items]


class ModeSelectScene:
    def __init__(self, game):
        self.game = game
        self.hover_mode = -1
        self.hover_content = -1
        # 从 game 恢复上次选中项，保证返回时状态不丢失
        self.selected_content = getattr(game, "selected_content_idx", 0)
        self.selected_mode = getattr(game, "selected_mode_idx", -1)
        self.mode_cards = self._build_mode_cards()
        self.content_btns = self._build_content_btns()
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
        """
        3组，每组内2个按钮并排，组间留更大间距。
        组框高度 = 标题区(24px) + 间距(8px) + 按钮高(40px) + 内边距(12px)*2 = 96px
        按钮 y = 框顶 + 标题区 + 间距 + 上内边距
        """
        btn_w, btn_h = 110, 40
        btn_gap = 10           # 组内按钮间距
        group_inner_w = 240    # 每组宽（含两按钮 + 间距）
        group_gap = 28         # 组间间距
        total_groups = len(CONTENT_GROUPS)
        total_w = total_groups * group_inner_w + (total_groups - 1) * group_gap
        sx = (SCREEN_WIDTH - total_w) // 2

        # 框顶 y（在"练习内容"标题下方留空）
        frame_top = 442
        btn_y = frame_top + 34   # 标题区26px + 上内边距8px

        btns = []
        flat_idx = 0
        for gi, (_, items) in enumerate(CONTENT_GROUPS):
            gx = sx + gi * (group_inner_w + group_gap)
            for bi, (ct, name) in enumerate(items):
                x = gx + bi * (btn_w + btn_gap)
                btns.append({
                    "rect": pygame.Rect(x, btn_y, btn_w, btn_h),
                    "content": ct,
                    "name": name,
                    "flat_idx": flat_idx,
                    "group_idx": gi,
                })
                flat_idx += 1
        return btns

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_mode = -1
            self.hover_content = -1
            for i, c in enumerate(self.mode_cards):
                if c["rect"].collidepoint(mx, my):
                    self.hover_mode = i
            for i, b in enumerate(self.content_btns):
                if b["rect"].collidepoint(mx, my):
                    self.hover_content = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_GRADE_SELECT)
                return
            for i, b in enumerate(self.content_btns):
                if b["rect"].collidepoint(mx, my):
                    self.selected_content = b["flat_idx"]
                    self.game.selected_content_idx = b["flat_idx"]  # 持久化选中项
            for i, c in enumerate(self.mode_cards):
                if c["rect"].collidepoint(mx, my):
                    ct = CONTENT_ITEMS[self.selected_content][0]
                    self.game.selected_content = ct
                    self.game.selected_content_idx = self.selected_content
                    self.game.selected_mode_idx = i   # 记住选中的模式
                    self.game.change_scene(c["scene"])

    def update(self):
        pass

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        self._draw_header(surface)
        self._draw_mode_cards(surface)
        self._draw_content_groups(surface)
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
        # 模式名 -> save_manager 中的 mode key
        mode_keys = {
            SCENE_FALLING:   "falling",
            SCENE_CHALLENGE: "challenge",
            SCENE_SPEED:     "speed",
            SCENE_PRACTICE:  None,
        }
        for i, c in enumerate(self.mode_cards):
            hover = (i == self.hover_mode)
            selected = (i == self.selected_mode)
            rect = c["rect"].inflate(0, hover * 6)
            color = c["color"]

            if selected:
                bg_color = tuple(min(255, v + 200) for v in color)
                draw_card(surface, rect, bg=bg_color, radius=16, shadow=True)
                pygame.draw.rect(surface, color, rect, width=3, border_radius=16)
            else:
                draw_card(surface, rect, bg=WHITE, radius=16, shadow=True)

            bar = pygame.Rect(rect.x, rect.y, 6, rect.height)
            pygame.draw.rect(surface, color, bar, border_radius=16)

            draw_text(surface, c["name"], 24, color,
                      rect.x + 26, rect.y + 30, bold=True)
            draw_text(surface, c["desc"], 15, COLOR_TEXT_SUB,
                      rect.x + 26, rect.y + 64)

            # 历史最佳成绩
            mk = mode_keys.get(c["scene"])
            if mk:
                best = get_best_record(mk,
                                       level=self.game.selected_level,
                                       content_type=CONTENT_ITEMS[self.selected_content][0])
                if best:
                    best_txt = f"最高 {best['score']} 分"
                    draw_text(surface, best_txt, 13, color,
                              rect.x + 26, rect.y + 92)

            hint_color = color if (hover or selected) else (200, 205, 220)
            hint_text = "上次选择 ✓" if (selected and not hover) else "点击进入 →"
            draw_text(surface, hint_text, 13, hint_color,
                      rect.centerx, rect.bottom - 18, center=True)

    def _draw_content_groups(self, surface):
        """绘制3组练习内容选择按钮：每组有独立背景框，标题在框顶，按钮在框内"""
        draw_text(surface, "练习内容", 18, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 418, center=True, bold=True)

        group_inner_w = 240
        group_gap = 28
        total_w = len(CONTENT_GROUPS) * group_inner_w + (len(CONTENT_GROUPS) - 1) * group_gap
        sx = (SCREEN_WIDTH - total_w) // 2

        frame_top = 442
        frame_h = 96   # 标题26 + 内边距8 + 按钮40 + 下内边距22

        # 先画每组背景框 + 标题（在按钮下层）
        for gi, (group_title, _) in enumerate(CONTENT_GROUPS):
            gx = sx + gi * (group_inner_w + group_gap)
            bg_rect = pygame.Rect(gx - 8, frame_top, group_inner_w + 16, frame_h)
            pygame.draw.rect(surface, (235, 239, 250), bg_rect, border_radius=12)
            # 组标题居中显示在框顶部区域
            draw_text(surface, group_title, 13, COLOR_TEXT_SUB,
                      gx + group_inner_w // 2, frame_top + 14, center=True)

        # 再画按钮（在背景框上层，不被覆盖）
        for b in self.content_btns:
            sel = (b["flat_idx"] == self.selected_content)
            hover = (b["flat_idx"] == self.hover_content)
            bg = COLOR_PRIMARY if sel else (WHITE if hover else (255, 255, 255))
            tc = WHITE if sel else (COLOR_TEXT_MAIN if hover else COLOR_TEXT_SUB)
            border = COLOR_PRIMARY if not sel and hover else None
            draw_button(surface, b["name"], b["rect"], bg, tc,
                        font_size=16, radius=10, hover=False,
                        border_color=border, shadow=sel)
