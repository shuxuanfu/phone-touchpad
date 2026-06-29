"""
Phone Touchpad — WiFi 版
用手机浏览器当 Windows 触控板，通过局域网 WebSocket 连接。
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import logging
import socket
import sys
import threading
import webbrowser
from pathlib import Path

from aiohttp import web
from pynput.keyboard import Controller as KeyboardController, Key

# 保证同目录模块可导入
sys.path.insert(0, str(Path(__file__).resolve().parent))
import input_win

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("phone-touchpad-wifi")

WIFI_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = WIFI_ROOT / "client" / "web"

keyboard = KeyboardController()

_KEY_ALIASES = {
    "ctrl": Key.ctrl,
    "control": Key.ctrl,
    "alt": Key.alt,
    "shift": Key.shift,
    "win": Key.cmd,
}

_held_hotkeys: list[str] = []

# 服务端合并移动/滚动，以固定频率刷入系统（约 120Hz）
TICK_SEC = 1 / 120
# 滚轮每 N 次 tick 才真正 SendInput 一次（降低系统输入压力）
SCROLL_FLUSH_EVERY = 3  # ≈40Hz
# 单次刷入上限，避免异常积压
MAX_PENDING_MOVE = 400.0
MAX_PENDING_SCROLL = 400.0

_move_lock = threading.Lock()
_pending_move = [0.0, 0.0]
_pending_scroll = 0.0
_input_lock = threading.Lock()
_scroll_loop_tick = 0


def local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _release_all_hotkeys() -> None:
    global _held_hotkeys
    if not _held_hotkeys:
        return
    for name in reversed(_held_hotkeys):
        key = _KEY_ALIASES.get(name.lower())
        if key is not None:
            keyboard.release(key)
    _held_hotkeys = []


def release_all_hotkeys() -> None:
    with _input_lock:
        _release_all_hotkeys()


def _hotkey_down(keys: list[str]) -> None:
    global _held_hotkeys
    for name in keys:
        if name in _held_hotkeys:
            continue
        key = _KEY_ALIASES.get(name.lower())
        if key is None:
            log.warning("未知按键: %s", name)
            continue
        keyboard.press(key)
        _held_hotkeys.append(name)


def _hotkey_up(keys: list[str]) -> None:
    global _held_hotkeys
    for name in reversed(keys):
        if name not in _held_hotkeys:
            continue
        key = _KEY_ALIASES.get(name.lower())
        if key is None:
            continue
        keyboard.release(key)
        _held_hotkeys.remove(name)


def hotkey_down(keys: list[str]) -> None:
    with _input_lock:
        _hotkey_down(keys)


def hotkey_up(keys: list[str]) -> None:
    with _input_lock:
        _hotkey_up(keys)


def queue_move(dx: float, dy: float) -> None:
    with _move_lock:
        _pending_move[0] = max(-MAX_PENDING_MOVE, min(MAX_PENDING_MOVE, _pending_move[0] + dx))
        _pending_move[1] = max(-MAX_PENDING_MOVE, min(MAX_PENDING_MOVE, _pending_move[1] + dy))


def queue_scroll(dy: float) -> None:
    global _pending_scroll
    with _move_lock:
        _pending_scroll = max(-MAX_PENDING_SCROLL, min(MAX_PENDING_SCROLL, _pending_scroll + dy))


def flush_motion(*, force_scroll: bool = False) -> None:
    global _pending_scroll, _scroll_loop_tick
    with _move_lock:
        dx, dy = _pending_move[0], _pending_move[1]
        scroll = _pending_scroll
        _pending_move[0] = 0.0
        _pending_move[1] = 0.0
        _pending_scroll = 0.0

    if dx or dy or scroll:
        with _input_lock:
            if dx or dy:
                input_win.move_relative(dx, dy)
            if scroll:
                input_win.scroll_accumulate(scroll)

    _scroll_loop_tick += 1
    if force_scroll or _scroll_loop_tick >= SCROLL_FLUSH_EVERY:
        _scroll_loop_tick = 0
        with _input_lock:
            input_win.scroll_flush()


def handle_action(msg: dict) -> None:
    kind = msg.get("type")

    if kind == "hello":
        log.info("客户端已连接: %s", msg.get("device", "unknown")[:80])
        return

    if kind == "ping":
        return

    if kind == "move":
        queue_move(float(msg.get("dx", 0)), float(msg.get("dy", 0)))
        return

    if kind == "scroll":
        queue_scroll(float(msg.get("dy", 0)))
        return

    # 点击前先刷完排队中的移动，避免点击位置偏移
    flush_motion(force_scroll=True)

    with _input_lock:
        if kind == "down":
            input_win.button_down(msg.get("button", "left"))
        elif kind == "up":
            input_win.button_up(msg.get("button", "left"))
        elif kind == "click":
            input_win.click(msg.get("button", "left"), int(msg.get("count", 1)))
        elif kind == "type":
            text = msg.get("text", "")
            if text:
                keyboard.type(text)
        elif kind == "hotkey_down":
            _hotkey_down(msg.get("keys", ["ctrl", "alt"]))
        elif kind == "hotkey_up":
            _hotkey_up(msg.get("keys", ["ctrl", "alt"]))
        else:
            log.warning("未知消息: %s", kind)


def motion_loop(stop: threading.Event) -> None:
    while not stop.wait(TICK_SEC):
        flush_motion()


_motion_stop = threading.Event()
_motion_thread = threading.Thread(target=motion_loop, args=(_motion_stop,), daemon=True)


def start_motion_thread() -> None:
    if not _motion_thread.is_alive():
        _motion_thread.start()


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    # heartbeat 放宽到 60s；iOS 内置浏览器对服务端 PING 响应不稳定
    ws = web.WebSocketResponse(heartbeat=60, compress=False)
    await ws.prepare(request)
    peer = request.remote
    log.info("WebSocket 会话开始: %s", peer)
    close_reason = "正常关闭"

    try:
        async for raw in ws:
            if raw.type.name == "CLOSE":
                close_reason = "客户端 CLOSE"
                break
            if raw.type.name == "PING":
                continue
            if raw.type.name != "TEXT":
                continue
            try:
                text = raw.data
                # 紧凑格式 m,dx,dy / s,dy — 比 JSON 解析更快
                if text and text[0] in ("m", "s") and "," in text:
                    parts = text.split(",")
                    if parts[0] == "m" and len(parts) >= 3:
                        queue_move(float(parts[1]), float(parts[2]))
                        continue
                    if parts[0] == "s" and len(parts) >= 2:
                        queue_scroll(float(parts[1]))
                        continue

                msg = json.loads(text)
                if msg.get("type") == "ping":
                    continue
                handle_action(msg)
            except json.JSONDecodeError:
                log.warning("无效消息: %s", raw.data[:100])
            except Exception:
                log.exception("处理输入失败")
    except asyncio.CancelledError:
        close_reason = "服务端取消"
        raise
    except Exception as exc:
        close_reason = f"异常: {exc}"
        log.warning("WebSocket 异常: %s — %s", peer, exc)
    finally:
        flush_motion(force_scroll=True)
        with _input_lock:
            input_win.reset_motion_remainders()
            _release_all_hotkeys()
        code = ws.close_code if ws.close_code is not None else "-"
        log.info("WebSocket 会话结束: %s (code=%s, %s)", peer, code, close_reason)

    return ws


async def index_handler(_: web.Request) -> web.Response:
    return web.FileResponse(WEB_DIR / "index.html")


async def pad_handler(_: web.Request) -> web.Response:
    resp = web.FileResponse(WEB_DIR / "pad.html")
    resp.headers["Cache-Control"] = "no-store"
    return resp


async def qr_handler(request: web.Request) -> web.Response:
    import qrcode

    host = request.host
    url = f"http://{host}/pad"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return web.Response(body=buf.getvalue(), content_type="image/png")


async def info_handler(request: web.Request) -> web.Response:
    host = request.host
    return web.json_response(
        {
            "url": f"http://{host}/",
            "pad_url": f"http://{host}/pad",
            "ws": f"ws://{host}/ws",
            "ip": local_ip(),
        }
    )


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index_handler)
    app.router.add_get("/pad", pad_handler)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/qr.png", qr_handler)
    app.router.add_get("/api/info", info_handler)
    app.router.add_static("/static", WEB_DIR, show_index=False)
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Phone Touchpad server")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址 (默认 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8765, help="端口 (默认 8765)")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()

    start_motion_thread()

    ip = local_ip()
    pad_url = f"http://{ip}:{args.port}/pad"
    qr_url = f"http://{ip}:{args.port}/qr.png"

    print()
    print("=" * 52)
    print("  Phone Touchpad — WiFi 版 已启动")
    print("=" * 52)
    print(f"  电脑本机:  http://127.0.0.1:{args.port}/")
    print(f"  手机触控板: {pad_url}")
    print(f"  扫码连接:  {qr_url}")
    print()
    print("  请确保手机和电脑连接同一 Wi-Fi")
    print("  首次运行若连不上，请在防火墙中允许 Python")
    print("=" * 52)
    print()

    if not args.no_browser:
        webbrowser.open(f"http://127.0.0.1:{args.port}/")

    web.run_app(build_app(), host=args.host, port=args.port, print=None)


if __name__ == "__main__":
    main()
