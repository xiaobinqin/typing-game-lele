import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_star, draw_input_box,
                                   draw_progress_bar, draw_divider)
from src.utils.data_loader import build_quiz_pool, normalize_pinyin
from src.utils.save_manager import save_record
from src.utils.sound_manager import play as sfx


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
        self.wrong_scroll = 0   # 错题回顾滚动偏移
        self.back_btn = pygame.Rect(20, 14, 88, 38)

    @property
    def current(self):
        return self.pool[self.idx] if self.idx < len(self.pool) else None

    def _submit(self):
        if not self.input_text or self.current is None:
            return
        typed = normalize_pinyin(self.input_text.strip())
        answer = self.current["answer"]   # 已经是 normalize 后的标准答案
        if typed == answer:
            self.correct += 1
            self.score += 10
            self.feedback = ("correct", f"正确！答案：{self.current['answer']}", 45)
            sfx("correct")
        else:
            self.wrong_items.append({
                "display": self.current["display"],
                "answer":  self.current["answer"],
                "typed":   typed,
            })
            self.feedback = ("wrong", f"正确答案：{self.current['answer']}", 55)
            sfx("wrong")
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
        if self.stars > 0:
            sfx("victory")

    def handle_event(self, event):
        if self.finished:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self._retry_btn().collidepoint(mx, my):
                    self.reset()
                elif self._menu_btn().collidepoint(mx, my):
                    self.game.change_scene(SCENE_MODE_SELECT)
            # 错题滚动：鼠标滚轮
            if event.type == pygame.MOUSEWHEEL and self.wrong_items:
                max_scroll = max(0, len(self.wrong_items) - 5)
                self.wrong_scroll = max(0, min(max_scroll,
                                               self.wrong_scroll - event.y))
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
        has_wrong = bool(self.wrong_items)
        # 卡片需包裹所有内容（含底部按钮），底边固定在 y=714
        card_top = 50
        card_h = 664
        card = pygame.Rect(SCREEN_WIDTH // 2 - 310, card_top, 620, card_h)
        draw_card(surface, card, bg=WHITE, radius=24, shadow=True)

        passed = self.stars > 0
        title_color = COLOR_SUCCESS if passed else COLOR_DANGER
        draw_text(surface, "恭喜通关！" if passed else "本次未通关",
                  44, title_color, SCREEN_WIDTH // 2, card_top + 70, center=True, bold=True)

        for i in range(3):
            draw_star(surface, SCREEN_WIDTH // 2 - 60 + i * 60, card_top + 128,
                      filled=(i < self.stars), size=26)

        total = len(self.pool)
        acc = round(self.correct / total * 100, 1) if total else 0
        draw_text(surface, f"{self.score}", 60, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, card_top + 198, center=True, bold=True)
        draw_text(surface, "分", 18, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2 + 50, card_top + 214)
        draw_text(surface, f"共 {total} 题  ·  正确 {self.correct} 题  ·  正确率 {acc}%",
                  18, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, card_top + 246, center=True)

        if has_wrong:
            div_y = card_top + 272
            draw_divider(surface, card.x + 40, div_y, card.right - 40, (235, 238, 248))
            wrong_n = len(self.wrong_items)
            draw_text(surface, f"错题回顾（共 {wrong_n} 题）",
                      16, COLOR_DANGER, SCREEN_WIDTH // 2, div_y + 22, center=True, bold=True)

            # 可视区域 5 行，行高 28px，支持滚动
            visible = 5
            row_h = 28
            list_top = div_y + 42
            start = self.wrong_scroll
            clip_rect = pygame.Rect(card.x + 10, list_top, card.width - 20, visible * row_h)
            surface.set_clip(clip_rect)
            for i, w in enumerate(self.wrong_items[start: start + visible]):
                line = f"{w['display']}  →  正确：{w['answer']}    你答：{w['typed']}"
                draw_text(surface, line, 15, COLOR_TEXT_SUB,
                          SCREEN_WIDTH // 2, list_top + i * row_h + row_h // 2, center=True)
            surface.set_clip(None)

            # 滚动指示（在列表区域下方，与按钮之间）
            if wrong_n > visible:
                shown_end = min(start + visible, wrong_n)
                draw_text(surface, f"↑↓ 滚轮翻页  {start+1}–{shown_end} / {wrong_n}",
                          13, COLOR_TEXT_SUB, SCREEN_WIDTH // 2,
                          list_top + visible * row_h + 16, center=True)

        draw_button(surface, "再来一关", self._retry_btn(),
                    COLOR_PRIMARY, WHITE, font_size=22, radius=14)
        draw_button(surface, "返回选择", self._menu_btn(),
                    (180, 188, 205), WHITE, font_size=22, radius=14)

    def _retry_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 290, 662, 256, 52)

    def _menu_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 34, 662, 256, 52)
