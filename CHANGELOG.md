# Changelog

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
