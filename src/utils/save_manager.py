import json
import os
import sys
from datetime import datetime


def _get_saves_dir():
    """打包环境下将存档写到用户主目录，避免写入只读的 _MEIPASS"""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.expanduser("~"), ".typing_game_lele", "saves")
    from src.utils.constants import SAVES_DIR
    return SAVES_DIR


_SAVES_DIR    = _get_saves_dir()
_RECORD_FILE  = os.path.join(_SAVES_DIR, "records.json")
_LEADER_FILE  = os.path.join(_SAVES_DIR, "leaderboard.json")

def _ensure_dir():
    os.makedirs(_SAVES_DIR, exist_ok=True)

def _load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def _save_json(path, data):
    _ensure_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- 学习记录 ----------

def save_record(mode: str, level: int, content_type: str,
                total: int, correct: int, score: int):
    records = _load_json(_RECORD_FILE, [])
    records.append({
        "time":         datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode":         mode,
        "level":        level,
        "content_type": content_type,
        "total":        total,
        "correct":      correct,
        "accuracy":     round(correct / total * 100, 1) if total else 0,
        "score":        score,
    })
    # 只保留最近200条
    _save_json(_RECORD_FILE, records[-200:])

def get_records():
    return _load_json(_RECORD_FILE, [])

# ---------- 排行榜 ----------

def save_leaderboard(name: str, score: int, mode: str = "speed"):
    board = _load_json(_LEADER_FILE, {})
    if mode not in board:
        board[mode] = []
    board[mode].append({
        "name":  name,
        "score": score,
        "time":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    board[mode] = sorted(board[mode], key=lambda x: x["score"], reverse=True)[:10]
    _save_json(_LEADER_FILE, board)

def get_leaderboard(mode: str = "speed"):
    board = _load_json(_LEADER_FILE, {})
    return board.get(mode, [])
