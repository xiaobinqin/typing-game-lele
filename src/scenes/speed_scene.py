import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_input_box,
                                   draw_progress_bar, draw_background_gradient,
                                   draw_rounded_rect)
from src.utils.data_loader import build_quiz_pool
from src.utils.save_manager import save_record, save_leaderboard, get_leaderboard


class SpeedScene:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.pool = build_quiz_pool(
            self.game.selected_content,
            self.game.selected_level,
            count=100
        )
        self.idx = 0
        self.input_text = ""
        self.score = 0
        self.correct = 0
        self.total = 0
        self.combo = 0
        self.max_combo = 0
        self.time_left = SPEED_DURATION * FPS   # 帧数
        self.feedback = None
        self.finished = False
        self.name_input = ""
        self.name_saved = False
        self.back_btn = pygame.Rect(30, 30, 100, 44)

    @property
    def current(self):
        if self.idx < len(self.pool):
            return self.pool[self.idx]
        return None

    def _submit(self):
        if not self.input_text or self.current is None:
            return
        typed = self.input_text.strip().lower()
        answer = self.current["answer"].lower()
        self.total += 1
        if typed == answer:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            bonus = min(self.combo, 5)
            gained = 10 + bonus * 2
            self.score += gained
            self.correct += 1
            self.feedback = ("correct", f"✓ +{gained}" + ("  🔥连击x" + str(self.combo) if self.combo > 1 else ""), 35)
        else:
            self.combo = 0
            self.feedback = ("wrong", f"✗ 正确：{self.current['answer']}", 40)
        self.input_text = ""
        self.idx += 1
        if self.idx >= len(self.pool):
            self.idx = 0

    def handle_event(self, event):
        if self.finished:
            if event.type == pygame.KEYDOWN:
                if not self.name_saved:
                    if event.key == pygame.K_RETURN:
                        if self.name_input.strip():
                            save_leaderboard(self.name_input.strip(), self.score)
                            self.name_saved = True
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                    else:
                        ch = event.unicode
                        if ch and len(self.name_input) < 8:
                            self.name_input += ch
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self._retry_btn().collidepoint(mx, my):
                    self.reset()
                elif self._menu_btn().collidepoint(mx, my):
                    self.game.change_scene(SCENE_MENU)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_MENU)
                return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene(SCENE_MENU)
            else:
                ch = event.unicode
                if ch and ch.isalpha() and len(self.input_text) < 12:
                    self.input_text += ch.lower()

    def update(self):
        if self.finished:
            return
        if self.time_left > 0:
            self.time_left -= 1
        else:
            self.finished = True
            save_record("speed", self.game.selected_level,
                        self.game.selected_content,
                        self.total, self.correct, self.score)
        if self.feedback:
            kind, text, timer = self.feedback
            self.feedback = (kind, text, timer - 1) if timer > 1 else None

    def draw(self, surface):
        draw_background_gradient(surface, (220, 235, 255), (255, 235, 220),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)

        if self.finished:
            self._draw_result(surface)
            return

        secs_left = self.time_left // FPS
        # 时间条
        bar_color = COLOR_DANGER if secs_left <= 10 else COLOR_PRIMARY
        draw_progress_bar(surface, 100, 30, SCREEN_WIDTH - 200, 22,
                          self.time_left, SPEED_DURATION * FPS,
                          color_fill=bar_color)
        draw_text(surface, f"⏱ {secs_left}s", 30, bar_color,
                  SCREEN_WIDTH // 2, 62, center=True, bold=True)
        draw_text(surface, f"得分：{self.score}", 28, COLOR_PRIMARY,
                  80, 62, bold=True)
        if self.combo > 1:
            draw_text(surface, f"🔥 连击 x{self.combo}", 26, ORANGE,
                      SCREEN_WIDTH - 80, 62, center=False)

        # 题目
        current = self.current
        if current:
            card = pygame.Rect(SCREEN_WIDTH // 2 - 200, 130, 400, 160)
            pygame.draw.rect(surface, WHITE, card, border_radius=22)
            pygame.draw.rect(surface, COLOR_PRIMARY, card, 3, border_radius=22)
            draw_text(surface, current["display"], 80, COLOR_TEXT_MAIN,
                      SCREEN_WIDTH // 2, 210, center=True, bold=True)

        # 输入框
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 330, 480, 64)
        draw_input_box(surface, self.input_text, input_rect, font_size=36)
        draw_text(surface, "输入拼音后按 Enter 确认", 18, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 410, center=True)

        if self.feedback:
            kind, text, _ = self.feedback
            color = COLOR_SUCCESS if kind == "correct" else COLOR_DANGER
            draw_text(surface, text, 26, color,
                      SCREEN_WIDTH // 2, 455, center=True, bold=True)

        draw_text(surface, f"已答 {self.total}  正确 {self.correct}  最大连击 {self.max_combo}",
                  20, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, center=True)

        draw_button(surface, "← 退出", self.back_btn, GRAY, WHITE, font_size=19)

    def _draw_result(self, surface):
        draw_background_gradient(surface, (220, 240, 255), (255, 245, 200),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_text(surface, "时间到！", 60, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 120, center=True, bold=True)
        draw_text(surface, f"最终得分：{self.score}", 48, COLOR_SECONDARY,
                  SCREEN_WIDTH // 2, 200, center=True, bold=True)
        acc = round(self.correct / self.total * 100, 1) if self.total else 0
        draw_text(surface, f"答题 {self.total}  正确 {self.correct}  正确率 {acc}%  最大连击 {self.max_combo}",
                  24, COLOR_TEXT_MAIN, SCREEN_WIDTH // 2, 270, center=True)

        # 保存名字
        if not self.name_saved:
            draw_text(surface, "输入昵称上榜（按 Enter 确认）：", 24, COLOR_TEXT_SUB,
                      SCREEN_WIDTH // 2, 330, center=True)
            name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 360, 360, 52)
            draw_input_box(surface, self.name_input, name_rect, font_size=28)
        else:
            draw_text(surface, "✓ 已保存到排行榜！", 28, COLOR_SUCCESS,
                      SCREEN_WIDTH // 2, 370, center=True, bold=True)
            board = get_leaderboard("speed")
            draw_text(surface, "本地排行榜 Top 5：", 22, COLOR_TEXT_SUB,
                      SCREEN_WIDTH // 2, 420, center=True)
            for i, entry in enumerate(board[:5]):
                draw_text(surface,
                          f"#{i+1}  {entry['name']}   {entry['score']} 分   {entry['time']}",
                          20, COLOR_TEXT_MAIN,
                          SCREEN_WIDTH // 2, 452 + i * 28, center=True)

        draw_button(surface, "再来一局", self._retry_btn(), COLOR_PRIMARY, WHITE, font_size=26)
        draw_button(surface, "返回主菜单", self._menu_btn(), COLOR_SECONDARY, WHITE, font_size=26)

    def _retry_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 280, SCREEN_HEIGHT - 110, 240, 56)

    def _menu_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 40, SCREEN_HEIGHT - 110, 240, 56)
