import pygame
import random
from src.utils.constants import *
from src.utils.draw_utils import (draw_text, draw_button, draw_background_solid,
                                   draw_card, draw_heart, draw_input_box,
                                   draw_divider, draw_shadow_rect)
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
        self.y = -80
        self.col = col
        self.speed = speed
        self.step = step
        self.tick = 0
        self.matched = False
        self.flash = 0
        self.screen_h = screen_h

    def update(self):
        self.tick += 1
        if self.tick >= self.speed:
            self.tick = 0
            self.y += self.step
        if self.flash > 0:
            self.flash -= 1

    def is_landed(self):
        return self.y > self.screen_h - 130

    def draw(self, surface, col_x):
        from src.utils.font_manager import get_font
        self.x = col_x
        card_w, card_h = 130, 68

        bg     = COLOR_SUCCESS if self.matched else WHITE
        border = (30, 160, 80) if self.matched else COLOR_PRIMARY

        rect = pygame.Rect(self.x - card_w // 2, int(self.y), card_w, card_h)
        draw_shadow_rect(surface, rect, radius=14, shadow_offset=4, shadow_alpha=30)
        pygame.draw.rect(surface, bg, rect, border_radius=14)
        pygame.draw.rect(surface, border, rect, 2, border_radius=14)

        text_color = WHITE if self.matched else COLOR_TEXT_MAIN
        fs = 32 if len(self.display) <= 2 else 24
        font = get_font(fs, bold=True)
        surf = font.render(self.display, True, text_color)
        sr = surf.get_rect(center=(self.x, int(self.y) + card_h // 2))
        surface.blit(surf, sr)


# ────────────────────────────────────────────────────────────
#  速度选择界面（游戏内嵌，进入消消乐前先选速度）
# ────────────────────────────────────────────────────────────
_SPEED_ITEMS = [
    (0, "慢速", "适合初学，字落较慢",   FALLING_SPEED_COLORS[0]),
    (1, "中速", "标准节奏，稳步提升",   FALLING_SPEED_COLORS[1]),
    (2, "快速", "极限挑战，高手专属",   FALLING_SPEED_COLORS[2]),
]


class SpeedPickScene:
    """嵌入 FallingScene 的速度选择界面，选完后调用 on_confirm(level)"""

    def __init__(self, selected=1, on_confirm=None, on_back=None):
        self.selected = selected
        self.on_confirm = on_confirm
        self.on_back = on_back
        self.hover = -1
        self.cards = self._build_cards()
        self.confirm_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, 560, 260, 56)
        self.back_btn = pygame.Rect(36, 28, 96, 40)

    def _build_cards(self):
        card_w, card_h = 260, 160
        gap = 30
        total_w = len(_SPEED_ITEMS) * card_w + (len(_SPEED_ITEMS) - 1) * gap
        sx = (SCREEN_WIDTH - total_w) // 2
        y = 290
        cards = []
        for i, (lv, name, desc, color) in enumerate(_SPEED_ITEMS):
            x = sx + i * (card_w + gap)
            cards.append({
                "rect": pygame.Rect(x, y, card_w, card_h),
                "level": lv, "name": name, "desc": desc, "color": color,
            })
        return cards

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover = -1
            for i, c in enumerate(self.cards):
                if c["rect"].collidepoint(mx, my):
                    self.hover = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                if self.on_back:
                    self.on_back()
                return
            for c in self.cards:
                if c["rect"].collidepoint(mx, my):
                    self.selected = c["level"]
            if self.confirm_btn.collidepoint(mx, my):
                if self.on_confirm:
                    self.on_confirm(self.selected)

    def draw(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)

        draw_text(surface, "选择下落速度", 44, COLOR_TEXT_MAIN,
                  SCREEN_WIDTH // 2, 110, center=True, bold=True)
        draw_text(surface, "速度越快，挑战越大！随游戏进行会自动加速",
                  20, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 158, center=True)
        draw_divider(surface, 80, 188, SCREEN_WIDTH - 80)

        for i, c in enumerate(self.cards):
            sel = (c["level"] == self.selected)
            hover = (i == self.hover)
            rect = c["rect"].inflate(0, 8) if hover or sel else c["rect"]
            color = c["color"]

            bg = color if sel else WHITE
            draw_card(surface, rect, bg=bg, radius=20,
                      border_color=color if not sel else None,
                      shadow=True)

            name_color = WHITE if sel else color
            desc_color = (230, 240, 255) if sel else COLOR_TEXT_SUB
            draw_text(surface, c["name"], 32, name_color,
                      rect.centerx, rect.centery - 22, center=True, bold=True)
            draw_text(surface, c["desc"], 17, desc_color,
                      rect.centerx, rect.centery + 18, center=True)

            if sel:
                draw_text(surface, "✓", 22, WHITE,
                          rect.right - 26, rect.y + 22, center=True)

        draw_button(surface, "开始游戏", self.confirm_btn,
                    COLOR_PRIMARY, WHITE, font_size=26, radius=14, shadow=True)
        draw_button(surface, "← 返回", self.back_btn,
                    (180, 188, 205), WHITE, font_size=17, radius=10, shadow=False)


# ────────────────────────────────────────────────────────────
#  消消乐主场景
# ────────────────────────────────────────────────────────────
class FallingScene:
    def __init__(self, game):
        self.game = game
        # 先进入速度选择界面
        self._speed_pick = SpeedPickScene(
            selected=getattr(game, "falling_speed_level", 1),
            on_confirm=self._on_speed_confirmed,
            on_back=lambda: game.change_scene(SCENE_MODE_SELECT),
        )
        self._picking_speed = True   # True = 显示速度选择; False = 正在游戏
        self._game_started = False

    def _on_speed_confirmed(self, level):
        self.game.falling_speed_level = level
        self._picking_speed = False
        self._game_started = True
        self._init_game()

    def _init_game(self):
        speed_lv = getattr(self.game, "falling_speed_level", 1)
        init_speed, self.fall_step, spawn_interval = FALLING_SPEED_LEVELS[speed_lv]
        self.pool = build_quiz_pool(self.game.selected_content,
                                    self.game.selected_level, count=60)
        self.pool_idx = 0
        self.items = []
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
        self.feedback = None
        self.col_xs = self._calc_col_xs()
        self.back_btn = pygame.Rect(20, 14, 88, 38)
        self.pause_btn = pygame.Rect(SCREEN_WIDTH - 110, 14, 88, 38)

    def _calc_col_xs(self):
        margin = 110
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
        used = {it.col for it in self.items}
        free = [c for c in range(COLUMN_COUNT) if c not in used]
        return random.choice(free) if free else None

    # ── 事件 ──────────────────────────────────────────────────
    def handle_event(self, event):
        if self._picking_speed:
            self._speed_pick.handle_event(event)
            return

        if not self.running:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self._retry_btn().collidepoint(mx, my):
                    self._picking_speed = True
                    self._speed_pick = SpeedPickScene(
                        selected=getattr(self.game, "falling_speed_level", 1),
                        on_confirm=self._on_speed_confirmed,
                        on_back=lambda: self.game.change_scene(SCENE_MODE_SELECT),
                    )
                elif self._menu_btn().collidepoint(mx, my):
                    self.game.change_scene(SCENE_MENU)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_btn.collidepoint(mx, my):
                self._save_exit()
                return
            if self.pause_btn.collidepoint(mx, my):
                self.paused = not self.paused
                return

        if self.paused:
            if event.type == pygame.KEYDOWN:
                self.paused = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self._save_exit()
            else:
                ch = event.unicode
                if ch and ch.isalpha() and len(self.input_text) < 12:
                    self.input_text += ch.lower()

    def _submit(self):
        if not self.input_text:
            return
        typed = self.input_text.strip().lower()
        matched = False
        for it in self.items:
            if it.matched:
                continue
            if typed == it.answer.lower():
                it.matched = True
                it.flash = 22
                self.score += 10
                self.correct += 1
                self.total_answered += 1
                self.feedback = ("correct", "正确！+10", 55)
                matched = True
                if self.correct % FALLING_SPEED_STEP == 0:
                    self.fall_speed = max(FALLING_MIN_SPEED, self.fall_speed - 2)
                    for x in self.items:
                        x.speed = self.fall_speed
                break
        if not matched:
            self.total_answered += 1
            hint = next((it.hint for it in self.items if not it.matched), "")
            self.feedback = ("wrong", f"答错了  {hint}", 75)
        self.input_text = ""

    # ── 更新 ──────────────────────────────────────────────────
    def update(self):
        if self._picking_speed or not self._game_started:
            return
        if not self.running or self.paused:
            return

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            if len(self.items) < FALLING_MAX_ITEMS:
                col = self._get_free_col()
                if col is not None:
                    q = self._next_item()
                    self.items.append(FallingItem(
                        q["display"], q["answer"], q["hint"],
                        col, self.fall_speed, SCREEN_HEIGHT, step=self.fall_step
                    ))
            self.spawn_timer = 0

        for it in self.items:
            it.update()

        for it in [x for x in self.items if x.is_landed() and not x.matched]:
            self.hp -= 1
            self.feedback = ("wrong", f"漏掉了！{it.hint}", 75)
        self.items = [it for it in self.items
                      if not it.is_landed() and not (it.matched and it.flash == 0)]

        if self.feedback:
            k, t, n = self.feedback
            self.feedback = (k, t, n - 1) if n > 1 else None

        if self.hp <= 0:
            self.running = False
            save_record("falling", self.game.selected_level,
                        self.game.selected_content,
                        self.total_answered, self.correct, self.score)

    # ── 绘制 ──────────────────────────────────────────────────
    def draw(self, surface):
        if self._picking_speed:
            self._speed_pick.draw(surface)
            return

        draw_background_solid(surface, (250, 252, 255))

        if not self.running:
            self._draw_gameover(surface)
            return

        self._draw_hud(surface)

        for it in self.items:
            it.draw(surface, self.col_xs[it.col])

        # 底部输入区
        pygame.draw.rect(surface, WHITE,
                         (0, SCREEN_HEIGHT - 110, SCREEN_WIDTH, 110))
        pygame.draw.line(surface, COLOR_BORDER,
                         (0, SCREEN_HEIGHT - 110), (SCREEN_WIDTH, SCREEN_HEIGHT - 110), 1)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 270, SCREEN_HEIGHT - 95, 540, 58)
        draw_input_box(surface, self.input_text, input_rect, font_size=34)
        draw_text(surface, "输入拼音后按 Enter 确认",
                  15, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, center=True)

        if self.feedback:
            k, text, _ = self.feedback
            fg = COLOR_SUCCESS if k == "correct" else COLOR_DANGER
            draw_text(surface, text, 22, fg,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 128, center=True, bold=True)

        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 30, 60, 140))
            surface.blit(overlay, (0, 0))
            draw_text(surface, "已暂停", 56, WHITE,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, center=True, bold=True)
            draw_text(surface, "点击「继续」或按任意键恢复",
                      22, (200, 210, 230), SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 2 + 44, center=True)

        draw_button(surface, "退出", self.back_btn,
                    (180, 188, 205), WHITE, font_size=15, radius=10, shadow=False)
        label = "暂停" if not self.paused else "继续"
        draw_button(surface, label, self.pause_btn,
                    COLOR_PRIMARY if not self.paused else COLOR_SUCCESS,
                    WHITE, font_size=15, radius=10, shadow=False)

    def _draw_hud(self, surface):
        pygame.draw.rect(surface, WHITE, (0, 0, SCREEN_WIDTH, 64))
        pygame.draw.line(surface, COLOR_BORDER, (0, 64), (SCREEN_WIDTH, 64), 1)

        for i in range(MAX_HP):
            draw_heart(surface, 140 + i * 30, 32, filled=(i < self.hp), size=20)

        draw_text(surface, f"{self.score}", 30, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 32, center=True, bold=True)
        draw_text(surface, "分", 16, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2 + 36, 38)

        acc = round(self.correct / self.total_answered * 100) if self.total_answered else 0
        draw_text(surface, f"正确率  {acc}%", 17, COLOR_TEXT_SUB,
                  SCREEN_WIDTH - 130, 32, center=True)

        # 当前速度档位标记
        speed_name = FALLING_SPEED_NAMES.get(getattr(self.game, "falling_speed_level", 1), "")
        draw_text(surface, speed_name, 14, COLOR_TEXT_SUB,
                  SCREEN_WIDTH - 130, 52, center=True)

    def _draw_gameover(self, surface):
        draw_background_solid(surface, COLOR_BG_MAIN)
        card = pygame.Rect(SCREEN_WIDTH // 2 - 280, 140, 560, 380)
        draw_card(surface, card, bg=WHITE, radius=24, shadow=True)

        acc = round(self.correct / self.total_answered * 100, 1) if self.total_answered else 0
        draw_text(surface, "游戏结束", 48, COLOR_DANGER,
                  SCREEN_WIDTH // 2, 220, center=True, bold=True)
        draw_text(surface, f"{self.score}", 72, COLOR_PRIMARY,
                  SCREEN_WIDTH // 2, 310, center=True, bold=True)
        draw_text(surface, "分", 22, COLOR_TEXT_SUB,
                  SCREEN_WIDTH // 2 + 60, 330)
        draw_text(surface, f"共答 {self.total_answered} 题   正确 {self.correct} 题   正确率 {acc}%",
                  20, COLOR_TEXT_SUB, SCREEN_WIDTH // 2, 382, center=True)

        draw_button(surface, "再来一局", self._retry_btn(),
                    COLOR_PRIMARY, WHITE, font_size=24, radius=14)
        draw_button(surface, "返回主菜单", self._menu_btn(),
                    (180, 188, 205), WHITE, font_size=24, radius=14)

    def _retry_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 290, 570, 256, 56)

    def _menu_btn(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 34, 570, 256, 56)

    def _save_exit(self):
        if self._game_started:
            save_record("falling", self.game.selected_level,
                        self.game.selected_content,
                        self.total_answered, self.correct, self.score)
        # 退出游戏回到速度选择页（而非直接跳主菜单）
        self._picking_speed = True
        self._game_started = False
        self._speed_pick = SpeedPickScene(
            selected=getattr(self.game, "falling_speed_level", 1),
            on_confirm=self._on_speed_confirmed,
            on_back=lambda: self.game.change_scene(SCENE_MODE_SELECT),
        )
