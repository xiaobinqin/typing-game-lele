import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_rounded_rect,
                                   draw_background_gradient, draw_star)
from src.utils.save_manager import get_leaderboard, get_records


class LeaderboardScene:
    def __init__(self, game):
        self.game = game
        self.tab = 0   # 0=竞速排行 1=学习记录
        self.back_btn = pygame.Rect(30, 30, 100, 44)
        self.tab_btns = [
            pygame.Rect(SCREEN_WIDTH // 2 - 160, 100, 140, 44),
            pygame.Rect(SCREEN_WIDTH // 2 + 20,  100, 140, 44),
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
        draw_background_gradient(surface, (225, 240, 255), (255, 245, 215),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_text(surface, "排行榜 & 学习记录", 46, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 50, center=True, bold=True)

        labels = ["竞速排行", "学习记录"]
        for i, (btn, label) in enumerate(zip(self.tab_btns, labels)):
            bg = COLOR_PRIMARY if i == self.tab else LIGHT_GRAY
            tc = WHITE if i == self.tab else COLOR_TEXT_MAIN
            draw_button(surface, label, btn, bg, tc, font_size=22)

        if self.tab == 0:
            self._draw_speed_board(surface)
        else:
            self._draw_records(surface)

        draw_button(surface, "← 返回", self.back_btn, GRAY, WHITE, font_size=19)

    def _draw_speed_board(self, surface):
        board = get_leaderboard("speed")
        start_y = 175
        col_headers = ["排名", "昵称", "得分", "时间"]
        col_xs = [160, 360, 560, 760]

        for i, (header, x) in enumerate(zip(col_headers, col_xs)):
            draw_text(surface, header, 22, COLOR_TEXT_SUB, x, start_y, center=True)
        pygame.draw.line(surface, LIGHT_GRAY,
                         (100, start_y + 28), (SCREEN_WIDTH - 100, start_y + 28), 1)

        if not board:
            draw_text(surface, "暂无记录，快去竞速模式挑战吧！", 28, COLOR_TEXT_SUB,
                      SCREEN_WIDTH // 2, 380, center=True)
            return

        rank_colors = [(255, 200, 0), (180, 180, 180), (200, 140, 80)]
        for i, entry in enumerate(board[:10]):
            y = start_y + 50 + i * 46
            if i % 2 == 0:
                pygame.draw.rect(surface, (240, 245, 255),
                                 (100, y - 16, SCREEN_WIDTH - 200, 40), border_radius=8)
            rc = rank_colors[i] if i < 3 else COLOR_TEXT_MAIN
            draw_text(surface, f"#{i+1}", 24, rc, col_xs[0], y, center=True, bold=(i < 3))
            draw_text(surface, entry["name"],  22, COLOR_TEXT_MAIN, col_xs[1], y, center=True)
            draw_text(surface, str(entry["score"]), 24, COLOR_PRIMARY, col_xs[2], y, center=True, bold=True)
            draw_text(surface, entry["time"],   18, COLOR_TEXT_SUB, col_xs[3], y, center=True)

    def _draw_records(self, surface):
        records = get_records()
        records = list(reversed(records[-10:]))
        start_y = 175

        headers = ["时间", "模式", "难度", "题数", "正确率", "得分"]
        col_xs = [120, 230, 330, 450, 570, 700]

        for header, x in zip(headers, col_xs):
            draw_text(surface, header, 20, COLOR_TEXT_SUB, x, start_y, center=True)
        pygame.draw.line(surface, LIGHT_GRAY,
                         (60, start_y + 26), (SCREEN_WIDTH - 60, start_y + 26), 1)

        if not records:
            draw_text(surface, "暂无学习记录，开始你的第一局吧！", 28, COLOR_TEXT_SUB,
                      SCREEN_WIDTH // 2, 380, center=True)
            return

        mode_names = {"falling": "消消乐", "challenge": "闯关", "speed": "竞速", "practice": "练习"}
        for i, rec in enumerate(records):
            y = start_y + 44 + i * 40
            if i % 2 == 0:
                pygame.draw.rect(surface, (245, 248, 255),
                                 (60, y - 14, SCREEN_WIDTH - 120, 36), border_radius=6)
            draw_text(surface, rec["time"][-5:], 17, COLOR_TEXT_SUB, col_xs[0], y, center=True)
            draw_text(surface, mode_names.get(rec["mode"], rec["mode"]), 18, COLOR_TEXT_MAIN, col_xs[1], y, center=True)
            draw_text(surface, LEVEL_NAMES.get(rec["level"], ""), 18, COLOR_TEXT_MAIN, col_xs[2], y, center=True)
            draw_text(surface, str(rec["total"]), 18, COLOR_TEXT_MAIN, col_xs[3], y, center=True)
            draw_text(surface, f"{rec['accuracy']}%", 18, COLOR_SUCCESS, col_xs[4], y, center=True)
            draw_text(surface, str(rec["score"]), 18, COLOR_PRIMARY, col_xs[5], y, center=True, bold=True)
