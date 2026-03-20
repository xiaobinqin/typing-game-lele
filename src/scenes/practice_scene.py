import pygame
import random
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_input_box,
                                   draw_rounded_rect, draw_background_gradient)
from src.utils.data_loader import build_quiz_pool


class PracticeScene:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.pool = build_quiz_pool(
            self.game.selected_content,
            self.game.selected_level,
            count=100
        )
        random.shuffle(self.pool)
        self.idx = 0
        self.input_text = ""
        self.feedback = None
        self.show_hint = False
        self.correct = 0
        self.total = 0
        self.back_btn = pygame.Rect(30, 30, 100, 44)
        self.hint_btn = pygame.Rect(SCREEN_WIDTH - 150, 30, 110, 44)
        self.next_btn = pygame.Rect(SCREEN_WIDTH // 2 + 20, 450, 200, 52)
        self.prev_btn = pygame.Rect(SCREEN_WIDTH // 2 - 220, 450, 200, 52)

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
            self.correct += 1
            self.feedback = ("correct", f"✓ 正确！答案：{self.current['answer']}", 80)
        else:
            self.feedback = ("wrong",
                             f"✗ 正确答案：{self.current['answer']}（你输入：{typed}）", 100)
        self.input_text = ""
        self.show_hint = False

    def _next(self):
        self.idx = (self.idx + 1) % len(self.pool)
        self.input_text = ""
        self.feedback = None
        self.show_hint = False

    def _prev(self):
        self.idx = (self.idx - 1) % len(self.pool)
        self.input_text = ""
        self.feedback = None
        self.show_hint = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.change_scene(SCENE_MENU)
                return
            if self.hint_btn.collidepoint(mx, my):
                self.show_hint = not self.show_hint
                return
            if self.next_btn.collidepoint(mx, my):
                self._next()
                return
            if self.prev_btn.collidepoint(mx, my):
                self._prev()
                return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.feedback:
                    self._next()
                else:
                    self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene(SCENE_MENU)
            elif event.key == pygame.K_RIGHT:
                self._next()
            elif event.key == pygame.K_LEFT:
                self._prev()
            else:
                ch = event.unicode
                if ch and ch.isalpha() and len(self.input_text) < 16:
                    self.input_text += ch.lower()

    def update(self):
        if self.feedback:
            kind, text, timer = self.feedback
            if timer > 1:
                self.feedback = (kind, text, timer - 1)

    def draw(self, surface):
        draw_background_gradient(surface, (230, 250, 235), (240, 250, 255),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)

        total = len(self.pool)
        draw_text(surface, f"练习模式  {self.idx + 1}/{total}", 26, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 50, center=True)

        current = self.current
        if current:
            card = pygame.Rect(SCREEN_WIDTH // 2 - 220, 120, 440, 180)
            pygame.draw.rect(surface, WHITE, card, border_radius=24)
            pygame.draw.rect(surface, COLOR_PRIMARY, card, 3, border_radius=24)
            draw_text(surface, "请输入拼音：", 22, COLOR_TEXT_SUB,
                      SCREEN_WIDTH // 2, 135, center=True)
            draw_text(surface, current["display"], 82, COLOR_TEXT_MAIN,
                      SCREEN_WIDTH // 2, 215, center=True, bold=True)

            if self.show_hint:
                draw_text(surface, f"提示：{current['answer']}", 24, ORANGE,
                          SCREEN_WIDTH // 2, 320, center=True)

        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 345, 480, 62)
        draw_input_box(surface, self.input_text, input_rect, font_size=36)

        if not self.feedback:
            draw_text(surface, "输入拼音后按 Enter 确认  |  ← → 切换题目",
                      17, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 425, center=True)
        else:
            kind, text, _ = self.feedback
            color = COLOR_SUCCESS if kind == "correct" else COLOR_DANGER
            draw_text(surface, text, 26, color, SCREEN_WIDTH // 2, 425, center=True, bold=True)
            draw_text(surface, "按 Enter 或 → 继续下一题", 17, COLOR_TEXT_SUB,
                      SCREEN_WIDTH // 2, 456, center=True)

        draw_button(surface, "上一题", self.prev_btn, LIGHT_BLUE, WHITE, font_size=22)
        draw_button(surface, "下一题", self.next_btn, COLOR_PRIMARY, WHITE, font_size=22)

        acc = round(self.correct / self.total * 100, 1) if self.total else 0
        draw_text(surface, f"已答 {self.total}  正确 {self.correct}  正确率 {acc}%",
                  20, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35, center=True)

        draw_button(surface, "← 退出", self.back_btn, GRAY, WHITE, font_size=19)
        hint_label = "隐藏提示" if self.show_hint else "显示提示"
        draw_button(surface, hint_label, self.hint_btn, COLOR_SECONDARY, WHITE, font_size=18)
