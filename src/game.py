import pygame
import sys
import os

# 确保导入路径正确
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


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # 全局游戏状态
        self.selected_level = LEVEL_STARTER
        self.selected_content = CONTENT_INITIALS
        self.selected_content_idx = 0   # 记住模式选择页的选中练习内容索引
        self.selected_mode_idx = -1     # 记住上次进入的游戏模式索引（-1表示未选）
        self.falling_speed_level = 1    # 0=慢 1=中 2=快

        # 场景注册表（懒加载）
        self._scene_cache = {}
        self._scene_name = SCENE_MENU
        self._scene = self._load_scene(SCENE_MENU)

    def _load_scene(self, name: str):
        constructors = {
            SCENE_MENU:         MenuScene,
            SCENE_GRADE_SELECT: GradeSelectScene,
            SCENE_MODE_SELECT:  ModeSelectScene,
            SCENE_FALLING:      FallingScene,
            SCENE_CHALLENGE:    ChallengeScene,
            SCENE_SPEED:        SpeedScene,
            SCENE_PRACTICE:     PracticeScene,
            SCENE_LEADERBOARD:  LeaderboardScene,
        }
        cls = constructors.get(name)
        if cls is None:
            raise ValueError(f"未知场景：{name}")
        return cls(self)

    def change_scene(self, name: str):
        """切换场景，每次都重新创建以重置状态"""
        self._scene_name = name
        self._scene = self._load_scene(name)

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
