import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_divider, draw_star)
from src.utils.save_manager import get_leaderboard, get_records, get_best_record


# Tab 定义：(标签名, 类型)
TABS = [
    ("竞速排行", "speed_board"),
    ("消消乐榜", "falling_board"),
    ("闯关记录", "challenge_board"),
    ("学习记录", "records"),
]


class LeaderboardScene:
    def __init__(self, game):
        self.game = game
        self.tab = 0
        self.back_btn = pygame.Rect(20, 14, 88, 38)
        self._build_tab_btns()

    def _build_tab_btns(self):
        btn_w = 156
        gap = 10
        total_w = len(TABS) * btn_w + (len(TABS) - 1) * gap
        sx = (SCREEN_WIDTH - total_w) // 2
        self.tab_btns = [
            pygame.Rect(sx + i * (btn_w + gap), 96, btn_w, 40)
            for i in range(len(TABS))
        ]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_MENU)
                return
            for i, btn in enumerate(self.tab_btns):
                if btn.collidepoint(mx, my):
                    self.tab = i

    def update(self):
        pass

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        self._draw_header(surface)
        tab_type = TABS[self.tab][1]
        if tab_type == "speed_board":
            self._draw_score_board(surface, "speed", "竞速模式 Top 10")
        elif tab_type == "falling_board":
            self._draw_falling_board(surface)
        elif tab_type == "challenge_board":
            self._draw_challenge_board(surface)
        else:
            self._draw_records(surface)
        draw_button(surface, "← 返回", self.back_btn,
                    (180, 188, 205), WHITE, font_size=15, radius=10, shadow=False)

    # ------------------------------------------------------------------ #
    def _draw_header(self, surface):
        draw_text(surface, "排行榜", 40, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 50, center=True, bold=True)
        for i, (btn, (label, _)) in enumerate(zip(self.tab_btns, TABS)):
            sel = (i == self.tab)
            bg = COLOR_PRIMARY if sel else (230, 234, 244)
            tc = WHITE if sel else COLOR_TEXT_SUB
            draw_button(surface, label, btn, bg, tc,
                        font_size=16, radius=12, shadow=sel)
        draw_divider(surface, 60, 152, SCREEN_WIDTH - 60)

    # ------------------------------------------------------------------ #
    #  竞速排行榜
    # ------------------------------------------------------------------ #
    def _draw_score_board(self, surface, mode, title):
        board = get_leaderboard(mode)
        table = pygame.Rect(80, 168, SCREEN_WIDTH - 160, 500)
        draw_card(surface, table, bg=WHITE, radius=18, shadow=True)

        col_xs = [table.x + 70, table.x + 230, table.x + 400, table.x + 580]
        headers = ["排名", "昵称", "得分", "时间"]
        hy = table.y + 34
        for h, cx in zip(headers, col_xs):
            draw_text(surface, h, 17, COLOR_TEXT_SUB, cx, hy, center=True, bold=True)
        draw_divider(surface, table.x + 24, hy + 22, table.right - 24, (235, 238, 248))

        if not board:
            draw_text(surface, "暂无记录，快去挑战吧！",
                      22, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, table.centery, center=True)
            return

        rank_colors = [(255, 185, 0), (160, 168, 180), (200, 130, 60)]
        for i, entry in enumerate(board[:8]):
            ry = hy + 50 + i * 46
            if i % 2 == 0:
                stripe = pygame.Rect(table.x + 8, ry - 18, table.width - 16, 40)
                pygame.draw.rect(surface, (248, 250, 254), stripe, border_radius=8)
            rc = rank_colors[i] if i < 3 else COLOR_TEXT_SUB
            draw_text(surface, f"#{i+1}", 20, rc, col_xs[0], ry, center=True, bold=(i < 3))
            if i < 3:
                draw_star(surface, col_xs[0] - 26, ry, filled=True, size=10)
            draw_text(surface, entry["name"],  19, COLOR_TEXT_MAIN, col_xs[1], ry, center=True)
            draw_text(surface, f"{entry['score']}", 22, COLOR_PRIMARY,
                      col_xs[2], ry, center=True, bold=True)
            draw_text(surface, entry["time"][-5:], 16, COLOR_TEXT_SUB,
                      col_xs[3], ry, center=True)

    # ------------------------------------------------------------------ #
    #  消消乐榜：按年级+内容分组，显示最高分
    # ------------------------------------------------------------------ #
    def _draw_falling_board(self, surface):
        records = [r for r in get_records() if r.get("mode") == "falling"]
        table = pygame.Rect(60, 168, SCREEN_WIDTH - 120, 500)
        draw_card(surface, table, bg=WHITE, radius=18, shadow=True)

        if not records:
            draw_text(surface, "暂无消消乐记录，去玩一局吧！",
                      22, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, table.centery, center=True)
            return

        col_xs = [table.x + 60, table.x + 190, table.x + 320, table.x + 450,
                  table.x + 560, table.x + 660]
        headers = ["时间", "难度", "内容", "题数", "正确率", "得分"]
        hy = table.y + 34
        for h, cx in zip(headers, col_xs):
            draw_text(surface, h, 16, COLOR_TEXT_SUB, cx, hy, center=True, bold=True)
        draw_divider(surface, table.x + 20, hy + 22, table.right - 20, (235, 238, 248))

        shown = sorted(records, key=lambda r: r.get("score", 0), reverse=True)[:9]
        content_short = {
            "initials": "声母", "finals": "韵母", "whole": "整体认读",
            "syllables": "音节", "characters": "汉字", "words": "词语",
        }
        for i, rec in enumerate(shown):
            ry = hy + 48 + i * 40
            if i % 2 == 0:
                stripe = pygame.Rect(table.x + 8, ry - 16, table.width - 16, 36)
                pygame.draw.rect(surface, (248, 250, 254), stripe, border_radius=6)
            draw_text(surface, rec["time"][-5:], 14, COLOR_TEXT_SUB, col_xs[0], ry, center=True)
            draw_text(surface, LEVEL_NAMES.get(rec["level"], ""), 15, COLOR_TEXT_MAIN, col_xs[1], ry, center=True)
            draw_text(surface, content_short.get(rec.get("content_type", ""), ""), 15, COLOR_TEXT_MAIN, col_xs[2], ry, center=True)
            draw_text(surface, str(rec["total"]), 15, COLOR_TEXT_MAIN, col_xs[3], ry, center=True)
            acc_color = COLOR_SUCCESS if rec["accuracy"] >= 70 else COLOR_DANGER
            draw_text(surface, f"{rec['accuracy']}%", 15, acc_color, col_xs[4], ry, center=True, bold=True)
            draw_text(surface, str(rec["score"]), 18, COLOR_PRIMARY, col_xs[5], ry, center=True, bold=True)

    # ------------------------------------------------------------------ #
    #  闯关记录：显示各内容/难度的最高星数和最高分
    # ------------------------------------------------------------------ #
    def _draw_challenge_board(self, surface):
        records = [r for r in get_records() if r.get("mode") == "challenge"]
        table = pygame.Rect(60, 168, SCREEN_WIDTH - 120, 500)
        draw_card(surface, table, bg=WHITE, radius=18, shadow=True)

        if not records:
            draw_text(surface, "暂无闯关记录，去闯关吧！",
                      22, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, table.centery, center=True)
            return

        col_xs = [table.x + 60, table.x + 190, table.x + 320, table.x + 440,
                  table.x + 560, table.x + 660]
        headers = ["时间", "难度", "内容", "正确率", "星级", "得分"]
        hy = table.y + 34
        for h, cx in zip(headers, col_xs):
            draw_text(surface, h, 16, COLOR_TEXT_SUB, cx, hy, center=True, bold=True)
        draw_divider(surface, table.x + 20, hy + 22, table.right - 20, (235, 238, 248))

        shown = sorted(records, key=lambda r: r.get("score", 0), reverse=True)[:9]
        content_short = {
            "initials": "声母", "finals": "韵母", "whole": "整体认读",
            "syllables": "音节", "characters": "汉字", "words": "词语",
        }
        for i, rec in enumerate(shown):
            ry = hy + 48 + i * 40
            if i % 2 == 0:
                stripe = pygame.Rect(table.x + 8, ry - 16, table.width - 16, 36)
                pygame.draw.rect(surface, (248, 250, 254), stripe, border_radius=6)
            acc = rec.get("accuracy", 0)
            stars = 3 if acc >= 90 else (2 if acc >= 70 else (1 if acc >= 60 else 0))
            draw_text(surface, rec["time"][-5:], 14, COLOR_TEXT_SUB, col_xs[0], ry, center=True)
            draw_text(surface, LEVEL_NAMES.get(rec["level"], ""), 15, COLOR_TEXT_MAIN, col_xs[1], ry, center=True)
            draw_text(surface, content_short.get(rec.get("content_type", ""), ""), 15, COLOR_TEXT_MAIN, col_xs[2], ry, center=True)
            acc_color = COLOR_SUCCESS if acc >= 70 else COLOR_DANGER
            draw_text(surface, f"{acc}%", 15, acc_color, col_xs[3], ry, center=True, bold=True)
            # 星星图标
            for s in range(3):
                draw_star(surface, col_xs[4] - 20 + s * 18, ry, filled=(s < stars), size=8)
            draw_text(surface, str(rec["score"]), 18, COLOR_PRIMARY, col_xs[5], ry, center=True, bold=True)

    # ------------------------------------------------------------------ #
    #  学习总记录
    # ------------------------------------------------------------------ #
    def _draw_records(self, surface):
        records = list(reversed(get_records()[-10:]))
        table = pygame.Rect(60, 168, SCREEN_WIDTH - 120, 500)
        draw_card(surface, table, bg=WHITE, radius=18, shadow=True)

        col_xs = [table.x + 60, table.x + 175, table.x + 290, table.x + 390,
                  table.x + 500, table.x + 610]
        headers = ["时间", "模式", "难度", "题数", "正确率", "得分"]
        hy = table.y + 34
        for h, cx in zip(headers, col_xs):
            draw_text(surface, h, 16, COLOR_TEXT_SUB, cx, hy, center=True, bold=True)
        draw_divider(surface, table.x + 20, hy + 22, table.right - 20, (235, 238, 248))

        if not records:
            draw_text(surface, "暂无学习记录，开始你的第一局吧！",
                      22, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, table.centery, center=True)
            return

        mode_names = {"falling": "消消乐", "challenge": "闯关",
                      "speed": "竞速", "practice": "练习"}
        for i, rec in enumerate(records):
            ry = hy + 48 + i * 40
            if i % 2 == 0:
                stripe = pygame.Rect(table.x + 8, ry - 16, table.width - 16, 36)
                pygame.draw.rect(surface, (248, 250, 254), stripe, border_radius=6)
            draw_text(surface, rec["time"][-5:],  14, COLOR_TEXT_SUB,  col_xs[0], ry, center=True)
            draw_text(surface, mode_names.get(rec["mode"], rec["mode"]),
                      16, COLOR_TEXT_MAIN, col_xs[1], ry, center=True)
            draw_text(surface, LEVEL_NAMES.get(rec["level"], ""),
                      16, COLOR_TEXT_MAIN, col_xs[2], ry, center=True)
            draw_text(surface, str(rec["total"]),  16, COLOR_TEXT_MAIN, col_xs[3], ry, center=True)
            acc_color = COLOR_SUCCESS if rec["accuracy"] >= 70 else COLOR_DANGER
            draw_text(surface, f"{rec['accuracy']}%", 16, acc_color,   col_xs[4], ry, center=True, bold=True)
            draw_text(surface, str(rec["score"]),  18, COLOR_PRIMARY,  col_xs[5], ry, center=True, bold=True)
