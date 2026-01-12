# Coder Screensaver

Animated code screensaver with syntax highlighting - displays source code as if being typed in real-time in a terminal, with an editor-like UI.

## Features

- 🎨 **Syntax Highlighting**: Full Pygments support with 256 colors
- 🎭 **Multiple Themes**: Choose from any Pygments style (monokai, vim, github-dark, etc.)
- 🌈 **Theme-Aware UI**: Menu and status bar colors adapt to match the selected theme
- 📝 **Editor-like UI**: Emacs-inspired menu bar and status line
- 🔄 **Auto-scrolling**: Smooth scrolling as code is typed
- 🎯 **Multi-language**: Supports Python, C/C++, Rust, Go, JavaScript, TypeScript, Java, and more
- ⚡ **Customizable Speed**: Adjust typing speed with millisecond precision
- 🎬 **Realistic Typing**: Pauses between words for natural flow

## Installation

### From PyPI (once published)

```bash
pip install coder-screensaver
```

### From Source

```bash
git clone https://github.com/sinanislekdemir/coder-screensaver.git
cd coder-screensaver
pip install -e .
```

## Usage

### Basic Usage

```bash
# Type files in current directory
coder-screensaver

# Type files in a specific directory
coder-screensaver /path/to/code

# Customize typing speed and style
coder-screensaver --delay 50 --style dracula
```
coder-screensaver /path/to/source

# Type a specific file
coder-screensaver myfile.py
```

### Advanced Options

```bash
# Faster typing (10ms delay)
coder-screensaver --delay 10

# Use different syntax theme
coder-screensaver --style vim

# Custom pause between files
coder-screensaver --pause 2.0

# Combine options
coder-screensaver ~/projects/myapp --delay 20 --style github-dark --pause 1.5
```

### Command-line Options

- `path`: Path to source directory or file (default: current directory)
- `-d, --delay`: Delay in milliseconds between characters (default: 35)
- `-s, --style`: Pygments style name (default: monokai)
- `-p, --pause`: Pause in seconds between files (default: 1.0)
- `--list-styles`: List all available Pygments styles and exit

### Available Styles

List all available Pygments themes:

```bash
coder-screensaver --list-styles
```

Some popular Pygments styles:
- `monokai` (default) - Dark theme with vibrant colors
- `vim` - Classic Vim color scheme
- `github-dark` - GitHub's dark theme
- `dracula` - Popular dark theme
- `solarized-dark` - Solarized dark variant
- `nord` - Arctic-inspired color palette

## Controls

- Press `q` to quit at any time

## Requirements

- Python 3.8+
- Terminal with 256-color support
- Unix-like system (Linux, macOS) with curses support

## How It Works

1. Scans the specified directory for source files
2. Uses Pygments to syntax highlight the code with your chosen theme
3. Displays the code character-by-character with realistic typing animation
4. Automatically scrolls and manages the display using curses
5. Loops through files continuously

## Examples

### Demo Recording

Watch code being typed in real-time with syntax highlighting in your terminal!

### Screenshot

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Edit  Options  Buffers  Tools  Lisp-Interaction  Help    │
├─────────────────────────────────────────────────────────────────┤
│ #include <iostream>                                             │
│ using namespace std;                                            │
│                                                                 │
│ int main() {                                                    │
│     string name = "world";                                      │
│     cout << "Hello " << name << endl;█                          │
│     return 0;                                                   │
│ }                                                               │
├─────────────────────────────────────────────────────────────────┤
│ -UUU:----F1  example.cpp   (C++)                               │
└─────────────────────────────────────────────────────────────────┘
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request at https://github.com/sinanislekdemir/coder-screensaver

## Author

Created by Sinan Islekdemir
