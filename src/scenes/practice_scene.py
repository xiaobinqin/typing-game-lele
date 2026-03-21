import pygame
import random
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_input_box, draw_divider)
from src.utils.data_loader import build_quiz_pool, normalize_pinyin
from src.utils.sound_manager import play as sfx


class PracticeScene:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.pool = build_quiz_pool(self.game.selected_content,
                                    self.game.selected_level, count=100)
        random.shuffle(self.pool)
        self.idx = 0
        self.input_text = ""
        self.feedback = None
        self.show_hint = False
        self.correct = 0
        self.total = 0
        self.back_btn = pygame.Rect(20, 14, 88, 38)
        self.hint_btn = pygame.Rect(SCREEN_WIDTH - 120, 14, 98, 38)

    @property
    def current(self):
        return self.pool[self.idx] if self.idx < len(self.pool) else None

    def _submit(self):
        if not self.input_text or self.current is None:
            return
        typed = normalize_pinyin(self.input_text.strip())
        answer = self.current["answer"]
        self.total += 1
        if typed == answer:
            self.correct += 1
            self.feedback = ("correct", f"正确！  答案：{self.current['answer']}", 90)
            sfx("correct")
        else:
            self.feedback = ("wrong",
                             f"正确答案：{self.current['answer']}（你输入：{typed}）", 110)
            sfx("wrong")
        self.input_text = ""
        self.show_hint = False

    def _go(self, delta):
        self.idx = (self.idx + delta) % len(self.pool)
        self.input_text = ""
        self.feedback = None
        self.show_hint = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_MODE_SELECT)
                return
            if self.hint_btn.collidepoint(mx, my):
                self.show_hint = not self.show_hint
                return
            if self._next_btn().collidepoint(mx, my):
                self._go(1)
                return
            if self._prev_btn().collidepoint(mx, my):
                self._go(-1)
                return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.feedback:
                    self._go(1)
                else:
                    self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene(SCENE_MODE_SELECT)
            elif event.key == pygame.K_RIGHT:
                self._go(1)
            elif event.key == pygame.K_LEFT:
                self._go(-1)
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
        self._draw_header(surface)
        self._draw_question(surface)
        self._draw_input_area(surface)
        self._draw_nav(surface)

        draw_button(surface, "退出", self.back_btn,
                    (180, 188, 205), WHITE, font_size=15, radius=10, shadow=False)
        hint_label = "隐藏提示" if self.show_hint else "显示提示"
        draw_button(surface, hint_label, self.hint_btn,
                    COLOR_SECONDARY if self.show_hint else (210, 215, 230),
                    WHITE if self.show_hint else COLOR_TEXT_SUB,
                    font_size=15, radius=10, shadow=False)

    def _draw_header(self, surface):
        pygame.draw.rect(surface, WHITE, (0, 0, SCREEN_WIDTH, 68))
        pygame.draw.line(surface, COLOR_BORDER, (0, 68), (SCREEN_WIDTH, 68), 1)
        total = len(self.pool)
        draw_text(surface, f"练习模式  {self.idx + 1} / {total}",
                  18, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 34, center=True)
        acc = round(self.correct / self.total * 100) if self.total else 0
        draw_text(surface, f"正确率  {acc}%", 17, COLOR_PRIMARY,
                  SCREEN_WIDTH - 120, 34, center=True, bold=True)

    def _draw_question(self, surface):
        current = self.current
        if not current:
            return
        card = pygame.Rect(SCREEN_WIDTH // 2 - 230, 108, 460, 220)
        draw_card(surface, card, bg=WHITE, radius=22, shadow=True)

        draw_text(surface, "请输入拼音", 18, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 136, center=True)
        draw_divider(surface, card.x + 30, 162, card.right - 30, (235, 238, 248))

        fs = 76 if len(current["display"]) <= 2 else 52
        draw_text(surface, current["display"], fs, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 234, center=True, bold=True)

        if self.show_hint:
            draw_text(surface, f"提示：{current['answer']}", 20, COLOR_SECONDARY,
                      SCREEN_WIDTH // 2, 295, center=True)

        if self.feedback:
            k, text, _ = self.feedback
            fg = COLOR_SUCCESS if k == "correct" else COLOR_DANGER
            bg = (238, 252, 244) if k == "correct" else (255, 240, 240)
            fb = pygame.Rect(SCREEN_WIDTH // 2 - 220, 348, 440, 44)
            pygame.draw.rect(surface, bg, fb, border_radius=10)
            draw_text(surface, text, 19, fg,
                      SCREEN_WIDTH // 2, 370, center=True, bold=True)
            draw_text(surface, "按 Enter 或 → 继续下一题",
                      14, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 406, center=True)

    def _draw_input_area(self, surface):
        pygame.draw.rect(surface, WHITE,
                         (0, SCREEN_HEIGHT - 130, SCREEN_WIDTH, 130))
        pygame.draw.line(surface, COLOR_BORDER,
                         (0, SCREEN_HEIGHT - 130), (SCREEN_WIDTH, SCREEN_HEIGHT - 130), 1)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT - 112, 520, 58)
        draw_input_box(surface, self.input_text, input_rect, font_size=34)
        draw_text(surface, "输入拼音后按 Enter 确认  ·  ← → 切换题目",
                  15, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 26, center=True)

    def _draw_nav(self, surface):
        draw_button(surface, "← 上一题", self._prev_btn(),
                    (230, 234, 244), COLOR_TEXT_MAIN, font_size=17, radius=12, shadow=False)
        draw_button(surface, "下一题 →", self._next_btn(),
                    COLOR_PRIMARY, WHITE, font_size=17, radius=12)

    def _prev_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 290, SCREEN_HEIGHT - 200, 200, 46)

    def _next_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 90, SCREEN_HEIGHT - 200, 200, 46)
