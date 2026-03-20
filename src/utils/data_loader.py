import json
import os
import random
from src.utils.constants import DATA_DIR, LEVEL_GRADES

def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

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
            # 答案：去掉空格
            answer = it["pinyin"].replace(" ", "")
            pool.append({
                "display": it["word"],
                "answer": answer,
                "hint": f"{it['word']} = {it['pinyin']}",
                "type": "word"
            })

    if not pool:
        return pool

    random.shuffle(pool)
    if len(pool) >= count:
        return pool[:count]
    repeated = (pool * (count // len(pool) + 1))
    return repeated[:count]
