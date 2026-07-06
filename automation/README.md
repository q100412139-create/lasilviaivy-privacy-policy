# ChatGPT → 豆包客户端全自动图片生成下载

这是一个 Windows 桌面自动化方案，用于把网页 ChatGPT 生成的 10 条图片提示词自动复制到已登录的豆包客户端，再逐条生成并下载图片。

> 重要：桌面自动化会模拟键盘、鼠标、剪贴板和窗口切换。第一次运行前请先用 `config.example.json` 复制出自己的 `config.json`，并按你的屏幕、浏览器、豆包客户端界面校准坐标或按钮截图。


## 这个文件夹在哪里？

如果你是在 GitHub 页面看到这个项目，请按下面方式找到 `automation` 文件夹：

1. 打开仓库页面。
2. 点击文件列表里的 `automation` 文件夹。
3. 点击 `Code` → `Download ZIP`，把整个项目下载到 Windows 电脑。
4. 解压 ZIP，例如解压到 `C:\Users\你的用户名\Desktop\lasilviaivy-privacy-policy`。
5. 打开解压后的文件夹，再进入里面的 `automation` 文件夹。

如果你已经在 Windows 上克隆了仓库，`automation` 文件夹就在仓库根目录下面，例如：

```text
C:\Users\你的用户名\Desktop\lasilviaivy-privacy-policy\automation
```

如果你是在当前开发环境里查看，仓库路径是：

```text
/workspace/lasilviaivy-privacy-policy/automation
```

> 注意：脚本要在你的 Windows 电脑上运行，因为它需要操作你电脑上的浏览器和豆包客户端。当前开发环境里的 `/workspace/...` 路径只是代码所在位置，不能直接控制你本机的豆包客户端。

## 最简单操作流程

1. 把项目下载或克隆到 Windows 电脑。
2. 进入 `automation` 文件夹。
3. 在文件夹空白处按住 `Shift`，点击鼠标右键，选择“在终端中打开”或“在 PowerShell 中打开”。
4. 运行安装命令：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

5. 复制配置文件：

```bash
copy config.example.json config.json
```

6. 校准坐标：

```bash
python doubao_chatgpt_auto.py --position
```

7. 把鼠标移到 ChatGPT 输入框、豆包输入框、豆包生成按钮、豆包下载按钮，记下坐标，填进 `config.json`。
8. 打开并登录 ChatGPT 网页，打开并登录豆包客户端。
9. 正式运行：

```bash
python doubao_chatgpt_auto.py
```

## 文件说明

- `doubao_chatgpt_auto.py`：主自动化脚本。
- `config.example.json`：示例配置文件，请复制为 `config.json` 后修改。
- `screenshots/`：可选，放置按钮截图，例如豆包生成按钮、下载按钮、ChatGPT 复制按钮。
- `downloads/`：建议把豆包下载目录设置到这里，方便统一管理。

## 安装

在 Windows 的 PowerShell 或 CMD 中运行：

```bash
cd automation
python -m venv .venv
.venv\Scripts\activate
pip install pyautogui pyperclip pygetwindow pillow
```

## 使用步骤

1. 打开浏览器并登录 ChatGPT 网页。
2. 打开并登录豆包客户端，进入图片生成页面或可直接生成图片的聊天页面。
3. 把 `config.example.json` 复制为 `config.json`。
4. 修改 `config.json`：
   - `chatgpt_window_keyword`：浏览器窗口标题里能识别 ChatGPT 的关键词。
   - `doubao_window_keyword`：豆包客户端窗口标题关键词。
   - `chatgpt_prompt_box`：ChatGPT 输入框坐标。
   - `doubao_prompt_box`：豆包输入框坐标。
   - `doubao_generate_button`：豆包生成按钮坐标。
   - `doubao_download_button`：豆包下载按钮坐标。
5. 运行：

```bash
python doubao_chatgpt_auto.py
```

脚本会先让 ChatGPT 生成 10 条提示词，然后复制回答，解析出 10 条提示词，再切换到豆包逐条生成并下载。

## 坐标校准

如果你不知道按钮坐标，可以运行：

```bash
python doubao_chatgpt_auto.py --position
```

把鼠标移动到目标按钮上，终端会持续显示当前坐标。把坐标填入 `config.json` 即可。

## 推荐运行前准备

- 保持 ChatGPT 和豆包窗口不要最小化。
- 不要在自动化运行时移动鼠标或使用键盘。
- 关闭可能遮挡界面的弹窗。
- 将豆包默认下载路径设为 `automation/downloads` 或你自己的固定目录。

## 常见问题

### 为什么需要配置坐标？

豆包客户端不是网页 API，桌面自动化无法稳定读取内部控件，只能通过坐标、快捷键、截图识别等方式操作。

### ChatGPT 输出没复制完整怎么办？

可以调大 `chatgpt_wait_seconds`，或把 `copy_strategy` 改为 `select_all_chat` 并根据你的网页布局调整。

### 豆包下载点不到怎么办？

先确认生成完成后下载按钮是否固定在同一位置。如果下载按钮需要鼠标悬停显示，请把 `doubao_image_hover_point` 设置为图片区域坐标。
