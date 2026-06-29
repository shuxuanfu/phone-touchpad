# Changelog

## [0.4.1] — 2026-06-29 — 滚动灵敏度（WiFi 版）

### 功能
- 新增 **滚速** 按钮，独立调节上下滚动灵敏度（×0.15 ~ ×1.0）
- 默认滚速从 ×0.9 降至 **×0.35**，解决滚动过快问题
- 设置保存在 `localStorage`，刷新后保留

---

## [0.4.0] — 2026-06-29 — 流畅度优化（WiFi 版）

参考 [RemotePC](https://github.com/Stan006/RemotePC) 多通道低延迟思路与浏览器 [getCoalescedEvents](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/getCoalescedEvents) API。

### 性能
- 移动/滚动改用 **二进制 WebSocket**（9/5 字节），减少解析开销
- 服务端刷新率 **120Hz → 240Hz**
- Windows 端 **子像素累积**，减少取整带来的跳跃感
- 手机端使用 **Pointer Events + getCoalescedEvents** 捕获合并前的触摸采样（iOS 18.2+ Safari）
- 启用 **Screen Wake Lock**，降低 iOS 后台限速概率
- 保留文本协议兼容旧页面

### 说明
- 浏览器无法直接发 UDP；局域网 WebSocket 延迟已接近网络下限
- 后续可考虑 WebRTC DataChannel（UDP 语义）进一步压低延迟

---

## [0.3.1] — 2026-06-29 — 滚动方向修正（WiFi 版）

### 修复
- 双指滚动方向改为与触控板自然滚动一致：手指上滑 → 页面向上，手指下滑 → 页面向下
- 修复 `wifi/start.bat` 中文编码导致 cmd 解析失败的问题
- 优化虚拟环境选择：优先使用根目录 `.venv`，并固定用 venv 的 `python.exe` 启动

---

## [0.3.0] — 2026-06-29 — 目录重构（WiFi 版）

### 结构
- 按连接方式拆分目录，当前实现归入 `wifi/`
- 服务端移至 `wifi/server/`（`main.py`、`input_win.py`）
- 前端移至 `wifi/client/web/`
- 根目录 `start.bat` 作为统一入口，转发至 `wifi/start.bat`
- 新增 `wifi/README.md`，根 README 改为版本索引

---

## [0.2.0] — 2026-06-29 — 低延迟优化（WiFi 版）

### 性能
- 手机端使用 `requestAnimationFrame` 合并每帧移动/滚动，减少 WebSocket 消息量
- 采用紧凑协议 `m,dx,dy` / `s,dy`，降低 JSON 解析开销
- Windows 端改用 `SendInput`（`input_win.py`）注入鼠标，替代 pynput 移动路径
- 服务端 120Hz 刷新线程合并位移后批量注入
- 关闭 WebSocket 压缩（`compress=False`），减少局域网延迟
- 触控板页面禁用缓存（`Cache-Control: no-store`）

### 功能
- 新增灵敏度切换（×1.5 / ×2.0 / ×2.2 / ×2.8 / ×3.5），设置保存在 `localStorage`
- 电脑端连接页与手机触控板页分离（`/` 与 `/pad`）
- 手机访问 `/` 自动跳转到 `/pad`

### 修复
- 修复 `_pending_scroll` 未声明 `global` 导致刷新线程崩溃的问题

---

## [0.1.0] — 2026-06-29 — 初始版本（WiFi 版）

### 功能
- Python 服务端 + 浏览器触控板，无需安装 iOS App
- WebSocket 实时通信，局域网直连，无云端
- 单指移动、单击/双击、长按拖动
- 双指滚动、双指轻点右键
- 虚拟键盘输入文字到电脑
- 一键启动脚本 `start.bat`（自动创建虚拟环境并安装依赖）
- 连接页二维码扫码配对
