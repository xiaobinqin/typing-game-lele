# 打字大挑战 · 乐乐版

> 一款面向小学 1—6 年级学生的跨平台键盘打字游戏，帮助学生在趣味游戏中巩固拼音与汉字知识。  
> 内容与**人教版小学语文教材**全程同步。

---

## 功能亮点

| 特性 | 说明 |
|------|------|
| 🎮 4 种游戏模式 | 消消乐 · 闯关模式 · 竞速模式 · 练习模式 |
| 📚 6 类练习内容 | 声母 · 韵母 · 整体认读 · 拼音音节 · 汉字 · 词语 |
| 🎓 4 个难度等级 | 启蒙级（1年级）→ 熟练级（5—6年级）|
| ⚡ 速度可调 | 消消乐支持慢速 / 中速 / 快速三档 |
| 🏆 本地排行榜 | 竞速模式 Top 10，支持昵称录入 |
| 💾 学习记录 | 自动保存每次游戏结果，历史可查 |
| 🔄 状态记忆 | 返回选择页时自动恢复上次的年级、内容、模式选择 |

---

## 游戏截图（游戏模式一览）

| 消消乐 | 闯关模式 | 竞速模式 | 练习模式 |
|--------|----------|----------|----------|
| 字从天降，打出拼音消除 | 20题闯关，三星评价 | 60秒极速挑战 | 无压力随意练习 |

---

## 快速开始

### macOS 直接运行

1. 前往 [Releases](https://github.com/xiaobinqin/typing-game-lele/releases) 下载最新 `typing-game-lele-macOS-vX.X.zip`
2. 解压，双击 `.app` 即可运行

> **首次打开提示"无法验证开发者"？**  
> 系统设置 → 隐私与安全性 → 点击"仍要打开"

### 源码运行（所有平台）

```bash
# 1. 克隆项目
git clone https://github.com/xiaobinqin/typing-game-lele.git
cd typing-game-lele

# 2. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 启动游戏
python main.py
```

---

## 操作说明

| 操作 | 说明 |
|------|------|
| 键盘字母键 | 逐字母输入拼音 |
| `Enter` | 提交答案 / 下一题 |
| `Backspace` | 删除最后一个字母 |
| `← →` | 练习模式切换题目 |
| `Esc` | 退出当前模式，返回上一页 |
| 鼠标点击 | 菜单导航、按钮交互 |

---

## 项目结构

```
打字游戏/
├── main.py                      # 程序入口
├── requirements.txt             # Python 依赖
├── typing_game.spec             # PyInstaller 打包配置（macOS）
├── REQUIREMENTS.md              # 产品需求文档
├── ARCHITECTURE.md              # 技术架构文档
├── DEPLOYMENT.md                # 部署与打包指南
│
├── data/                        # 题库（JSON，人教版同步）
│   ├── phonics.json             # 拼音题库
│   ├── characters.json          # 汉字题库
│   └── words.json               # 词语题库
│
├── assets/
│   ├── fonts/                   # 内置中文字体
│   ├── images/                  # 图片资源（预留）
│   └── sounds/                  # 音效资源（预留）
│
└── src/
    ├── game.py                  # 主游戏引擎 & 场景管理
    ├── scenes/                  # 各游戏场景
    │   ├── menu_scene.py
    │   ├── grade_select_scene.py
    │   ├── mode_select_scene.py
    │   ├── falling_scene.py
    │   ├── challenge_scene.py
    │   ├── speed_scene.py
    │   ├── practice_scene.py
    │   └── leaderboard_scene.py
    └── utils/                   # 工具模块
        ├── constants.py
        ├── font_manager.py
        ├── data_loader.py
        ├── save_manager.py
        └── draw_utils.py
```

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [REQUIREMENTS.md](./REQUIREMENTS.md) | 完整产品需求，含功能列表、用户故事、版本规划 |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 技术架构，含模块设计、数据格式、扩展建议 |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | 开发环境搭建、打包发布、常见问题 |

---

## 依赖

- [pygame](https://www.pygame.org/) >= 2.5.0
- Python >= 3.9

---

## License

MIT License © 2026 乐乐版团队
