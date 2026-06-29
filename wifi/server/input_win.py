"""Windows 低延迟鼠标/滚轮注入（ctypes SendInput，子像素累积减少抖动）。"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800

WHEEL_DELTA = 120

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

# 子像素余量，避免每帧 round 造成阶梯感
_remainder_x = 0.0
_remainder_y = 0.0
_remainder_scroll = 0.0


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]

    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUT)]


def _send_mouse(flags: int, dx: int = 0, dy: int = 0, data: int = 0) -> None:
    inp = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dx, dy, data, flags, 0, 0))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def move_relative(dx: float, dy: float) -> None:
    global _remainder_x, _remainder_y
    if not dx and not dy:
        return
    _remainder_x += dx
    _remainder_y += dy
    mx = int(_remainder_x)
    my = int(_remainder_y)
    if mx:
        _remainder_x -= mx
    if my:
        _remainder_y -= my
    if mx or my:
        _send_mouse(MOUSEEVENTF_MOVE, mx, my)


def scroll_vertical(delta: float) -> None:
    global _remainder_scroll
    if not delta:
        return
    _remainder_scroll += delta
    steps = int(_remainder_scroll)
    if steps == 0:
        return
    _remainder_scroll -= steps
    _send_mouse(MOUSEEVENTF_WHEEL, data=steps * WHEEL_DELTA)


_BUTTON_FLAGS = {
    "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}


def button_down(button: str = "left") -> None:
    down, _ = _BUTTON_FLAGS.get(button, _BUTTON_FLAGS["left"])
    _send_mouse(down)


def button_up(button: str = "left") -> None:
    _, up = _BUTTON_FLAGS.get(button, _BUTTON_FLAGS["left"])
    _send_mouse(up)


def click(button: str = "left", count: int = 1) -> None:
    down, up = _BUTTON_FLAGS.get(button, _BUTTON_FLAGS["left"])
    for _ in range(max(1, count)):
        _send_mouse(down)
        _send_mouse(up)
