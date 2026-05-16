# Regex Tool

```
╔══════════════════════════════════════╗
║       REGEX TOOL — Linux GUI         ║
║  Tester · Reference · File Search    ║
╚══════════════════════════════════════╝
```

A desktop GUI tool for Linux built with Python and tkinter.  
Test regular expressions in real time, browse an interactive reference cheatsheet, and search files on your system using regex patterns.

---

## Table of Contents

- [How it works](#how-it-works)
- [Installation](#installation)
- [Tabs and features](#tabs-and-features)
- [Regex quick reference](#regex-quick-reference)
- [Requirements](#requirements)
- [Uninstallation](#uninstallation)

---

## How it works

**Regex Tool** has three integrated tabs:

| Tab | What it does |
|-----|-------------|
| 🔬 Tester | Type a pattern and test text — matches are highlighted in real time with captured groups shown |
| 📖 Reference | Full cheatsheet of metacharacters, quantifiers, anchors, and groups. Click any item to load it into the Tester |
| 🗂 File Search | Filter files by name (regex) and/or file content, recursively across directories |

Everything runs locally. No data leaves your machine.

---

## Installation

**Via script (recommended):**

```bash
git clone https://github.com/BabuinoDoNorte/RegexTool.git
cd RegexTool
chmod +x install.sh
./install.sh
```

> After install, the `regextool` command is available system-wide.

**One-liner:**

```bash
curl -fsSL https://raw.githubusercontent.com/BabuinoDoNorte/RegexTool/main/install.sh | bash
```

---

## Tabs and features

### 🔬 Tester

- Regex input field with immediate visual error feedback
- Toggleable flags: `i` (ignore case), `m` (multiline), `s` (dotall)
- Matches highlighted in two alternating colors in the test text
- Table showing: match number, matched text, start/end position, captured groups

### 📖 Reference

- Sections: Special characters · Quantifiers · Anchors · Character classes · Groups · Escape
- Each entry shows the symbol, description, and usage example
- **Click any row** → loads the pattern directly into the Tester

### 🗂 File Search

- Choose directory via `…` button or by typing the path
- **Name pattern**: filter files by filename using regex (e.g. `[Ff]ile\d+`)
- **Content pattern**: search for a regex pattern inside file contents
- Options: recursive · include hidden files · case-insensitive
- Search runs in a separate thread — UI stays responsive
- Double-click a result to open its location in the file manager

---

## Regex quick reference

| Pattern | Meaning | Example |
|---------|---------|---------|
| `.` | Any character (except `\n`) | `a.c` → `abc`, `a1c` |
| `\d` | Digit [0-9] | `\d{3}` → `123` |
| `\w` | Alphanumeric + `_` | `\w+` → `hello_world` |
| `\s` | Whitespace | `kali\s+tools` |
| `*` | 0 or more | `cats*` → `cat`, `catsss` |
| `+` | 1 or more | `br+` → `br`, `brrrrr` |
| `?` | Optional (0 or 1) | `colou?r` → `color`, `colour` |
| `{n,m}` | Between n and m times | `\d{2,4}` → `12`, `1234` |
| `^` | Start of line | `^username:` |
| `$` | End of line | `EOF$` |
| `[abc]` | a, b, or c | `[cfh]at` → `cat`, `fat` |
| `[^abc]` | Negation | `[^0-9]` → non-digit |
| `(a\|b)` | a or b | `nano\|vim` |
| `(\w+)` | Capture group | `(\w+)@(\w+)\.com` |

---

## Requirements

- Ubuntu 20.04+ (or any distro with Python 3.8+)
- Python 3.8+
- `python3-tk` (installed automatically by `install.sh` if missing)

No external dependencies — Python standard library only.

---

## Uninstallation

```bash
./uninstall.sh
```

Or manually:

```bash
sudo rm /usr/local/bin/regextool
```

---

## License

MIT — free to use, modify, and distribute.
