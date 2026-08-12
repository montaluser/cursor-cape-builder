# Cursor Cape Builder

[English](README_en.md)

把标准的 15 张指针 PNG 动画帧图自动封装成完整的 Mousecape `.cape` 主题。

将指针 ZIP 或图片文件夹拖到 App 图标上，就会在原文件旁生成 `.cape`，并自动关闭 App。

## 功能

- 自动填充 44 个 macOS 指针状态；
- 完整嵌入动画帧，不依赖外部图片；
- 自动处理主箭头、文本、链接、移动、等待、帮助和各方向缩放等常用别名状态；
- 默认动画总时长为 0.8 秒，按图片实际帧数自动计算每帧时长。

## 使用

**[前往 Releases 下载 Cursor Cape Builder.app](https://github.com/montaluser/cursor-cape-builder/releases)**

1. 在 Releases 页面下载 `Cursor Cape Builder.app`。
2. 首次使用时，对 App 右键 →“打开”。
3. 将一个指针 ZIP 或图片文件夹拖到 App 图标；也可双击 App 后选择文件。
4. 在原文件旁找到生成的 `（自动生成）.cape`，双击导入 Mousecape。

若 macOS 在首次打开时拦截，请对 App 右键 →“打开”，或前往“隐私与安全性”选择“仍要打开”。

## 输入图片要求

指针包必须包含以下 15 张固定名称的 PNG 帧图。每张图都是由正方形帧自上而下拼成的动画序列，例如 `32×256` 代表 8 帧 `32×32` 图像。

| | | |
|---|---|---|
| `Alternate.png` | `Busy.png` | `Diagonal1.png` |
| `Diagonal2.png` | `Handwriting.png` | `Help.png` |
| `Horizontal.png` | `Link.png` | `Move.png` |
| `Normal.png` | `Precision.png` | `Text.png` |
| `Unavailable.png` | `Vertical.png` | `Working.png` |

## 从源码构建

需要 macOS 15+、Xcode Command Line Tools，以及带 Pillow 的 Python 3。

```bash
python3 -m pip install -r requirements.txt
zsh scripts/build-app.sh
```

生成的 App 位于 `dist/Cursor Cape Builder.app`。

如需打包成可上传到 GitHub Releases 的压缩包：

```bash
zsh scripts/package-release.sh
```

压缩包位于 `release/Cursor-Cape-Builder-macOS.zip`。

## 命令行用法

```bash
python3 src/CursorCapeBuilder.py /path/to/cursor-pack.zip /path/to/theme.cape \
  --name "My Cursor Theme" --author "Your Name"
```

## 许可证

MIT。项目不包含任何指针美术资源；美术资源的版权和许可归其原作者所有。
