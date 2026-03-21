# 部署与打包指南 — 打字大挑战·乐乐版

## 1. 开发环境搭建

### 1.1 前置条件

| 工具 | 最低版本 | 获取方式 |
|------|----------|----------|
| Python | 3.9 | https://www.python.org/downloads/ |
| pip | 21.0+ | 随 Python 自带 |
| Git | 2.x | https://git-scm.com/ |

### 1.2 克隆项目

```bash
git clone https://github.com/xiaobinqin/typing-game-lele.git
cd typing-game-lele
```

### 1.3 创建虚拟环境

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 1.4 安装依赖

```bash
# 使用国内镜像加速安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.5 运行游戏

```bash
python main.py
```

---

## 2. macOS 打包为 `.app`

### 2.1 安装 PyInstaller

```bash
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.2 执行打包

```bash
pyinstaller typing_game.spec --clean --noconfirm
```

打包完成后，应用位于：

```
dist/打字大挑战-乐乐.app
```

### 2.3 制作发布 zip

```bash
mkdir -p releases
cd dist
zip -r "../releases/typing-game-lele-macOS-v1.0.zip" "打字大挑战-乐乐.app"
cd ..
```

> **注意**：zip 文件名使用英文，避免上传 GitHub Releases 时文件名乱码。

### 2.4 首次运行提示（macOS Gatekeeper）

由于应用未经过 Apple 公证，首次双击时系统会提示"无法验证开发者"。解决方法：

**方法一（推荐）**：
1. 右键点击 `.app` → 选择"打开"
2. 在弹出窗口中点击"打开"

**方法二**：
1. 系统设置 → 隐私与安全性
2. 找到被阻止的应用，点击"仍要打开"

**方法三（终端）**：
```bash
xattr -cr /path/to/打字大挑战-乐乐.app
```

---

## 3. Windows 打包为 `.exe`（参考）

> 当前项目主要支持 macOS，Windows 打包为规划功能。

```bash
# 安装依赖
pip install pygame pyinstaller

# 创建 Windows spec（示例，需根据实际字体路径调整）
pyinstaller --onefile --noconsole \
  --add-data "data;data" \
  --add-data "assets;assets" \
  --name "typing-game-lele" \
  main.py
```

---

## 4. 发布到 GitHub Releases

### 4.1 前置：安装 GitHub CLI

```bash
# macOS
brew install gh

# 登录
gh auth login
```

### 4.2 创建 Release 并上传

```bash
# 打 Tag
git tag v1.0.0
git push origin v1.0.0

# 创建 Release 并上传 zip
gh release create v1.0.0 \
  "releases/typing-game-lele-macOS-v1.0.zip" \
  --title "v1.0.0 - 初始正式版" \
  --notes "首个正式版本，支持 4 种游戏模式，内容与人教版同步。"
```

---

## 5. 存档文件位置

| 环境 | 存档路径 |
|------|----------|
| 源码运行 | `项目根目录/saves/` |
| macOS `.app` | `~/.typing_game_lele/saves/` |

> 存档文件包含：
> - `records.json`：每局游戏记录
> - `leaderboard.json`：竞速模式排行榜

若需重置存档，删除对应目录下的 JSON 文件即可。

---

## 6. 常见问题

### Q：运行时提示 `No module named 'pygame'`

确认已激活虚拟环境并安装依赖：

```bash
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q：字体显示为方块（豆腐块）

项目依赖内置字体文件。请确认 `assets/fonts/` 目录下存在字体文件，或在运行时检查 `font_manager.py` 的字体回退逻辑。

### Q：macOS `.app` 打开无任何反应

在终端中直接运行排查错误：

```bash
./dist/打字大挑战-乐乐.app/Contents/MacOS/typing-game-lele
```

### Q：游戏记录/排行榜数据丢失

打包后存档路径变更为 `~/.typing_game_lele/saves/`，源码运行时的 `saves/` 目录数据不会自动迁移，需手动复制。

### Q：如何修改游戏题库

直接编辑 `data/` 目录下的 JSON 文件，格式参考 [ARCHITECTURE.md](./ARCHITECTURE.md) 第 4 节。

---

## 7. 项目依赖版本

```
pygame>=2.5.0
pyinstaller>=6.0.0
```

更新依赖：

```bash
pip install --upgrade pygame pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
```
