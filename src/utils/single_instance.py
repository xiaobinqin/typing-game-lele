"""
单例实例锁 — 保证同一时刻只有一个游戏进程在运行。

实现方式：
  绑定本地 TCP 端口（127.0.0.1:47531）。
  - 第一个实例成功绑定：持有单例，游戏正常启动
  - 后续实例绑定失败：说明已有实例在运行，聚焦已有窗口后退出

优点：跨平台（macOS / Windows / Linux）无需第三方库，
      进程结束后端口自动释放，无"锁文件残留"问题。
"""
import os
import sys
import socket

# 使用固定的本地端口作为单例信号
_LOCK_PORT = 47531
_LOCK_HOST = "127.0.0.1"


class SingleInstance:
    """
    用法：
        lock = SingleInstance()
        if not lock.acquired:
            focus_existing_window()
            sys.exit(0)
        # 正常启动 ...
    """

    def __init__(self):
        self._sock = None
        self.acquired = self._try_acquire()

    def _try_acquire(self) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            s.bind((_LOCK_HOST, _LOCK_PORT))
            s.listen(1)
            self._sock = s
            return True
        except OSError:
            # 端口已被占用：已有实例在运行
            if self._sock:
                try:
                    self._sock.close()
                except Exception:
                    pass
                self._sock = None
            return False

    def release(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def __del__(self):
        self.release()


def focus_existing_window():
    """尝试将已有游戏窗口聚焦到前台"""
    try:
        if sys.platform == "darwin":
            _focus_macos()
        elif sys.platform == "win32":
            _focus_windows()
    except Exception:
        pass


def _focus_macos():
    """macOS：用 AppleScript 激活标题含「打字大挑战」的窗口"""
    import subprocess
    script = '''
    tell application "System Events"
        set procs to every process whose name contains "Python"
        repeat with p in procs
            set wins to every window of p
            repeat with w in wins
                if name of w contains "打字大挑战" then
                    set frontmost of p to true
                    perform action "AXRaise" of w
                    return
                end if
            end repeat
        end repeat
    end tell
    '''
    subprocess.run(["osascript", "-e", script],
                   capture_output=True, timeout=3)


def _focus_windows():
    """Windows：用 win32gui 找到标题含「打字大挑战」的窗口并激活"""
    try:
        import win32gui
        import win32con

        def enum_cb(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if "打字大挑战" in title:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)

        win32gui.EnumWindows(enum_cb, None)
    except ImportError:
        pass
