# phone-touchpad — WiFi 版

通过 **局域网 Wi-Fi + 浏览器** 将手机变成 Windows 触控板。

- 通信：WebSocket over LAN（默认端口 `8765`）
- 客户端：手机浏览器（推荐 iPhone Safari），无需安装 App
- 服务端：Windows Python 服务

[返回项目主页](../README.md) · [更新日志](../CHANGELOG.md)

---

## 快速开始

```bash
# 在项目根目录
start.bat

# 或进入 wifi 目录
cd wifi
start.bat
```

手动启动：

```bash
cd wifi
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server/main.py
```

## 连接

启动后访问终端显示的地址，例如 `http://192.168.1.100:8765/pad`。

电脑端打开 `http://127.0.0.1:8765/` 可查看二维码。

## 目录说明

```
wifi/
├── start.bat              # WiFi 版启动脚本
├── requirements.txt       # Python 依赖
├── server/
│   ├── main.py            # HTTP + WebSocket 服务入口
│   └── input_win.py       # Windows SendInput 注入
└── client/
    └── web/
        ├── index.html     # 电脑连接页
        └── pad.html       # 手机触控板页
```

## 环境要求

- Windows 10 / 11，Python 3.10+
- 手机与电脑同一 Wi-Fi

## 手势

| 操作 | 效果 |
|------|------|
| 单指滑动 | 移动光标 |
| 单击 / 双击 | 左键 / 双击 |
| 长按拖动 | 拖选 |
| 双指滑动 | 滚动 |
| 双指轻点 | 右键 |
