#!/usr/bin/env python3

import time
import random
import curses
import re
import argparse
from pathlib import Path

from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import Terminal256Formatter


SOURCE_PATH = Path(".")
DELAY_MS = 35
PAUSE_BETWEEN_FILES = 1.0
STYLE_NAME = "monokai"

EXTENSIONS = {
    ".py",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".rs",
    ".go",
    ".js",
    ".ts",
    ".java",
}

COLOR_FRAME = 1
COLOR_NORMAL = 2
COLOR_FRAME_FG = curses.COLOR_WHITE
COLOR_FRAME_BG = curses.COLOR_BLUE

running = True
current_file = ""
ansi_color_map = {}


def get_theme_colors():
    from pygments.styles import get_style_by_name
    from pygments.token import Keyword

    try:
        style = get_style_by_name(STYLE_NAME)
        keyword_style = style.style_for_token(Keyword)
        fg_hex = keyword_style.get("color", None)
        bg_hex = style.background_color

        fg_color = hex_to_ansi256(fg_hex) if fg_hex else 15
        bg_color = hex_to_ansi256(bg_hex) if bg_hex else 0

        return fg_color, bg_color
    except (ValueError, AttributeError):
        return 15, 4


def hex_to_ansi256(hex_color):
    if not hex_color or hex_color.startswith("#"):
        hex_color = hex_color[1:] if hex_color else "ffffff"

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r_idx = round(r * 5 / 255)
        g_idx = round(g * 5 / 255)
        b_idx = round(b * 5 / 255)

        return 16 + (36 * r_idx) + (6 * g_idx) + b_idx
    except (ValueError, TypeError):
        return 15


def parse_ansi_code(code):
    if code < curses.COLORS:
        return code
    return curses.COLOR_WHITE


def strip_ansi_and_parse(text):
    global ansi_color_map

    ansi_pattern = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

    result = []
    current_color = curses.color_pair(COLOR_NORMAL)
    pos = 0

    for match in ansi_pattern.finditer(text):
        result.extend([(ch, current_color) for ch in text[pos : match.start()]])

        color_match = re.match(r"\x1b\[([0-9;]+)m", match.group())
        if color_match:
            codes = color_match.group(1).split(";")

            if len(codes) >= 3 and codes[0] == "38" and codes[1] == "5":
                try:
                    color_code = int(codes[2])
                    cache_key = f"256_{color_code}"
                    if cache_key not in ansi_color_map:
                        pair_num = len(ansi_color_map) + 10
                        if pair_num < 64:
                            curses_color = parse_ansi_code(color_code)
                            curses.init_pair(pair_num, curses_color, curses.COLOR_BLACK)
                            ansi_color_map[cache_key] = pair_num

                    if cache_key in ansi_color_map:
                        current_color = curses.color_pair(ansi_color_map[cache_key])
                except (ValueError, KeyError):
                    pass

        pos = match.end()

    result.extend([(ch, current_color) for ch in text[pos:]])

    return result


def load_source_files():
    files = [
        p for p in SOURCE_PATH.rglob("*") if p.is_file() and p.suffix in EXTENSIONS
    ]
    random.shuffle(files)
    return files


def type_file(stdscr, path: Path):
    global current_file, running

    current_file = str(path)

    try:
        code = path.read_text(errors="ignore")
        lexer = guess_lexer_for_filename(path.name, code)
    except Exception:
        return

    formatter = Terminal256Formatter(style=STYLE_NAME)
    highlighted = highlight(code, lexer, formatter)
    parsed = strip_ansi_and_parse(highlighted)

    lines = [[]]
    current_line = 0
    current_col = 0
    chars_since_refresh = 0

    for ch, color in parsed:
        if not running:
            return

        if ch == "\n":
            lines.append([])
            current_line += 1
            current_col = 0
        else:
            lines[current_line].append((ch, color))
            current_col += 1

        chars_since_refresh += 1

        height, width = stdscr.getmaxyx()
        content_height = height - 2

        lines_typed = current_line + 1
        scroll_offset = max(0, lines_typed - content_height)

        if chars_since_refresh >= 100:
            stdscr.clear()
            chars_since_refresh = 0

        render_screen(
            stdscr, lines[:lines_typed], current_line, current_col, scroll_offset
        )

        if ch == " ":
            time.sleep((DELAY_MS / 1000) * random.uniform(0.7, 1.3) * 3)
        else:
            time.sleep((DELAY_MS / 1000) * random.uniform(0.7, 1.3))

    height, width = stdscr.getmaxyx()
    content_height = height - 2
    lines_typed = len(lines)
    scroll_offset = max(0, lines_typed - content_height)
    render_screen(stdscr, lines, current_line, current_col, scroll_offset)
    time.sleep(PAUSE_BETWEEN_FILES)


def render_screen(stdscr, lines, cursor_line, cursor_col, scroll_offset):
    try:
        height, width = stdscr.getmaxyx()
    except curses.error:
        return

    content_height = height - 2
    total_lines = len(lines)

    if scroll_offset > 0:
        if cursor_line >= scroll_offset + content_height:
            scroll_offset = cursor_line - content_height + 1
        elif cursor_line < scroll_offset:
            scroll_offset = cursor_line

        max_scroll = max(0, total_lines - content_height)
        scroll_offset = min(scroll_offset, max_scroll)

    stdscr.erase()

    menu_text = (
        " File  Edit  Options  Buffers  Tools  Lisp-Interaction  Projectile  Help"
    )
    try:
        stdscr.attron(curses.color_pair(COLOR_FRAME))
        stdscr.addstr(0, 0, menu_text[:width].ljust(width))
        stdscr.attroff(curses.color_pair(COLOR_FRAME))
    except curses.error:
        pass

    for i in range(content_height):
        line_idx = scroll_offset + i
        if line_idx >= len(lines):
            break

        y = i + 1
        x = 0

        for j in range(min(len(lines[line_idx]), width)):
            ch, color = lines[line_idx][j]
            try:
                stdscr.addstr(y, x, ch, color)
                x += 1
            except curses.error:
                pass

        if line_idx == cursor_line and x < width:
            try:
                stdscr.addstr(y, x, "█", curses.color_pair(COLOR_FRAME))
            except curses.error:
                pass

    status_y = height - 1
    filename = Path(current_file).name if current_file else "untitled"

    if filename.endswith((".cpp", ".hpp", ".c", ".h")):
        mode = "C++"
    elif filename.endswith(".py"):
        mode = "Python"
    else:
        mode = "Text"

    status_text = f"-UUU:----F1  {filename}   ({mode})"

    try:
        stdscr.attron(curses.color_pair(COLOR_FRAME))
        stdscr.addstr(status_y, 0, status_text[: width - 1].ljust(width - 1))
        stdscr.attroff(curses.color_pair(COLOR_FRAME))
    except curses.error:
        pass

    stdscr.noutrefresh()
    curses.doupdate()


def typer_loop(stdscr):
    global running
    files = load_source_files()
    if not files:
        return

    while running:
        for f in files:
            if not running:
                return
            type_file(stdscr, f)


def main(stdscr):
    global running, COLOR_FRAME_FG, COLOR_FRAME_BG

    curses.start_color()

    COLOR_FRAME_FG, COLOR_FRAME_BG = get_theme_colors()

    curses.init_pair(COLOR_FRAME, COLOR_FRAME_FG, COLOR_FRAME_BG)
    curses.init_pair(COLOR_NORMAL, curses.COLOR_WHITE, curses.COLOR_BLACK)

    stdscr.bkgd(" ", curses.color_pair(COLOR_NORMAL))
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.resizeterm(curses.LINES, curses.COLS)

    import threading

    thread = threading.Thread(target=typer_loop, args=(stdscr,), daemon=True)
    thread.start()

    while running:
        try:
            key = stdscr.getch()
            if key == ord("q"):
                running = False
                break
            elif key == curses.KEY_RESIZE:
                stdscr.clear()
                stdscr.refresh()
        except curses.error:
            pass
        time.sleep(0.1)


def main_wrapper():
    parser = argparse.ArgumentParser(
        description="Animated code typer with syntax highlighting",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Path to source directory or file"
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=35,
        help="Delay in milliseconds between characters",
    )
    parser.add_argument("-s", "--style", default="monokai", help="Pygments style name")
    parser.add_argument(
        "-p", "--pause", type=float, default=1.0, help="Pause in seconds between files"
    )
    parser.add_argument(
        "--list-styles", action="store_true", help="List all available Pygments styles"
    )

    args = parser.parse_args()

    if args.list_styles:
        from pygments.styles import get_all_styles

        print("Available Pygments styles:")
        print()
        styles = sorted(get_all_styles())
        for style in styles:
            marker = " (default)" if style == "monokai" else ""
            print(f"  • {style}{marker}")
        print()
        print(f"Total: {len(styles)} styles")
        print()
        print("Use with: coder-screensaver --style STYLE_NAME")
        return 0

    global SOURCE_PATH, DELAY_MS, STYLE_NAME, PAUSE_BETWEEN_FILES
    SOURCE_PATH = Path(args.path)
    DELAY_MS = args.delay
    STYLE_NAME = args.style
    PAUSE_BETWEEN_FILES = args.pause

    if not SOURCE_PATH.exists():
        print(f"Error: Path '{SOURCE_PATH}' does not exist")
        return 1

    curses.wrapper(main)
    return 0


if __name__ == "__main__":
    exit(main_wrapper())
