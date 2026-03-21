import pygame
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_input_box, draw_progress_bar,
                                   draw_divider)
from src.utils.data_loader import build_quiz_pool, normalize_pinyin
from src.utils.save_manager import save_record, save_leaderboard, get_leaderboard
from src.utils.sound_manager import play as sfx


class SpeedScene:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.pool = build_quiz_pool(self.game.selected_content,
                                    self.game.selected_level, count=100)
        self.idx = 0
        self.input_text = ""
        self.score = 0
        self.correct = 0
        self.total = 0
        self.combo = 0
        self.max_combo = 0
        self.time_left = SPEED_DURATION * FPS
        self.feedback = None
        self.finished = False
        self.name_input = ""
        self.name_saved = False
        self.name_empty_hint = False   # 空昵称提示标志
        self.back_btn = pygame.Rect(20, 14, 88, 38)

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
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            bonus = min(self.combo, 5) * 2
            gained = 10 + bonus
            self.score += gained
            self.correct += 1
            combo_str = f"  连击 x{self.combo}" if self.combo > 1 else ""
            self.feedback = ("correct", f"+{gained}{combo_str}", 32)
            sfx("correct")
        else:
            self.combo = 0
            self.feedback = ("wrong", f"正确：{self.current['answer']}", 40)
            sfx("wrong")
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
                            self.name_empty_hint = False
                        else:
                            self.name_empty_hint = True   # 空昵称：显示提示
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                        self.name_empty_hint = False
                    else:
                        ch = event.unicode
                        if ch and len(self.name_input) < 8:
                            self.name_input += ch
                            self.name_empty_hint = False
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
            k, t, n = self.feedback
            self.feedback = (k, t, n - 1) if n > 1 else None

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        if self.finished:
            self._draw_result(surface)
            return

        self._draw_hud(surface)
        self._draw_question(surface)
        self._draw_input_area(surface)

        draw_button(surface, "退出", self.back_btn,
                    (180, 188, 205), WHITE, font_size=15, radius=10, shadow=False)

    def _draw_hud(self, surface):
        secs = self.time_left // FPS
        urgent = secs <= 10
        bar_color = COLOR_DANGER if urgent else COLOR_PRIMARY

        pygame.draw.rect(surface, WHITE, (0, 0, SCREEN_WIDTH, 72))
        pygame.draw.line(surface, COLOR_BORDER, (0, 72), (SCREEN_WIDTH, 72), 1)

        draw_progress_bar(surface, 120, 18, SCREEN_WIDTH - 240, 14,
                          self.time_left, SPEED_DURATION * FPS, color_fill=bar_color)
        draw_text(surface, f"{secs}s", 28, bar_color,
                  SCREEN_WIDTH // 2, 52, center=True, bold=True)
        draw_text(surface, f"{self.score} 分", 20, COLOR_PRIMARY,
                  200, 52, center=True, bold=True)
        if self.combo > 1:
            draw_text(surface, f"连击 x{self.combo}", 18, COLOR_SECONDARY,
                      SCREEN_WIDTH - 200, 52, center=True, bold=True)

    def _draw_question(self, surface):
        current = self.current
        if not current:
            return
        card = pygame.Rect(SCREEN_WIDTH // 2 - 220, 108, 440, 200)
        draw_card(surface, card, bg=WHITE, radius=22, shadow=True)

        draw_text(surface, "请输入拼音", 18, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, 136, center=True)
        draw_divider(surface, card.x + 30, 162, card.right - 30, (235, 238, 248))

        fs = 76 if len(current["display"]) <= 2 else 52
        draw_text(surface, current["display"], fs, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 224, center=True, bold=True)

        if self.feedback:
            k, text, _ = self.feedback
            fg = COLOR_SUCCESS if k == "correct" else COLOR_DANGER
            draw_text(surface, text, 22, fg,
                      SCREEN_WIDTH // 2, 330, center=True, bold=True)

    def _draw_input_area(self, surface):
        pygame.draw.rect(surface, WHITE,
                         (0, SCREEN_HEIGHT - 130, SCREEN_WIDTH, 130))
        pygame.draw.line(surface, COLOR_BORDER,
                         (0, SCREEN_HEIGHT - 130), (SCREEN_WIDTH, SCREEN_HEIGHT - 130), 1)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT - 112, 520, 58)
        draw_input_box(surface, self.input_text, input_rect, font_size=34)
        draw_text(surface, "输入拼音后按 Enter 确认",
                  15, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 26, center=True)

        acc = round(self.correct / self.total * 100) if self.total else 0
        draw_text(surface, f"已答 {self.total}  正确率 {acc}%",
                  16, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 148, center=True)

    def _draw_result(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        card = pygame.Rect(SCREEN_WIDTH // 2 - 300, 80, 600, 480)
        draw_card(surface, card, bg=WHITE, radius=24, shadow=True)

        draw_text(surface, "时间到！", 46, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 152, center=True, bold=True)
        draw_text(surface, f"{self.score}", 78, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 252, center=True, bold=True)
        draw_text(surface, "分", 22, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2 + 66, 270)

        acc = round(self.correct / self.total * 100, 1) if self.total else 0
        draw_text(surface, f"答题 {self.total}  ·  正确 {self.correct}  ·  正确率 {acc}%  ·  最大连击 {self.max_combo}",
                  18, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 310, center=True)

        draw_divider(surface, card.x + 50, 338, card.right - 50, (235, 238, 248))

        if not self.name_saved:
            draw_text(surface, "输入昵称上榜（Enter 确认）",
                      18, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 366, center=True)
            nr = pygame.Rect(SCREEN_WIDTH // 2 - 170, 386, 340, 50)
            draw_input_box(surface, self.name_input, nr, font_size=26)
            if self.name_empty_hint:
                draw_text(surface, "昵称不能为空，请输入后再确认",
                          15, COLOR_DANGER, SCREEN_WIDTH // 2, 448, center=True)
        else:
            draw_text(surface, "已保存到排行榜！", 20, COLOR_SUCCESS,
                      SCREEN_WIDTH // 2, 380, center=True, bold=True)
            board = get_leaderboard("speed")
            for i, entry in enumerate(board[:5]):
                clr = (COLOR_SECONDARY if i == 0
                       else (GRAY if i == 1 else COLOR_TEXT_SUB))
                draw_text(surface,
                          f"#{i+1}  {entry['name']}   {entry['score']} 分   {entry['time']}",
                          17, clr, SCREEN_WIDTH // 2, 412 + i * 28, center=True)

        draw_button(surface, "再来一局", self._retry_btn(),
                    COLOR_PRIMARY, WHITE, font_size=22, radius=14)
        draw_button(surface, "返回选择", self._menu_btn(),
                    (180, 188, 205), WHITE, font_size=22, radius=14)

    def _retry_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 290, 590, 256, 52)

    def _menu_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 34, 590, 256, 52)
