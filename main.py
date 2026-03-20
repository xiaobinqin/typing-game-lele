#!/usr/bin/env python3
"""
打字大挑战 - 乐乐版
小学生拼音与汉字学习打字游戏
支持平台：Windows / macOS
"""
import sys
import os

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
