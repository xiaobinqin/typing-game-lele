# 打字大挑战 - 乐乐版

一款面向小学生（1-6年级）的跨平台键盘打字游戏，帮助小学生学习拼音和汉字。内容与人教版小学语文教材同步。

## 功能特色

- **4种游戏模式**：消消乐、闯关模式、竞速模式、练习模式
- **4个难度等级**：启蒙级（1年级）/ 基础级（2年级）/ 进阶级（3-4年级）/ 熟练级（5-6年级）
- **6类练习内容**：声母、韵母、整体认读音节、拼音音节、汉字拼音、词语练习
- **题库同步人教版**：覆盖小学1-6年级生字词
- **消消乐速度可选**：慢速 / 中速 / 快速三档，随答题数量自动加速
- **本地学习记录**：自动保存每次游戏结果
- **竞速排行榜**：本地 Top 10 排行

## 运行环境

- Python 3.9+
- Windows / macOS

## 快速开始

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 安装依赖（国内镜像）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 启动游戏
python main.py
```

## 游戏操作

| 操作 | 说明 |
|------|------|
| 键盘输入 | 逐个字母键入拼音 |
| Enter | 确认提交答案 |
| Backspace | 删除最后一个字母 |
| ← → | 练习模式切换题目 |
| Esc | 退出当前模式 |

## 项目结构

```
打字游戏/
├── main.py                    # 启动入口
├── requirements.txt           # 依赖清单
├── data/
│   ├── phonics.json           # 拼音题库
│   ├── characters.json        # 汉字题库（人教版1-6年级）
│   └── words.json             # 词语题库
├── saves/                     # 本地存档（运行时自动生成）
└── src/
    ├── game.py                # 主游戏引擎
    ├── utils/                 # 工具模块
    └── scenes/                # 各游戏场景
```

## 依赖

- [pygame](https://www.pygame.org/) >= 2.5.0
