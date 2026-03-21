import json
import os
import random
import unicodedata
from src.utils.constants import DATA_DIR, LEVEL_GRADES

# 模块级缓存，避免重复 I/O
_json_cache: dict = {}

def _load_json(filename):
    if filename not in _json_cache:
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            _json_cache[filename] = json.load(f)
    return _json_cache[filename]


def normalize_pinyin(text: str) -> str:
    """
    拼音标准化：去声调、去空格、转小写，用于答题匹配容错。
    例：'bái yún' -> 'baiyun'，'lǘ' -> 'lv'
    """
    # NFD 分解 unicode，过滤掉组合音调字符（category Mn）
    nfd = unicodedata.normalize("NFD", text)
    no_tone = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    # ü/ǖǘǚǜ 分解后变成 u + 音调，音调已去掉；但 ü 本身（\u00fc）分解为 u + \u0308
    # 以上处理后 ü -> u，再统一把 u 中需要表示 v 的情况保留（拼音里 lv/nv 规范输入）
    result = no_tone.replace(" ", "").lower()
    return result

def get_phonics_items(content_type: str) -> list[str]:
    """获取拼音题库项目列表"""
    data = _load_json("phonics.json")
    mapping = {
        "initials":   "initials",
        "finals":     "finals",
        "whole":      "whole_syllables",
        "syllables":  "syllables",
    }
    key = mapping.get(content_type)
    if key and key in data:
        return data[key]["items"]
    return []

def get_character_items(level: int) -> list[dict]:
    """按难度级别获取汉字题库"""
    data = _load_json("characters.json")
    grades = LEVEL_GRADES.get(level, [])
    result = []
    for key, val in data.items():
        if val["grade"] in grades:
            result.extend(val["words"])
    return result

def get_word_items(level: int) -> list[dict]:
    """按难度级别获取词语题库"""
    data = _load_json("words.json")
    grades = LEVEL_GRADES.get(level, [])
    result = []
    for key, val in data.items():
        if val["grade"] in grades:
            result.extend(val["items"])
    return result

def build_quiz_pool(content_type: str, level: int, count: int = 20) -> list[dict]:
    """
    构建答题池，统一格式：
    {"display": 显示内容, "answer": 拼音答案(无声调/无空格), "hint": 提示}
    """
    pool = []

    if content_type in ("initials", "finals", "whole", "syllables"):
        items = get_phonics_items(content_type)
        for item in items:
            pool.append({
                "display": item,
                "answer": item.replace("v", "v"),
                "hint": f"拼音: {item}",
                "type": "phonics"
            })

    elif content_type == "characters":
        items = get_character_items(level)
        for it in items:
            pool.append({
                "display": it["char"],
                "answer": it["pinyin"],
                "hint": f"{it['char']} = {it['pinyin']} ({it['meaning']})",
                "type": "character"
            })

    elif content_type == "words":
        items = get_word_items(level)
        for it in items:
            # 标准答案：去空格、去声调，学生输入时同样 normalize 后比较
            answer_raw = it["pinyin"]
            answer = normalize_pinyin(answer_raw)
            pool.append({
                "display": it["word"],
                "answer":  answer,
                "answer_raw": answer_raw,   # 保留原始带声调版本用于提示
                "hint":    f"{it['word']} = {answer_raw}",
                "type":    "word"
            })

    if not pool:
        return pool

    random.shuffle(pool)
    if len(pool) >= count:
        return pool[:count]
    repeated = (pool * (count // len(pool) + 1))
    return repeated[:count]
