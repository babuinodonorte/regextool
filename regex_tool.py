#!/usr/bin/env python3
"""
Regex Tool — Smart regex builder with natural language input
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
import threading
from pathlib import Path
import tkinter.font


# ── Colors ────────────────────────────────────────────────────────────────────
BG       = "#1a1a2e"
BG2      = "#16213e"
BG3      = "#0f3460"
ACCENT   = "#e94560"
ACCENT2  = "#53d8fb"
TEXT     = "#e8e8e8"
DIM      = "#8888aa"
SUCCESS  = "#4ade80"
MONO     = ("Courier New", 11)
UI       = ("Segoe UI", 10)


# ── Natural language → regex rules ───────────────────────────────────────────
# Each rule: (trigger_words, regex_fragment, description)
NL_RULES = [
    # case
    (["ignore case", "case insensitive", "uppercase", "lowercase", "any case"],
     None, "flag:i"),

    # repetition
    (["repeating", "repeated", "one or more"],        "+",    "one or more"),
    (["zero or more", "any amount"],                   "*",    "zero or more"),
    (["optional", "maybe"],                            "?",    "optional"),

    # anchors
    (["starts with", "beginning", "start of line"],    "^",    "start of line"),
    (["ends with", "end of line", "ending"],           "$",    "end of line"),

    # digits
    (["digit", "number", "numeric"],                   r"\d",  "digit"),
    (["not a digit", "non-digit"],                     r"\D",  "non-digit"),

    # whitespace
    (["space", "whitespace", "tab"],                   r"\s",  "whitespace"),
    (["non-space", "no space"],                        r"\S",  "non-whitespace"),

    # word chars
    (["word character", "alphanumeric", "letter or number"], r"\w", "word char"),
    (["non-word", "symbol", "special character"],      r"\W",  "non-word char"),

    # word boundary
    (["whole word", "exact word", "word boundary"],    r"\b",  "word boundary"),

    # any char
    (["any character", "any char", "wildcard"],        ".",    "any character"),
]


def parse_natural_language(text: str, word: str) -> tuple[str, list[str]]:
    """
    Builds a regex from a base word + natural language modifiers.
    Returns (pattern, explanation_lines).
    """
    text_lower = text.lower()
    flags_set = set()
    mods_before = []
    mods_after = []
    explanations = []
    use_flag_i = False

    for triggers, fragment, desc in NL_RULES:
        if any(t in text_lower for t in triggers):
            if desc == "flag:i":
                use_flag_i = True
                explanations.append("• case-insensitive match")
            elif fragment in ("^", r"\b"):
                mods_before.append(fragment)
                explanations.append(f"• {desc}: {fragment}")
            elif fragment in ("$",):
                mods_after.append(fragment)
                explanations.append(f"• {desc}: {fragment}")
            elif fragment in ("+", "*", "?"):
                # apply to last char of word
                mods_after.append(fragment)
                explanations.append(f"• {desc}: last character repeats ({fragment})")
            else:
                mods_after.append(fragment)
                explanations.append(f"• {desc}: {fragment}")

    # Check for "ends with s / plural"
    plural = any(t in text_lower for t in ["plural", "ends with s", "with s", "optional s"])
    if plural and word:
        word = word.rstrip("s") + "s?"
        explanations.append("• optional trailing 's'")

    # Build pattern
    escaped = re.escape(word) if word else ""
    pattern = "".join(mods_before) + escaped + "".join(mods_after)

    if use_flag_i:
        # wrap in (?i) inline flag
        pattern = "(?i)" + pattern

    if not pattern:
        pattern = escaped

    return pattern, explanations


# ══════════════════════════════════════════════════════════════════════════════
class RegexTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Regex Tool")
        self.geometry("960x700")
        self.minsize(760, 500)
        self.configure(bg=BG)
        self._mode = tk.IntVar(value=1)  # 1=view, 2=edit, 3=stop
        self._setup_styles()
        self._build_ui()

    # ── Styles ────────────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook",     background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG2, foreground=DIM,
                    padding=[16, 8], font=UI)
        s.map("TNotebook.Tab",
              background=[("selected", BG3)],
              foreground=[("selected", ACCENT2)])
        s.configure("TFrame",    background=BG)
        s.configure("TLabel",    background=BG, foreground=TEXT, font=UI)
        s.configure("TScrollbar", background=BG2, troughcolor=BG,
                    borderwidth=0, arrowsize=12)
        s.configure("Treeview",  background=BG2, foreground=TEXT,
                    fieldbackground=BG2, rowheight=26, font=UI)
        s.configure("Treeview.Heading", background=BG3, foreground=ACCENT2,
                    font=("Segoe UI", 10, "bold"))
        s.map("Treeview", background=[("selected", BG3)],
                          foreground=[("selected", ACCENT2)])
        s.configure("TRadiobutton", background=BG2, foreground=TEXT, font=UI)
        s.map("TRadiobutton", background=[("active", BG2)],
                              foreground=[("active", ACCENT2)])

    # ── Main UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG3, height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚡ Regex Tool", font=("Segoe UI", 15, "bold"),
                 bg=BG3, fg=ACCENT2).pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text="smart search · tester · file search",
                 font=("Segoe UI", 9), bg=BG3, fg=DIM).pack(side="left", pady=14)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self._build_smart(nb)
        self._build_search(nb)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — SMART SEARCH
    # ══════════════════════════════════════════════════════════════════════════
    def _build_smart(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="  🔬 Smart Search  ")

        # ── Top input area ────────────────────────────────────────────────────
        top = tk.Frame(frame, bg=BG2, padx=16, pady=14)
        top.pack(fill="x")

        # Row 0 — labels
        tk.Label(top, text="Word to search", font=("Segoe UI", 9),
                 bg=BG2, fg=DIM).grid(row=0, column=0, sticky="w")
        tk.Label(top, text="Describe how to search (natural language)",
                 font=("Segoe UI", 9), bg=BG2, fg=DIM).grid(
                 row=0, column=1, sticky="w", padx=(16, 0))

        # Row 1 — inputs
        self.word_var = tk.StringVar()
        self.word_var.trace_add("write", self._on_input_change)
        tk.Entry(top, textvariable=self.word_var, font=MONO,
                 bg=BG, fg=ACCENT2, insertbackground=TEXT,
                 relief="flat", bd=0, highlightthickness=2,
                 highlightcolor=ACCENT, highlightbackground=BG3,
                 width=18).grid(row=1, column=0, sticky="ew", ipady=6)

        self.desc_var = tk.StringVar()
        self.desc_var.trace_add("write", self._on_input_change)
        desc_hints = (
            'e.g. "ignore case", "ends with s", "starts with", "repeating"'
        )
        self.desc_entry = tk.Entry(top, textvariable=self.desc_var, font=UI,
                                   bg=BG, fg=TEXT, insertbackground=TEXT,
                                   relief="flat", bd=0, highlightthickness=2,
                                   highlightcolor=ACCENT, highlightbackground=BG3)
        self.desc_entry.grid(row=1, column=1, sticky="ew", padx=(16, 0), ipady=6)
        top.columnconfigure(1, weight=1)

        # Row 2 — mode selector
        mode_frame = tk.Frame(top, bg=BG2)
        mode_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))

        tk.Label(mode_frame, text="Regex field:", font=("Segoe UI", 9),
                 bg=BG2, fg=DIM).pack(side="left", padx=(0, 10))

        for val, label in [(1, "1 — View"), (2, "2 — Edit"), (3, "3 — Stop")]:
            tk.Radiobutton(mode_frame, text=label, variable=self._mode, value=val,
                           bg=BG2, fg=TEXT, selectcolor=BG3, activebackground=BG2,
                           activeforeground=ACCENT2, font=UI,
                           command=self._on_mode_change).pack(side="left", padx=8)

        # ── Regex display area ────────────────────────────────────────────────
        regex_row = tk.Frame(frame, bg=BG3, padx=16, pady=10)
        regex_row.pack(fill="x")

        tk.Label(regex_row, text="Generated regex:", font=("Segoe UI", 9),
                 bg=BG3, fg=DIM).pack(side="left")

        self.regex_var = tk.StringVar()
        self.regex_var.trace_add("write", self._update_matches)
        self.regex_entry = tk.Entry(regex_row, textvariable=self.regex_var,
                                    font=MONO, bg=BG, fg=SUCCESS,
                                    insertbackground=TEXT, relief="flat",
                                    bd=0, highlightthickness=1,
                                    highlightbackground=BG3,
                                    highlightcolor=ACCENT,
                                    state="readonly", width=40)
        self.regex_entry.pack(side="left", padx=(12, 0), ipady=4, fill="x", expand=True)

        self.status_var = tk.StringVar(value="Type a word and describe the search")
        tk.Label(regex_row, textvariable=self.status_var, font=("Segoe UI", 9),
                 bg=BG3, fg=DIM).pack(side="right", padx=(16, 0))

        # ── Explanation box ───────────────────────────────────────────────────
        self.explain_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.explain_var, font=("Segoe UI", 9),
                 bg=BG2, fg=ACCENT2, anchor="w", justify="left",
                 padx=16, pady=6).pack(fill="x")

        # ── Body: test text + results ─────────────────────────────────────────
        body = tk.PanedWindow(frame, orient="vertical", bg=BG,
                              sashwidth=6, sashrelief="flat")
        body.pack(fill="both", expand=True)

        # Test text
        test_frame = tk.Frame(body, bg=BG)
        tk.Label(test_frame, text="Test text", font=("Segoe UI", 9),
                 bg=BG, fg=DIM).pack(anchor="w", padx=16, pady=(10, 2))
        self.test_text = tk.Text(test_frame, font=MONO, bg=BG2, fg=TEXT,
                                 insertbackground=TEXT, relief="flat",
                                 bd=0, padx=12, pady=10, wrap="word", undo=True)
        self.test_text.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.test_text.bind("<KeyRelease>", self._update_matches)
        self.test_text.tag_configure("match",
                                     background="#e9456080", foreground="#ffffff")
        self.test_text.tag_configure("match_alt",
                                     background="#53d8fb60", foreground="#ffffff")
        self.test_text.insert("1.0",
            "Type your test text here!\n\n"
            "Try searching: cat, Cat, Cats, cats, CATS, catsss\n"
            "Or: hello world, File01, file12, user@domain.com\n"
            "IP: 192.168.1.1 — Password:Abc1234xyz"
        )
        body.add(test_frame, minsize=120)

        # Results table
        res_frame = tk.Frame(body, bg=BG)
        tk.Label(res_frame, text="Matches", font=("Segoe UI", 9),
                 bg=BG, fg=DIM).pack(anchor="w", padx=16, pady=(10, 2))
        cols = ("n", "match", "start", "end", "groups")
        self.result_tree = ttk.Treeview(res_frame, columns=cols,
                                        show="headings", height=5)
        for col, w, label in [("n", 40, "#"), ("match", 200, "Match"),
                               ("start", 70, "Start"), ("end", 70, "End"),
                               ("groups", 300, "Captured groups")]:
            self.result_tree.heading(col, text=label)
            self.result_tree.column(col, width=w, minwidth=w)
        sb = ttk.Scrollbar(res_frame, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 8))
        self.result_tree.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        body.add(res_frame, minsize=100)

    # ── Mode handling ─────────────────────────────────────────────────────────
    def _on_mode_change(self):
        mode = self._mode.get()
        if mode == 1:
            self.regex_entry.configure(state="readonly")
            self._on_input_change()
        elif mode == 2:
            self.regex_entry.configure(state="normal")
        elif mode == 3:
            self.regex_entry.configure(state="readonly")
            self.regex_var.set("")
            self._clear_matches()
            self.status_var.set("Stopped — choose mode 1 or 2 to resume")
            self.explain_var.set("")

    def _on_input_change(self, *_):
        if self._mode.get() == 3:
            return
        word = self.word_var.get().strip()
        desc = self.desc_var.get().strip()

        if not word:
            self.regex_var.set("")
            self.status_var.set("Type a word to search")
            self.explain_var.set("")
            self._clear_matches()
            return

        pattern, explanations = parse_natural_language(desc, word)

        if self._mode.get() == 1:
            self.regex_entry.configure(state="normal")
            self.regex_var.set(pattern)
            self.regex_entry.configure(state="readonly")
        elif self._mode.get() == 2:
            self.regex_var.set(pattern)

        if explanations:
            self.explain_var.set("Applied rules:  " + "   ".join(explanations))
        else:
            self.explain_var.set(f'Searching for "{word}" exactly as typed')

        self._update_matches()

    def _update_matches(self, *_):
        if self._mode.get() == 3:
            return
        pattern = self.regex_var.get()
        text = self.test_text.get("1.0", "end-1c")

        self._clear_matches()
        if not pattern:
            return

        try:
            rx = re.compile(pattern)
        except re.error as e:
            self.status_var.set(f"⚠ Invalid pattern: {e}")
            return

        matches = list(rx.finditer(text))
        if not matches:
            self.status_var.set("No matches found")
            return

        self.status_var.set(f"✓  {len(matches)} match{'es' if len(matches) > 1 else ''} found")
        for i, m in enumerate(matches):
            tag = "match" if i % 2 == 0 else "match_alt"
            self.test_text.tag_add(tag,
                                   f"1.0 + {m.start()} chars",
                                   f"1.0 + {m.end()} chars")
            groups = " | ".join(
                f"G{j+1}={g}" for j, g in enumerate(m.groups()) if g is not None
            ) or "—"
            self.result_tree.insert("", "end",
                values=(i + 1, m.group(), m.start(), m.end(), groups))

    def _clear_matches(self):
        self.test_text.tag_remove("match",     "1.0", "end")
        self.test_text.tag_remove("match_alt", "1.0", "end")
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — FILE SEARCH
    # ══════════════════════════════════════════════════════════════════════════
    def _build_search(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="  🗂 File Search  ")

        ctrl = tk.Frame(frame, bg=BG2, padx=16, pady=12)
        ctrl.pack(fill="x")

        tk.Label(ctrl, text="Directory", font=("Segoe UI", 9),
                 bg=BG2, fg=DIM).grid(row=0, column=0, sticky="w")
        tk.Label(ctrl, text="Filename pattern (regex)",
                 font=("Segoe UI", 9), bg=BG2, fg=DIM).grid(
                 row=0, column=1, sticky="w", padx=(12, 0))
        tk.Label(ctrl, text="Content pattern (regex)",
                 font=("Segoe UI", 9), bg=BG2, fg=DIM).grid(
                 row=0, column=2, sticky="w", padx=(12, 0))

        self.dir_var = tk.StringVar(value=str(Path.home()))
        dir_entry = tk.Entry(ctrl, textvariable=self.dir_var, font=UI,
                             bg=BG, fg=TEXT, insertbackground=TEXT,
                             relief="flat", bd=0, highlightthickness=1,
                             highlightbackground=BG3, highlightcolor=ACCENT)
        dir_entry.grid(row=1, column=0, sticky="ew", ipady=5)
        tk.Button(ctrl, text="…", bg=BG3, fg=TEXT, relief="flat",
                  font=UI, cursor="hand2",
                  command=self._browse_dir).grid(row=1, column=0, sticky="e")

        self.fname_var = tk.StringVar()
        tk.Entry(ctrl, textvariable=self.fname_var, font=MONO,
                 bg=BG, fg=ACCENT2, insertbackground=TEXT,
                 relief="flat", bd=0, highlightthickness=1,
                 highlightbackground=BG3, highlightcolor=ACCENT).grid(
                 row=1, column=1, sticky="ew", padx=(12, 0), ipady=5)

        self.content_var2 = tk.StringVar()
        tk.Entry(ctrl, textvariable=self.content_var2, font=MONO,
                 bg=BG, fg=ACCENT2, insertbackground=TEXT,
                 relief="flat", bd=0, highlightthickness=1,
                 highlightbackground=BG3, highlightcolor=ACCENT).grid(
                 row=1, column=2, sticky="ew", padx=(12, 0), ipady=5)

        ctrl.columnconfigure(0, weight=2)
        ctrl.columnconfigure(1, weight=2)
        ctrl.columnconfigure(2, weight=2)

        opt = tk.Frame(ctrl, bg=BG2)
        opt.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))

        self.recur_var  = tk.BooleanVar(value=True)
        self.hidden_var = tk.BooleanVar(value=False)
        self.icase_var  = tk.BooleanVar(value=False)

        for text, var in [("Recursive", self.recur_var),
                          ("Include hidden", self.hidden_var),
                          ("Case-insensitive", self.icase_var)]:
            tk.Checkbutton(opt, text=text, variable=var,
                           bg=BG2, fg=TEXT, selectcolor=BG3,
                           activebackground=BG2, activeforeground=ACCENT2,
                           font=UI).pack(side="left", padx=(0, 16))

        self.search_btn = tk.Button(ctrl, text="🔍  Search",
                                    bg=ACCENT, fg="#fff",
                                    font=("Segoe UI", 10, "bold"),
                                    relief="flat", padx=18, pady=6,
                                    cursor="hand2", command=self._run_search)
        self.search_btn.grid(row=2, column=2, sticky="e", pady=(8, 0))

        self.fs_status = tk.StringVar(value="Ready to search")
        tk.Label(frame, textvariable=self.fs_status, font=("Segoe UI", 9),
                 bg=BG, fg=DIM, anchor="w").pack(fill="x", padx=16, pady=(6, 2))

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", padx=16)

        res = tk.Frame(frame, bg=BG)
        res.pack(fill="both", expand=True, padx=12, pady=8)

        cols = ("path", "file", "size", "hits")
        self.fs_tree = ttk.Treeview(res, columns=cols, show="headings")
        for col, w, label in [("path", 350, "Path"), ("file", 200, "File"),
                               ("size", 80, "Size"), ("hits", 80, "Hits")]:
            self.fs_tree.heading(col, text=label)
            self.fs_tree.column(col, width=w, minwidth=60)
        vsb = ttk.Scrollbar(res, command=self.fs_tree.yview)
        hsb = ttk.Scrollbar(res, orient="horizontal", command=self.fs_tree.xview)
        self.fs_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.fs_tree.pack(fill="both", expand=True)
        self.fs_tree.bind("<Double-1>", self._open_location)

        self.fs_count = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.fs_count, font=("Segoe UI", 9),
                 bg=BG, fg=SUCCESS, anchor="w").pack(fill="x", padx=16, pady=(0, 8))

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _run_search(self):
        self.search_btn.configure(state="disabled", text="Searching…")
        for row in self.fs_tree.get_children():
            self.fs_tree.delete(row)
        self.fs_count.set("")
        self.progress.start(12)
        threading.Thread(target=self._search_worker, daemon=True).start()

    def _search_worker(self):
        flags = re.IGNORECASE if self.icase_var.get() else 0
        try:
            fname_rx = re.compile(self.fname_var.get(), flags) if self.fname_var.get() else None
            content_rx = re.compile(self.content_var2.get(), flags) if self.content_var2.get() else None
        except re.error as e:
            self.after(0, lambda: self._search_done([], f"Pattern error: {e}"))
            return

        results = []
        errors = 0
        p = Path(self.dir_var.get())
        walker = p.rglob("*") if self.recur_var.get() else p.iterdir()

        try:
            for path in walker:
                if not path.is_file():
                    continue
                if not self.hidden_var.get() and path.name.startswith("."):
                    continue
                if fname_rx and not fname_rx.search(path.name):
                    continue
                hits = 0
                if content_rx:
                    try:
                        hits = len(content_rx.findall(
                            path.read_text(encoding="utf-8", errors="ignore")))
                        if hits == 0:
                            continue
                    except (PermissionError, OSError):
                        errors += 1
                        continue
                size = path.stat().st_size
                results.append((str(path.parent), path.name,
                                 _fmt_size(size), str(hits) if content_rx else "—"))
                if len(results) % 50 == 0:
                    self.after(0, lambda n=len(results):
                               self.fs_status.set(f"Found {n} files…"))
        except Exception as e:
            errors += 1

        msg = f"✓ {len(results)} file(s) found"
        if errors:
            msg += f"  ({errors} permission errors skipped)"
        self.after(0, lambda: self._search_done(results, msg))

    def _search_done(self, results, msg):
        self.progress.stop()
        self.fs_status.set(msg)
        self.search_btn.configure(state="normal", text="🔍  Search")
        for row in results:
            self.fs_tree.insert("", "end", values=row)
        self.fs_count.set(f"{len(results)} result(s)")

    def _open_location(self, event):
        sel = self.fs_tree.selection()
        if not sel:
            return
        vals = self.fs_tree.item(sel[0])["values"]
        try:
            os.system(f'xdg-open "{vals[0]}"')
        except Exception:
            messagebox.showinfo("Path", str(Path(vals[0]) / vals[1]))


def _fmt_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


if __name__ == "__main__":
    app = RegexTool()
    app.mainloop()
