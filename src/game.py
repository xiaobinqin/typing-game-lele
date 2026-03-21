import pygame
import sys
import os
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.constants import *
from src.scenes.menu_scene import MenuScene
from src.scenes.grade_select_scene import GradeSelectScene
from src.scenes.mode_select_scene import ModeSelectScene
from src.scenes.falling_scene import FallingScene
from src.scenes.challenge_scene import ChallengeScene
from src.scenes.speed_scene import SpeedScene
from src.scenes.practice_scene import PracticeScene
from src.scenes.leaderboard_scene import LeaderboardScene


@dataclass
class GameState:
    """全局游戏状态，集中管理跨场景共享数据"""
    selected_level: int       = LEVEL_STARTER
    selected_content: str     = CONTENT_INITIALS
    selected_content_idx: int = 0       # 模式选择页练习内容的选中索引
    selected_mode_idx: int    = -1      # 模式选择页上次进入的模式索引
    falling_speed_level: int  = 1       # 消消乐速度档位（0慢/1中/2快）


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.state = GameState()

        # 将 GameState 字段代理到 self，保持各场景的兼容访问方式
        # e.g. self.selected_level 等价于 self.state.selected_level
        self._scene_name = SCENE_MENU
        self._scene = self._load_scene(SCENE_MENU)

    # ── GameState 属性代理 ──────────────────────────────────────
    def __getattr__(self, name):
        if name != "state" and hasattr(GameState, name):
            return getattr(self.state, name)
        raise AttributeError(f"'Game' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name != "state" and "state" in self.__dict__ and hasattr(GameState, name):
            setattr(self.state, name, value)
        else:
            super().__setattr__(name, value)

    # ── 场景管理 ────────────────────────────────────────────────
    def _load_scene(self, name: str):
        constructors = {
            SCENE_MENU:          MenuScene,
            SCENE_GRADE_SELECT:  GradeSelectScene,
            SCENE_MODE_SELECT:   ModeSelectScene,
            SCENE_FALLING:       FallingScene,
            SCENE_CHALLENGE:     ChallengeScene,
            SCENE_SPEED:         SpeedScene,
            SCENE_PRACTICE:      PracticeScene,
            SCENE_LEADERBOARD:   LeaderboardScene,
        }
        cls = constructors.get(name)
        if cls is None:
            raise ValueError(f"未知场景：{name}")
        return cls(self)

    def change_scene(self, name: str):
        """切换场景，每次都重新创建以重置状态"""
        self._scene_name = name
        self._scene = self._load_scene(name)

    # ── 主循环 ──────────────────────────────────────────────────
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._scene.handle_event(event)

            self._scene.update()
            self._scene.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
