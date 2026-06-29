# phone-touchpad

**Use your phone as a Windows touchpad via browser.**

用手机浏览器（iPhone Safari / Android Chrome）当 Windows 无线触控板。无需安装手机 App，局域网直连，数据不出本机网络。

[更新日志](CHANGELOG.md)

---

## 功能

- 单指移动光标、单击 / 双击、长按拖动
- 双指滚动、双指轻点右键
- 可调灵敏度（×1.5 ~ ×3.5）
- 键盘模式：从手机输入文字到电脑
- 扫码连接，支持添加到主屏幕当 PWA 使用

## 环境要求

- **电脑**：Windows 10 / 11，Python 3.10+
- **手机**：与电脑同一 Wi-Fi
- **浏览器**：推荐 iPhone Safari

## 快速开始

### 1. 下载项目

```bash
git clone https://github.com/shuxuanfu/phone-touchpad.git
cd phone-touchpad
```

### 2. 启动（Windows）

双击 **`start.bat`**，首次运行会自动安装依赖。

或手动启动：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### 3. 手机连接

启动后终端会显示地址，例如：

```
手机触控板: http://192.168.1.100:8765/pad
```

- iPhone Safari 打开上述地址，或
- 在电脑浏览器打开 `http://127.0.0.1:8765/` 扫描二维码

### 4. 添加到主屏幕（可选）

Safari → 分享 → **添加到主屏幕**，之后像 App 一样打开。

## 手势说明

| 操作 | 效果 |
|------|------|
| 单指滑动 | 移动光标 |
| 单击 | 左键 |
| 双击 | 双击左键 |
| 长按再拖 | 拖动选中 |
| 双指滑动 | 滚动 |
| 双指轻点 | 右键 |
| 右上角「滚动」 | 单指滚动模式 |
| 右上角「×2.2」 | 切换灵敏度 |

## 项目结构

```
phone-touchpad/
├── server.py        # HTTP + WebSocket 服务
├── input_win.py     # Windows SendInput 低延迟注入
├── start.bat        # Windows 一键启动
├── requirements.txt
├── web/
│   ├── index.html   # 电脑端连接页（含二维码）
│   └── pad.html     # 手机触控板界面
└── CHANGELOG.md
```

## 连不上？

1. 确认手机和电脑在 **同一 Wi-Fi**（不要用访客网络）
2. Windows 防火墙弹窗时选择 **允许**
3. 公司/学校网络可能有设备隔离，可试手机热点
4. 保持 Safari **前台** 使用，后台会被 iOS 限速

## 技术说明

- **通信**：WebSocket over LAN
- **输入注入**：Windows `SendInput` API
- **优化**：客户端帧合并 + 服务端 120Hz 批量刷新

## 与 Tracepad 的区别

[Tracepad](https://www.tracepad.site/) 仅支持控制 Mac。本项目面向 **Windows**，通过浏览器即可使用，无需 Mac 配套软件。

## License

GPL-3.0 — see [LICENSE](LICENSE)
