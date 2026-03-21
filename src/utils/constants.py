import os
import sys


def _get_base_dir():
    """兼容 PyInstaller 打包后的路径"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


BASE_DIR = _get_base_dir()

# 屏幕尺寸
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "打字大挑战-乐乐"

# 颜色
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
GRAY        = (180, 180, 180)
LIGHT_GRAY  = (230, 230, 230)
DARK_GRAY   = (80,  80,  80)

RED         = (220, 60,  60)
LIGHT_RED   = (255, 120, 120)
GREEN       = (60,  180, 60)
LIGHT_GREEN = (120, 220, 120)
BLUE        = (60,  120, 220)
LIGHT_BLUE  = (100, 180, 255)
YELLOW      = (255, 210, 0)
ORANGE      = (255, 140, 0)
PURPLE      = (140, 60,  200)
PINK        = (255, 100, 160)
CYAN        = (0,   200, 200)

# 主题色 —— 简洁蓝白风格
COLOR_PRIMARY    = (56,  132, 255)   # 主蓝色（鲜明）
COLOR_SECONDARY  = (255, 170, 0)     # 金黄色
COLOR_SUCCESS    = (40,  190, 95)    # 成功绿
COLOR_DANGER     = (225, 55,  55)    # 危险红
COLOR_BG_MAIN    = (245, 248, 254)   # 主背景（极浅蓝灰）
COLOR_BG_PANEL   = (255, 255, 255)   # 面板白
COLOR_TEXT_MAIN  = (28,  36,  64)    # 主文字（深蓝黑）
COLOR_TEXT_SUB   = (130, 138, 168)   # 副文字（蓝灰）
COLOR_BORDER     = (218, 224, 238)   # 边框色

# 字体路径（内置系统字体作为备选）
FONT_PATH_CN = os.path.join(BASE_DIR, "assets", "fonts", "chinese.ttf")

# 数据文件路径
DATA_DIR     = os.path.join(BASE_DIR, "data")
SAVES_DIR    = os.path.join(BASE_DIR, "saves")

# 游戏场景标识
SCENE_MENU        = "menu"
SCENE_GRADE_SELECT = "grade_select"
SCENE_MODE_SELECT  = "mode_select"
SCENE_FALLING     = "falling"
SCENE_CHALLENGE   = "challenge"
SCENE_SPEED       = "speed"
SCENE_PRACTICE    = "practice"
SCENE_RESULT      = "result"
SCENE_LEADERBOARD = "leaderboard"

# 难度等级
LEVEL_STARTER    = 0   # 启蒙级 - 1年级
LEVEL_BASIC      = 1   # 基础级 - 2年级
LEVEL_MIDDLE     = 2   # 进阶级 - 3/4年级
LEVEL_ADVANCED   = 3   # 熟练级 - 5/6年级

LEVEL_NAMES = {
    LEVEL_STARTER:  "启蒙级",
    LEVEL_BASIC:    "基础级",
    LEVEL_MIDDLE:   "进阶级",
    LEVEL_ADVANCED: "熟练级",
}

LEVEL_GRADES = {
    LEVEL_STARTER:  [1],
    LEVEL_BASIC:    [2],
    LEVEL_MIDDLE:   [3, 4],
    LEVEL_ADVANCED: [5, 6],
}

# 练习内容类型
CONTENT_INITIALS      = "initials"       # 声母
CONTENT_FINALS        = "finals"         # 韵母
CONTENT_WHOLE         = "whole"          # 整体认读
CONTENT_SYLLABLES     = "syllables"      # 音节
CONTENT_CHARACTERS    = "characters"     # 汉字
CONTENT_WORDS         = "words"          # 词语

CONTENT_NAMES = {
    CONTENT_INITIALS:   "声母练习",
    CONTENT_FINALS:     "韵母练习",
    CONTENT_WHOLE:      "整体认读",
    CONTENT_SYLLABLES:  "拼音音节",
    CONTENT_CHARACTERS: "汉字拼音",
    CONTENT_WORDS:      "词语练习",
}

# 消除模式参数
FALLING_MIN_SPEED   = 8     # 最快下落速度（帧数/px，越小越快）
FALLING_SPEED_STEP  = 3     # 每消除N个加速一次
FALLING_MAX_ITEMS   = 5     # 屏幕同时最多几个

# 消消乐速度档位：(初始speed帧数, 下落步长px, 生成间隔帧)
FALLING_SPEED_LEVELS = {
    0: (45, 2, 90),    # 慢速
    1: (28, 3, 60),    # 中速
    2: (16, 4, 38),    # 快速
}
FALLING_SPEED_NAMES = {0: "慢速", 1: "中速", 2: "快速"}
FALLING_SPEED_COLORS = {0: (60, 185, 120), 1: (255, 160, 40), 2: (220, 60, 60)}

# 闯关模式参数
CHALLENGE_TOTAL     = 20    # 每关题目数
CHALLENGE_PASS_RATE = 0.6   # 过关正确率

# 竞速模式参数
SPEED_DURATION      = 60    # 秒

# 音效文件（占位路径）
SOUND_CORRECT  = os.path.join(BASE_DIR, "assets", "sounds", "correct.wav")
SOUND_WRONG    = os.path.join(BASE_DIR, "assets", "sounds", "wrong.wav")
SOUND_LEVELUP  = os.path.join(BASE_DIR, "assets", "sounds", "levelup.wav")
SOUND_GAMEOVER = os.path.join(BASE_DIR, "assets", "sounds", "gameover.wav")
