import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_divider, draw_star)
from src.utils.save_manager import get_leaderboard, get_records


class LeaderboardScene:
    def __init__(self, game):
        self.game = game
        self.tab = 0
        self.back_btn = pygame.Rect(20, 14, 88, 38)
        self.tab_btns = [
            pygame.Rect(SCREEN_WIDTH // 2 - 156, 100, 140, 42),
            pygame.Rect(SCREEN_WIDTH // 2 + 16,  100, 140, 42),
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
        if self.tab == 0:
            self._draw_speed_board(surface)
        else:
            self._draw_records(surface)
        draw_button(surface, "← 返回", self.back_btn,
                    (180, 188, 205), WHITE, font_size=15, radius=10, shadow=False)

    def _draw_header(self, surface):
        draw_text(surface, "排行榜", 42, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 52, center=True, bold=True)
        labels = ["竞速排行", "学习记录"]
        for i, (btn, label) in enumerate(zip(self.tab_btns, labels)):
            sel = (i == self.tab)
            bg = COLOR_PRIMARY if sel else (230, 234, 244)
            tc = WHITE if sel else COLOR_TEXT_SUB
            draw_button(surface, label, btn, bg, tc,
                        font_size=18, radius=12, shadow=sel)
        draw_divider(surface, 60, 160, SCREEN_WIDTH - 60)

    def _draw_speed_board(self, surface):
        board = get_leaderboard("speed")
        table = pygame.Rect(80, 176, SCREEN_WIDTH - 160, 500)
        draw_card(surface, table, bg=WHITE, radius=18, shadow=True)

        col_xs = [table.x + 70, table.x + 230, table.x + 400, table.x + 580]
        headers = ["排名", "昵称", "得分", "时间"]
        hy = table.y + 34
        for h, cx in zip(headers, col_xs):
            draw_text(surface, h, 17, COLOR_TEXT_SUB, cx, hy, center=True, bold=True)
        draw_divider(surface, table.x + 24, hy + 22, table.right - 24, (235, 238, 248))

        if not board:
            draw_text(surface, "暂无记录，快去竞速模式挑战吧！",
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

    def _draw_records(self, surface):
        records = list(reversed(get_records()[-10:]))
        table = pygame.Rect(60, 176, SCREEN_WIDTH - 120, 500)
        draw_card(surface, table, bg=WHITE, radius=18, shadow=True)

        col_xs = [table.x + 70, table.x + 180, table.x + 290, table.x + 390,
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

            draw_text(surface, rec["time"][-5:],  15, COLOR_TEXT_SUB,  col_xs[0], ry, center=True)
            draw_text(surface, mode_names.get(rec["mode"], rec["mode"]),
                      16, COLOR_TEXT_MAIN, col_xs[1], ry, center=True)
            draw_text(surface, LEVEL_NAMES.get(rec["level"], ""),
                      16, COLOR_TEXT_MAIN, col_xs[2], ry, center=True)
            draw_text(surface, str(rec["total"]),  16, COLOR_TEXT_MAIN, col_xs[3], ry, center=True)
            acc_color = COLOR_SUCCESS if rec["accuracy"] >= 70 else COLOR_DANGER
            draw_text(surface, f"{rec['accuracy']}%", 16, acc_color,   col_xs[4], ry, center=True, bold=True)
            draw_text(surface, str(rec["score"]),  18, COLOR_PRIMARY,  col_xs[5], ry, center=True, bold=True)
