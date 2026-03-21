import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_star, draw_input_box,
                                   draw_progress_bar, draw_divider)
from src.utils.data_loader import build_quiz_pool
from src.utils.save_manager import save_record


class ChallengeScene:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.pool = build_quiz_pool(self.game.selected_content,
                                    self.game.selected_level,
                                    count=CHALLENGE_TOTAL)
        self.idx = 0
        self.input_text = ""
        self.correct = 0
        self.wrong_items = []
        self.feedback = None
        self.finished = False
        self.score = 0
        self.stars = 0
        self.back_btn = pygame.Rect(20, 14, 88, 38)

    @property
    def current(self):
        return self.pool[self.idx] if self.idx < len(self.pool) else None

    def _submit(self):
        if not self.input_text or self.current is None:
            return
        typed = self.input_text.strip().lower()
        answer = self.current["answer"].lower()
        if typed == answer:
            self.correct += 1
            self.score += 10
            self.feedback = ("correct", f"正确！答案：{self.current['answer']}", 45)
        else:
            self.wrong_items.append({
                "display": self.current["display"],
                "answer":  self.current["answer"],
                "typed":   typed,
            })
            self.feedback = ("wrong", f"正确答案：{self.current['answer']}", 55)
        self.input_text = ""
        self.idx += 1
        if self.idx >= len(self.pool):
            self._finish()

    def _finish(self):
        self.finished = True
        total = len(self.pool)
        acc = self.correct / total if total else 0
        self.stars = 3 if acc >= 0.9 else (2 if acc >= 0.7 else (1 if acc >= CHALLENGE_PASS_RATE else 0))
        save_record("challenge", self.game.selected_level,
                    self.game.selected_content, total, self.correct, self.score)

    def handle_event(self, event):
        if self.finished:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self._retry_btn().collidepoint(mx, my):
                    self.reset()
                elif self._menu_btn().collidepoint(mx, my):
                    self.game.change_scene(SCENE_MODE_SELECT)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.collidepoint(*event.pos):
                self.game.change_scene(SCENE_MODE_SELECT)
                return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene(SCENE_MODE_SELECT)
            else:
                ch = event.unicode
                if ch and ch.isalpha() and len(self.input_text) < 16:
                    self.input_text += ch.lower()

    def update(self):
        if self.feedback:
            k, t, n = self.feedback
            self.feedback = (k, t, n - 1) if n > 1 else None

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)

        if self.finished:
            self._draw_result(surface)
            return

        self._draw_header(surface)
        self._draw_question(surface)
        self._draw_input_area(surface)

        draw_button(surface, "退出", self.back_btn,
                    (180, 188, 205), WHITE, font_size=15, radius=10, shadow=False)

    def _draw_header(self, surface):
        total = len(self.pool)
        # 进度条
        pygame.draw.rect(surface, WHITE, (0, 0, SCREEN_WIDTH, 68))
        pygame.draw.line(surface, COLOR_BORDER, (0, 68), (SCREEN_WIDTH, 68), 1)
        draw_progress_bar(surface, 120, 26, SCREEN_WIDTH - 240, 16,
                          self.idx, total, color_fill=COLOR_PRIMARY)
        draw_text(surface, f"{self.idx} / {total}", 15, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 48, center=True)
        draw_text(surface, f"得分  {self.score}", 18, COLOR_PRIMARY,
                  SCREEN_WIDTH - 120, 34, center=True, bold=True)

    def _draw_question(self, surface):
        current = self.current
        if not current:
            return
        # 大题目卡片
        card = pygame.Rect(SCREEN_WIDTH // 2 - 220, 110, 440, 200)
        draw_card(surface, card, bg=WHITE, radius=22, shadow=True)

        draw_text(surface, "请输入拼音", 18, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 138, center=True)
        draw_divider(surface, card.x + 30, 164, card.right - 30, (235, 238, 248))

        # 自适应字号
        fs = 76 if len(current["display"]) <= 2 else 52
        draw_text(surface, current["display"], fs, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 222, center=True, bold=True)

        # 反馈
        if self.feedback:
            k, text, _ = self.feedback
            fg = COLOR_SUCCESS if k == "correct" else COLOR_DANGER
            bg = (235, 252, 242) if k == "correct" else (255, 240, 240)
            fb_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 328, 400, 44)
            pygame.draw.rect(surface, bg, fb_rect, border_radius=10)
            draw_text(surface, text, 20, fg,
                      SCREEN_WIDTH // 2, 350, center=True, bold=True)

    def _draw_input_area(self, surface):
        pygame.draw.rect(surface, WHITE,
                         (0, SCREEN_HEIGHT - 130, SCREEN_WIDTH, 130))
        pygame.draw.line(surface, COLOR_BORDER,
                         (0, SCREEN_HEIGHT - 130), (SCREEN_WIDTH, SCREEN_HEIGHT - 130), 1)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT - 112, 520, 58)
        draw_input_box(surface, self.input_text, input_rect, font_size=34)
        draw_text(surface, "输入拼音后按 Enter 确认",
                  15, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 26, center=True)

        wrong_n = self.idx - self.correct
        draw_text(surface, f"正确 {self.correct}", 17, COLOR_SUCCESS,
                  SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 148, center=True)
        draw_text(surface, f"错误 {wrong_n}", 17, COLOR_DANGER,
                  SCREEN_WIDTH // 2 + 90, SCREEN_HEIGHT - 148, center=True)

    def _draw_result(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        card = pygame.Rect(SCREEN_WIDTH // 2 - 300, 90, 600, 460)
        draw_card(surface, card, bg=WHITE, radius=24, shadow=True)

        passed = self.stars > 0
        title_color = COLOR_SUCCESS if passed else COLOR_DANGER
        draw_text(surface, "恭喜通关！" if passed else "本次未通关",
                  46, title_color, SCREEN_WIDTH // 2, 160, center=True, bold=True)

        # 星级
        for i in range(3):
            draw_star(surface, SCREEN_WIDTH // 2 - 60 + i * 60, 228,
                      filled=(i < self.stars), size=26)

        total = len(self.pool)
        acc = round(self.correct / total * 100, 1) if total else 0
        draw_text(surface, f"{self.score}", 64, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 304, center=True, bold=True)
        draw_text(surface, "分", 20, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2 + 54, 322)
        draw_text(surface, f"共 {total} 题  ·  正确 {self.correct} 题  ·  正确率 {acc}%",
                  19, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 360, center=True)

        if self.wrong_items:
            draw_divider(surface, card.x + 40, 390, card.right - 40, (235, 238, 248))
            draw_text(surface, "错题回顾", 17, COLOR_DANGER,
                      SCREEN_WIDTH // 2, 412, center=True, bold=True)
            for i, w in enumerate(self.wrong_items[:4]):
                line = f"{w['display']}  →  正确：{w['answer']}    你答：{w['typed']}"
                draw_text(surface, line, 16, COLOR_TEXT_SUB,
                          SCREEN_WIDTH // 2, 438 + i * 24, center=True)

        draw_button(surface, "再来一关", self._retry_btn(),
                    COLOR_PRIMARY, WHITE, font_size=22, radius=14)
        draw_button(surface, "返回选择", self._menu_btn(),
                    (180, 188, 205), WHITE, font_size=22, radius=14)

    def _retry_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 290, 584, 256, 52)

    def _menu_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 34, 584, 256, 52)
