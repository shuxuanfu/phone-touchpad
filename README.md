# phone-touchpad

**Use your phone as a Windows touchpad via browser.**

用手机当 Windows 无线触控板。按连接方式分版本维护，当前提供 **WiFi 版**。

| 版本 | 连接方式 | 状态 | 说明 |
|------|----------|------|------|
| [WiFi](wifi/) | 局域网 Wi-Fi + 浏览器 | ✅ 可用 | 无需安装手机 App，扫码即用 |
| Bluetooth | 蓝牙 HID | 🚧 计划中 | — |
| USB | 有线连接 | 🚧 计划中 | — |

[更新日志](CHANGELOG.md)

---

## 快速开始（WiFi 版）

```bash
git clone https://github.com/shuxuanfu/phone-touchpad.git
cd phone-touchpad
start.bat
```

手机 Safari 打开终端显示的 `/pad` 地址，或扫描电脑连接页二维码。

详细说明见 **[wifi/README.md](wifi/README.md)**。

## 项目结构

```
phone-touchpad/
├── start.bat              # 启动 WiFi 版（入口）
├── wifi/                  # WiFi 版实现
│   ├── start.bat
│   ├── requirements.txt
│   ├── server/
│   │   ├── main.py
│   │   └── input_win.py
│   └── client/
│       └── web/
│           ├── index.html
│           └── pad.html
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## 功能（WiFi 版）

- 单指移动、单击/双击、长按拖动
- 双指滚动、双指轻点右键
- 可调灵敏度、键盘输入
- 局域网直连，无云端

## License

GPL-3.0 — see [LICENSE](LICENSE)
