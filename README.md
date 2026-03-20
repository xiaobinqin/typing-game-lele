# 打字大挑战 - 乐乐版

一款面向小学生（1-6年级）的跨平台键盘打字游戏，帮助小学生学习拼音和汉字。内容与人教版小学语文教材同步。

## 下载使用（macOS）

前往 [Releases](https://github.com/xiaobinqin/typing-game-lele/releases) 下载最新版本的 `typing-game-lele-macOS-vX.X.zip`，解压后双击 `.app` 即可运行。

> 首次打开时若系统提示"无法验证开发者"，请：
> 系统设置 → 隐私与安全性 → 仍要打开

## 功能特色

- **4种游戏模式**：消消乐、闯关模式、竞速模式、练习模式
- **4个难度等级**：启蒙级（1年级）/ 基础级（2年级）/ 进阶级（3-4年级）/ 熟练级（5-6年级）
- **6类练习内容**：声母、韵母、整体认读音节、拼音音节、汉字拼音、词语练习
- **题库同步人教版**：覆盖小学1-6年级生字词
- **消消乐速度可选**：慢速 / 中速 / 快速三档，随答题数量自动加速
- **本地学习记录**：自动保存每次游戏结果
- **竞速排行榜**：本地 Top 10 排行

## 从源码运行

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 启动游戏
python main.py
```

## 打包为 macOS .app

```bash
source venv/bin/activate
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
pyinstaller typing_game.spec --clean --noconfirm
# 输出位于 dist/打字大挑战-乐乐.app
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
├── typing_game.spec           # PyInstaller 打包配置
├── releases/                  # 发布包（zip）
├── data/
│   ├── phonics.json           # 拼音题库
│   ├── characters.json        # 汉字题库（人教版1-6年级）
│   └── words.json             # 词语题库
└── src/
    ├── game.py                # 主游戏引擎
    ├── utils/                 # 工具模块
    └── scenes/                # 各游戏场景
```

## 依赖

- [pygame](https://www.pygame.org/) >= 2.5.0
