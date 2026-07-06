"""Windows desktop automation for ChatGPT prompt generation and Doubao image downloads.

The script intentionally uses UI automation instead of undocumented service APIs.
It expects both ChatGPT in a browser and the Doubao desktop client to already be
logged in and visible on the Windows desktop.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import pyautogui
import pygetwindow as gw
import pyperclip

CONFIG_PATH = Path(__file__).with_name("config.json")
EXAMPLE_CONFIG_PATH = Path(__file__).with_name("config.example.json")

CALIBRATION_POINTS = [
    ("chatgpt_prompt_box", "ChatGPT 网页输入框中心位置"),
    ("doubao_prompt_box", "豆包输入框中心位置"),
    ("doubao_generate_button", "豆包生成按钮位置"),
    ("doubao_image_hover_point", "豆包图片区域/下载按钮出现前需要悬停的位置"),
    ("doubao_download_button", "豆包下载按钮位置"),
]

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.35


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"缺少配置文件：{CONFIG_PATH}\n"
            f"请先复制 {EXAMPLE_CONFIG_PATH.name} 为 config.json 并按你的电脑界面修改。"
        )
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def show_mouse_position() -> None:
    print("移动鼠标到目标位置。按 Ctrl+C 结束。")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"x={x}, y={y}", end="\r", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已结束坐标显示。")


def calibrate_config() -> None:
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    else:
        config = json.loads(EXAMPLE_CONFIG_PATH.read_text(encoding="utf-8"))

    print("准备记录坐标。每一步都把鼠标放到提示的位置，然后回到这个窗口按 Enter。")
    print("如果想取消，请按 Ctrl+C。")

    for key, label in CALIBRATION_POINTS:
        input(f"\n请把鼠标放到：{label}，然后按 Enter 记录坐标...")
        x, y = pyautogui.position()
        config[key] = [x, y]
        print(f"已记录 {key}: [{x}, {y}]")

    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n已保存到 {CONFIG_PATH}。你可以运行：")
    print(".venv\\Scripts\\python.exe doubao_chatgpt_auto.py")


def activate_window(keyword: str) -> None:
    windows = [w for w in gw.getWindowsWithTitle(keyword) if w.title and not w.isMinimized]
    if not windows:
        raise RuntimeError(f"找不到包含标题关键词的窗口：{keyword}")
    window = windows[0]
    window.activate()
    time.sleep(1)


def click_point(point: list[int] | tuple[int, int], clicks: int = 1) -> None:
    pyautogui.click(point[0], point[1], clicks=clicks)


def paste_text(text: str) -> None:
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")


def ask_chatgpt(config: dict[str, Any]) -> str:
    activate_window(config["chatgpt_window_keyword"])
    click_point(config["chatgpt_prompt_box"])
    paste_text(config["prompt_request"])
    pyautogui.press("enter")
    time.sleep(int(config.get("chatgpt_wait_seconds", 70)))
    return copy_chatgpt_answer(config)


def copy_chatgpt_answer(config: dict[str, Any]) -> str:
    strategy = config.get("copy_strategy", "select_all_page")
    activate_window(config["chatgpt_window_keyword"])

    if strategy == "select_all_page":
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "c")
    else:
        raise ValueError(f"不支持的 copy_strategy：{strategy}")

    time.sleep(0.5)
    text = pyperclip.paste()
    if not text.strip():
        raise RuntimeError("没有从 ChatGPT 页面复制到任何内容。")
    return text


def parse_prompts(text: str, count: int) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*•\s]+", "", line)
        line = re.sub(r"^\d+[).、：:\s]+", "", line).strip()
        if len(line) < 12:
            continue
        if any(skip in line.lower() for skip in ["chatgpt", "send message", "请为豆包"]):
            continue
        lines.append(line)

    unique: list[str] = []
    for line in lines:
        if line not in unique:
            unique.append(line)
        if len(unique) == count:
            break

    if len(unique) < count:
        raise RuntimeError(f"只解析到 {len(unique)} 条提示词，少于目标数量 {count}。请调大等待时间或优化提示词格式。")
    return unique


def generate_in_doubao(prompt: str, config: dict[str, Any], index: int) -> None:
    activate_window(config["doubao_window_keyword"])
    click_point(config["doubao_prompt_box"])
    pyautogui.hotkey("ctrl", "a")
    paste_text(prompt)
    click_point(config["doubao_generate_button"])

    wait_seconds = int(config.get("doubao_generation_wait_seconds", 90))
    print(f"[{index}] 等待豆包生成：{wait_seconds} 秒")
    time.sleep(wait_seconds)

    download_targets = config.get("doubao_download_targets") or []
    if download_targets:
        for target in download_targets:
            hover_point = target.get("hover")
            download_button = target.get("download")
            if hover_point:
                pyautogui.moveTo(hover_point[0], hover_point[1])
                time.sleep(0.8)
            if download_button:
                click_point(download_button)
                time.sleep(int(config.get("after_download_wait_seconds", 5)))
        return

    hover_point = config.get("doubao_image_hover_point")
    if hover_point:
        pyautogui.moveTo(hover_point[0], hover_point[1])
        time.sleep(0.8)

    click_point(config["doubao_download_button"])
    time.sleep(int(config.get("after_download_wait_seconds", 5)))


def run() -> None:
    config = load_config()
    count = int(config.get("count", 10))

    print("正在请求 ChatGPT 生成提示词……")
    answer = ask_chatgpt(config)
    prompts = parse_prompts(answer, count)

    print("解析到以下提示词：")
    for i, prompt in enumerate(prompts, start=1):
        print(f"{i}. {prompt}")

    for i, prompt in enumerate(prompts, start=1):
        print(f"开始处理第 {i}/{count} 条提示词……")
        generate_in_doubao(prompt, config, i)

    print("全部完成。")


def main() -> int:
    parser = argparse.ArgumentParser(description="ChatGPT 到豆包客户端图片生成下载自动化")
    parser.add_argument("--position", action="store_true", help="持续显示鼠标坐标，用于校准 config.json")
    parser.add_argument("--calibrate-config", action="store_true", help="按提示逐项记录鼠标坐标并写入 config.json")
    args = parser.parse_args()

    if args.position:
        show_mouse_position()
        return 0

    if args.calibrate_config:
        calibrate_config()
        return 0

    try:
        run()
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should show a friendly Chinese error.
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
