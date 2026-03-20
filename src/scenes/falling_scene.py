import pygame
import random
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_rounded_rect,
                                   draw_heart, draw_input_box, draw_background_gradient)
from src.utils.data_loader import build_quiz_pool
from src.utils.save_manager import save_record


MAX_HP = 5
COLUMN_COUNT = 5


class FallingItem:
    def __init__(self, display, answer, hint, col, speed, screen_h, step=2):
        self.display = display
        self.answer = answer
        self.hint = hint
        self.x = 0
        self.y = -60
        self.col = col
        self.speed = speed       # 每N帧下落step px
        self.step = step
        self.tick = 0
        self.matched = False
        self.flash = 0           # 消除动画帧
        self.screen_h = screen_h

    def update(self):
        self.tick += 1
        if self.tick >= self.speed:
            self.tick = 0
            self.y += self.step
        if self.flash > 0:
            self.flash -= 1

    def is_landed(self):
        return self.y > self.screen_h - 120

    def draw(self, surface, col_x, font_size=34):
        from src.utils.font_manager import get_font
        self.x = col_x
        if self.matched:
            alpha = max(0, self.flash * 12)
            color = COLOR_SUCCESS
        else:
            color = COLOR_PRIMARY

        card_w, card_h = 120, 60
        rect = pygame.Rect(self.x - card_w // 2, self.y, card_w, card_h)
        pygame.draw.rect(surface, color, rect, border_radius=14)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=14)

        font = get_font(font_size, bold=True)
        surf = font.render(self.display, True, WHITE)
        sr = surf.get_rect(center=(self.x, self.y + card_h // 2))
        surface.blit(surf, sr)


class FallingScene:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        speed_lv = getattr(self.game, "falling_speed_level", 1)
        init_speed, self.fall_step, spawn_interval = FALLING_SPEED_LEVELS[speed_lv]

        self.pool = build_quiz_pool(
            self.game.selected_content,
            self.game.selected_level,
            count=60
        )
        self.pool_idx = 0
        self.items: list[FallingItem] = []
        self.input_text = ""
        self.hp = MAX_HP
        self.score = 0
        self.correct = 0
        self.total_answered = 0
        self.spawn_timer = 0
        self.spawn_interval = spawn_interval
        self.fall_speed = init_speed
        self.running = True
        self.paused = False
        self.feedback = None       # ("correct"|"wrong", text, timer)
        self.col_xs = self._calc_col_xs()
        self.back_btn = pygame.Rect(30, 30, 100, 44)
        self.pause_btn = pygame.Rect(SCREEN_WIDTH - 140, 30, 100, 44)

    def _calc_col_xs(self):
        margin = 100
        usable = SCREEN_WIDTH - 2 * margin
        return [margin + usable * i // (COLUMN_COUNT - 1) for i in range(COLUMN_COUNT)]

    def _next_item(self):
        if self.pool_idx >= len(self.pool):
            self.pool_idx = 0
            random.shuffle(self.pool)
        q = self.pool[self.pool_idx]
        self.pool_idx += 1
        return q

    def _get_free_col(self):
        used_cols = {item.col for item in self.items}
        free = [c for c in range(COLUMN_COUNT) if c not in used_cols]
        if not free:
            return None
        return random.choice(free)

    def handle_event(self, event):
        if not self.running:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self._retry_btn().collidepoint(mx, my):
                    self.reset()
                elif self._back_btn_result().collidepoint(mx, my):
                    self.game.change_scene(SCENE_MENU)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self._save_and_go_menu()
                return
            if self.pause_btn.collidepoint(mx, my):
                self.paused = not self.paused
                return

        if self.paused:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self._save_and_go_menu()
            else:
                ch = event.unicode
                if ch and ch.isalpha() and len(self.input_text) < 12:
                    self.input_text += ch.lower()

    def _submit(self):
        if not self.input_text:
            return
        typed = self.input_text.strip().lower()
        matched = False
        for item in self.items:
            if item.matched:
                continue
            if typed == item.answer.lower():
                item.matched = True
                item.flash = 20
                self.score += 10
                self.correct += 1
                self.total_answered += 1
                self.feedback = ("correct", f"✓ 正确！+10", 60)
                matched = True
                # 加速
                if self.correct % FALLING_SPEED_STEP == 0:
                    self.fall_speed = max(FALLING_MIN_SPEED, self.fall_speed - 2)
                    for it in self.items:
                        it.speed = self.fall_speed
                break
        if not matched:
            self.total_answered += 1
            # 找最近一个提示
            hint = ""
            for item in self.items:
                if not item.matched:
                    hint = item.hint
                    break
            self.feedback = ("wrong", f"✗ 答错  {hint}", 80)
        self.input_text = ""

    def update(self):
        if not self.running or self.paused:
            return

        # 生成新字
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            if len(self.items) < FALLING_MAX_ITEMS:
                col = self._get_free_col()
                if col is not None:
                    q = self._next_item()
                    item = FallingItem(
                        q["display"], q["answer"], q["hint"],
                        col, self.fall_speed, SCREEN_HEIGHT, step=self.fall_step
                    )
                    self.items.append(item)
            self.spawn_timer = 0

        # 更新下落
        for item in self.items:
            item.update()

        # 检查落地
        landed = [it for it in self.items if it.is_landed() and not it.matched]
        for it in landed:
            self.hp -= 1
            self.feedback = ("wrong", f"漏掉了！{it.hint}", 80)
        self.items = [it for it in self.items if not it.is_landed() and not (it.matched and it.flash == 0)]

        if self.feedback:
            kind, text, timer = self.feedback
            self.feedback = (kind, text, timer - 1) if timer > 1 else None

        if self.hp <= 0:
            self.running = False
            save_record("falling", self.game.selected_level,
                        self.game.selected_content,
                        self.total_answered, self.correct, self.score)

    def draw(self, surface):
        draw_background_gradient(surface, (200, 225, 255), (230, 245, 230),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)

        if not self.running:
            self._draw_gameover(surface)
            return

        # 顶部信息栏
        self._draw_hud(surface)

        # 落下的字
        for item in self.items:
            item.draw(surface, self.col_xs[item.col])

        # 输入框
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT - 90, 520, 60)
        draw_input_box(surface, self.input_text, input_rect, font_size=36)
        draw_text(surface, "输入拼音后按 Enter 确认", 18, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT - 18, center=True)

        # 反馈消息
        if self.feedback:
            kind, text, _ = self.feedback
            color = COLOR_SUCCESS if kind == "correct" else COLOR_DANGER
            draw_text(surface, text, 26, color,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130, center=True, bold=True)

        # 暂停蒙层
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))
            draw_text(surface, "⏸ 已暂停", 60, WHITE,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True, bold=True)
            draw_text(surface, '点击"继续"或按任意键恢复', 26, LIGHT_GRAY,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, center=True)

        draw_button(surface, "← 退出", self.back_btn, GRAY, WHITE, font_size=19)
        label = "⏸ 暂停" if not self.paused else "▶ 继续"
        draw_button(surface, label, self.pause_btn, COLOR_SECONDARY, WHITE, font_size=19)

    def _draw_hud(self, surface):
        # 分数
        draw_text(surface, f"得分: {self.score}", 28, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 40, center=True, bold=True)
        # 连击/命数
        for i in range(MAX_HP):
            draw_heart(surface, 200 + i * 36, 50, filled=(i < self.hp))
        draw_text(surface, f"已答: {self.total_answered}  正确: {self.correct}", 20, COLOR_TEXT_SUB,
                  SCREEN_WIDTH - 20, 50, center=False)
        # 分隔线
        pygame.draw.line(surface, LIGHT_GRAY, (0, 80), (SCREEN_WIDTH, 80), 2)

    def _draw_gameover(self, surface):
        draw_background_gradient(surface, (255, 220, 220), (255, 245, 200),
                                 SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_text(surface, "游戏结束！", 64, COLOR_DANGER,
                  SCREEN_WIDTH // 2, 180, center=True, bold=True)
        acc = round(self.correct / self.total_answered * 100, 1) if self.total_answered else 0
        draw_text(surface, f"最终得分：{self.score}", 40, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 280, center=True, bold=True)
        draw_text(surface, f"答题数：{self.total_answered}   正确：{self.correct}   正确率：{acc}%",
                  28, COLOR_TEXT_MAIN, SCREEN_WIDTH // 2, 350, center=True)

        draw_button(surface, "再来一局", self._retry_btn(),
                    COLOR_PRIMARY, WHITE, font_size=28)
        draw_button(surface, "返回主菜单", self._back_btn_result(),
                    COLOR_SECONDARY, WHITE, font_size=28)

    def _retry_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 280, 440, 240, 60)

    def _back_btn_result(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 40, 440, 240, 60)

    def _save_and_go_menu(self):
        save_record("falling", self.game.selected_level,
                    self.game.selected_content,
                    self.total_answered, self.correct, self.score)
        self.game.change_scene(SCENE_MENU)
