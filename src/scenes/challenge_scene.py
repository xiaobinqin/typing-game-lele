import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_rounded_rect,
                                   draw_star, draw_input_box, draw_progress_bar,
                                   draw_background_gradient)
from src.utils.data_loader import build_quiz_pool
from src.utils.save_manager import save_record


class ChallengeScene:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.pool = build_quiz_pool(
            self.game.selected_content,
            self.game.selected_level,
            count=CHALLENGE_TOTAL
        )
        self.idx = 0
        self.input_text = ""
        self.correct = 0
        self.wrong_items = []
        self.feedback = None     # ("correct"|"wrong", text, timer)
        self.finished = False
        self.score = 0
        self.stars = 0
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
        if typed == answer:
            self.correct += 1
            self.score += 10
            self.feedback = ("correct", "✓ 正确！", 45)
        else:
            self.wrong_items.append({
                "display": self.current["display"],
                "answer":  self.current["answer"],
                "typed":   typed,
            })
            self.feedback = ("wrong", f"✗ 正确答案：{self.current['answer']}", 55)
        self.input_text = ""
        self.idx += 1
        if self.idx >= len(self.pool):
            self._finish()

    def _finish(self):
        self.finished = True
        total = len(self.pool)
        acc = self.correct / total if total else 0
        if acc >= 0.9:
            self.stars = 3
        elif acc >= 0.7:
            self.stars = 2
        elif acc >= CHALLENGE_PASS_RATE:
            self.stars = 1
        else:
            self.stars = 0
        save_record("challenge", self.game.selected_level,
                    self.game.selected_content,
                    total, self.correct, self.score)

    def handle_event(self, event):
        if self.finished:
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
                if ch and ch.isalpha() and len(self.input_text) < 16:
                    self.input_text += ch.lower()

    def update(self):
        if self.feedback:
            kind, text, timer = self.feedback
            self.feedback = (kind, text, timer - 1) if timer > 1 else None

    def draw(self, surface):
        draw_background_gradient(surface, (230, 245, 255), (255, 245, 220),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)

        if self.finished:
            self._draw_result(surface)
            return

        total = len(self.pool)
        current = self.current

        # 进度条
        draw_text(surface, f"闯关模式  {self.idx}/{total}", 26, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 50, center=True)
        draw_progress_bar(surface, 100, 75, SCREEN_WIDTH - 200, 18,
                          self.idx, total)

        # 题目展示
        if current:
            card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 140, 400, 180)
            pygame.draw.rect(surface, WHITE, card_rect, border_radius=24)
            pygame.draw.rect(surface, COLOR_PRIMARY, card_rect, 3, border_radius=24)

            draw_text(surface, "请输入拼音：", 22, COLOR_TEXT_SUB,
                      SCREEN_WIDTH // 2, 155, center=True)
            draw_text(surface, current["display"], 80, COLOR_TEXT_MAIN,
                      SCREEN_WIDTH // 2, 235, center=True, bold=True)

        # 输入框
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 360, 480, 64)
        draw_input_box(surface, self.input_text, input_rect, font_size=38)
        draw_text(surface, "输入拼音后按 Enter 确认", 18, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 440, center=True)

        # 反馈
        if self.feedback:
            kind, text, _ = self.feedback
            color = COLOR_SUCCESS if kind == "correct" else COLOR_DANGER
            draw_text(surface, text, 28, color,
                      SCREEN_WIDTH // 2, 490, center=True, bold=True)

        # 统计
        draw_text(surface, f"✓ {self.correct}  ✗ {self.idx - self.correct}  得分：{self.score}",
                  22, COLOR_TEXT_MAIN, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, center=True)

        draw_button(surface, "← 退出", self.back_btn, GRAY, WHITE, font_size=19)

    def _draw_result(self, surface):
        draw_background_gradient(surface, (220, 255, 220) if self.stars > 0 else (255, 220, 220),
                                 (255, 250, 200), SCREEN_WIDTH, SCREEN_HEIGHT)

        title = "恭喜通关！" if self.stars > 0 else "未通关，加油！"
        color = COLOR_SUCCESS if self.stars > 0 else COLOR_DANGER
        draw_text(surface, title, 60, color,
                  SCREEN_WIDTH // 2, 140, center=True, bold=True)

        # 星星
        star_cx = SCREEN_WIDTH // 2
        for i in range(3):
            x = star_cx - 80 + i * 80
            draw_star(surface, x, 240, filled=(i < self.stars), size=36)

        total = len(self.pool)
        acc = round(self.correct / total * 100, 1) if total else 0
        draw_text(surface, f"得分：{self.score}", 40, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 320, center=True, bold=True)
        draw_text(surface, f"共 {total} 题  正确 {self.correct} 题  正确率 {acc}%",
                  26, COLOR_TEXT_MAIN, SCREEN_WIDTH // 2, 380, center=True)

        if self.wrong_items:
            draw_text(surface, "错题回顾：", 22, COLOR_DANGER,
                      SCREEN_WIDTH // 2, 430, center=True)
            for i, w in enumerate(self.wrong_items[:5]):
                line = f"{w['display']} → 正确：{w['answer']}  你答的：{w['typed']}"
                draw_text(surface, line, 19, COLOR_TEXT_MAIN,
                          SCREEN_WIDTH // 2, 460 + i * 28, center=True)

        draw_button(surface, "再来一关", self._retry_btn(), COLOR_PRIMARY, WHITE, font_size=26)
        draw_button(surface, "返回主菜单", self._menu_btn(), COLOR_SECONDARY, WHITE, font_size=26)

    def _retry_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 280, SCREEN_HEIGHT - 120, 240, 56)

    def _menu_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 40, SCREEN_HEIGHT - 120, 240, 56)
