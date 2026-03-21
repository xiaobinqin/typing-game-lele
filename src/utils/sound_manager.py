"""
音效管理器 — 用 pygame.sndarray 程序合成音效，无需外部 .wav 文件。
提供：correct（答对）, wrong（答错）, land（落地警告）, victory（通关）
"""
import pygame
import numpy as np

_sounds: dict = {}
_initialized = False


def _init():
    global _initialized
    if _initialized:
        return
    try:
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        _initialized = True
        _build_sounds()
    except Exception:
        _initialized = False


def _sine_wave(freq: float, duration: float, volume: float = 0.5,
               sample_rate: int = 44100) -> np.ndarray:
    """生成单频正弦波"""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = (np.sin(2 * np.pi * freq * t) * volume * 32767).astype(np.int16)
    return wave


def _envelope(wave: np.ndarray, attack: float = 0.01, release: float = 0.1) -> np.ndarray:
    """添加淡入淡出包络"""
    n = len(wave)
    atk = max(1, int(n * attack))
    rel = max(1, int(n * release))
    env = np.ones(n)
    env[:atk]  = np.linspace(0, 1, atk)
    env[-rel:] = np.linspace(1, 0, rel)
    return (wave * env).astype(np.int16)


def _make_sound(wave: np.ndarray) -> pygame.mixer.Sound:
    sound = pygame.sndarray.make_sound(wave)
    return sound


def _build_sounds():
    sr = 44100
    # 答对：短促上升两音
    w1 = _envelope(_sine_wave(880, 0.07, 0.4, sr), release=0.3)
    w2 = _envelope(_sine_wave(1320, 0.10, 0.4, sr), release=0.4)
    correct_wave = np.concatenate([w1, np.zeros(int(sr * 0.03), dtype=np.int16), w2])
    _sounds["correct"] = _make_sound(correct_wave)

    # 答错：低沉短音
    w = _envelope(_sine_wave(220, 0.18, 0.35, sr), attack=0.02, release=0.5)
    _sounds["wrong"] = _make_sound(w)

    # 落地警告：急促两短音
    w1 = _envelope(_sine_wave(440, 0.06, 0.45, sr), release=0.4)
    w2 = _envelope(_sine_wave(440, 0.06, 0.45, sr), release=0.4)
    land_wave = np.concatenate([w1, np.zeros(int(sr * 0.04), dtype=np.int16), w2])
    _sounds["land"] = _make_sound(land_wave)

    # 胜利：四音上升
    freqs = [523, 659, 784, 1047]
    parts = []
    for f in freqs:
        parts.append(_envelope(_sine_wave(f, 0.12, 0.4, sr), release=0.3))
        parts.append(np.zeros(int(sr * 0.02), dtype=np.int16))
    _sounds["victory"] = _make_sound(np.concatenate(parts))

    # 一击多消奖励音：快速上升三音
    freqs2 = [784, 988, 1175]
    parts2 = []
    for f in freqs2:
        parts2.append(_envelope(_sine_wave(f, 0.09, 0.4, sr), release=0.3))
        parts2.append(np.zeros(int(sr * 0.015), dtype=np.int16))
    _sounds["multi"] = _make_sound(np.concatenate(parts2))


def play(name: str):
    """播放指定音效，失败时静默"""
    if not _initialized:
        _init()
    s = _sounds.get(name)
    if s:
        try:
            s.play()
        except Exception:
            pass


# 模块导入时自动初始化
_init()
