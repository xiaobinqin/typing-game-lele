# 架构文档 — 打字大挑战·乐乐版

## 1. 技术栈

| 层次 | 技术 |
|------|------|
| 语言 | Python 3.9+ |
| 渲染引擎 | Pygame 2.5+ |
| 数据存储 | JSON 文件（题库 + 存档） |
| 打包工具 | PyInstaller 6.0+ |

---

## 2. 目录结构

```
打字游戏/
├── main.py                      # 程序入口，初始化 Pygame 并启动 Game
├── requirements.txt             # Python 依赖
├── typing_game.spec             # PyInstaller 打包配置
│
├── data/                        # 题库数据（JSON，与代码解耦）
│   ├── phonics.json             # 拼音题库：声母/韵母/整体认读/音节
│   ├── characters.json          # 汉字题库：人教版 1—6 年级生字
│   └── words.json               # 词语题库：人教版 1—6 年级词语
│
├── assets/
│   ├── fonts/                   # 内置中文字体
│   ├── images/                  # 图片资源（预留）
│   └── sounds/                  # 音效文件（预留）
│
├── saves/                       # 运行时生成，本地存档
│   ├── records.json             # 每局游戏记录
│   └── leaderboard.json         # 竞速模式排行榜
│
└── src/
    ├── game.py                  # 主游戏类：场景管理器 + 全局状态
    ├── scenes/                  # 各场景实现
    │   ├── menu_scene.py        # 主菜单
    │   ├── grade_select_scene.py# 年级选择
    │   ├── mode_select_scene.py # 模式选择
    │   ├── falling_scene.py     # 消消乐模式（含内置速度选择）
    │   ├── challenge_scene.py   # 闯关模式
    │   ├── speed_scene.py       # 竞速模式
    │   ├── practice_scene.py    # 练习模式
    │   └── leaderboard_scene.py # 排行榜
    └── utils/
        ├── constants.py         # 全局常量（颜色、尺寸、场景名、速度配置等）
        ├── font_manager.py      # 字体加载与缓存（兼容 PyInstaller）
        ├── data_loader.py       # 题库加载 & 测题池构建
        ├── save_manager.py      # 存档读写（路径兼容打包环境）
        └── draw_utils.py        # UI 绘制工具库（按钮/卡片/输入框等）
```

---

## 3. 核心设计

### 3.1 场景管理（Game 类）

`Game` 类是整个程序的中枢，负责：

1. **主循环**：事件分发 → 状态更新 → 渲染 → 帧率控制（60 FPS）
2. **场景切换**：`change_scene(name)` 按名称重建场景实例（每次重置状态）
3. **全局状态持久化**：跨场景传递用户选择，返回时恢复

```python
class Game:
    selected_level        # 当前选中年级
    selected_content      # 当前选中内容类型（字符串 ID）
    selected_content_idx  # 当前选中内容索引（用于 UI 恢复高亮）
    selected_mode_idx     # 上次进入的游戏模式索引（用于 UI 恢复高亮）
    falling_speed_level   # 消消乐速度档位（0=慢 1=中 2=快）
```

### 3.2 场景接口（统一约定）

每个场景类均实现以下三个方法，`Game` 主循环统一调用：

```python
class XxxScene:
    def handle_event(self, event): ...  # 处理 Pygame 事件
    def update(self):              ...  # 每帧逻辑更新
    def draw(self, surface):       ...  # 每帧渲染
```

### 3.3 导航流程

```
MenuScene
    │  点击"开始游戏"
    ▼
GradeSelectScene
    │  点击年级卡片
    ▼
ModeSelectScene
    │  选择内容类型 + 点击模式卡片
    ├──▶ FallingScene（内置 SpeedPickScene 速度选择子界面）
    ├──▶ ChallengeScene
    ├──▶ SpeedScene
    └──▶ PracticeScene

任意游戏模式 ──退出──▶ ModeSelectScene（恢复选中状态）
消消乐游戏中  ──退出──▶ SpeedPickScene（返回速度选择）
```

### 3.4 题库加载（data_loader.py）

```
build_quiz_pool(content_type, level, count)
    │
    ├─ 读取对应 JSON 文件
    ├─ 按 level 过滤数据
    ├─ 随机打乱
    └─ 返回 [{"display": "汉字/拼音", "answer": "拼音"}, ...]
```

- `display`：题目展示内容（汉字、声母等）
- `answer`：标准答案（小写拼音字符串）

### 3.5 UI 绘制工具（draw_utils.py）

集中封装所有可复用 UI 组件，避免各场景重复绘制逻辑：

| 函数 | 说明 |
|------|------|
| `draw_text` | 渲染文字，支持居中/透明度/加粗 |
| `draw_button` | 带阴影/hover 效果的矩形按钮 |
| `draw_card` | 带阴影的圆角卡片 |
| `draw_input_box` | 带光标的输入框 |
| `draw_progress_bar` | 进度/血量条 |
| `draw_badge` | 胶囊标签 |
| `draw_divider` | 分割线 |
| `draw_star` / `draw_heart` | 星级/生命图标 |

### 3.6 存档路径策略

| 环境 | 存档路径 |
|------|----------|
| 源码运行 | `项目根目录/saves/` |
| PyInstaller 打包 | `~/.typing_game_lele/saves/`（用户主目录，可读写）|

通过 `save_manager._get_saves_dir()` 自动判断，避免写入只读的 `.app` 包内部。

---

## 4. 数据格式

### 4.1 题库 JSON 通用结构

```json
{
  "level_0": [
    { "display": "b",   "answer": "b" },
    { "display": "p",   "answer": "p" }
  ],
  "level_1": [ ... ],
  "level_2": [ ... ],
  "level_3": [ ... ]
}
```

### 4.2 游戏记录 JSON

```json
[
  {
    "mode": "challenge",
    "level": 0,
    "content": "initials",
    "total": 20,
    "correct": 18,
    "score": 180,
    "time": "2026-03-21 10:30:00"
  }
]
```

### 4.3 排行榜 JSON

```json
{
  "speed": [
    { "name": "小明", "score": 350, "time": "2026-03-21 10:30:00" }
  ]
}
```

---

## 5. 关键常量配置（constants.py）

| 常量 | 默认值 | 说明 |
|------|--------|------|
| `SCREEN_WIDTH / HEIGHT` | 1024 × 768 | 窗口尺寸 |
| `FPS` | 60 | 帧率 |
| `FALLING_SPEED_LEVELS` | `{0:(45,2,90), 1:(28,3,60), 2:(16,4,38)}` | 消消乐速度档（帧数, 步长px, 生成间隔帧）|
| `CHALLENGE_TOTAL` | 20 | 闯关每关题数 |
| `CHALLENGE_PASS_RATE` | 0.6 | 闯关过关正确率 |
| `SPEED_DURATION` | 60 | 竞速时长（秒）|

---

## 6. 扩展建议

| 方向 | 实现思路 |
|------|----------|
| 新增游戏模式 | 在 `src/scenes/` 新建场景类，在 `Game._load_scene` 中注册，在 `mode_select_scene.py` 的 `MODES` 中添加入口 |
| 新增题库内容 | 在 `data/` 中按格式添加 JSON，在 `data_loader.py` 中适配加载逻辑 |
| 音效系统 | 在 `assets/sounds/` 放置 `.wav` 文件，在各场景答题回调中调用 `pygame.mixer` |
| 网络排行榜 | 替换 `save_manager` 中的本地 JSON 读写为 HTTP API 调用 |
| Windows 打包 | 新增 `.spec` 文件，调整字体路径为 Windows 系统字体，`pyinstaller xxx.spec` 生成 `.exe` |
