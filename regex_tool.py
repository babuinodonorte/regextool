#!/usr/bin/env python3
"""
Regex Tool — Tester, referência e busca no sistema
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
import threading
from pathlib import Path


# ── Paleta de cores ────────────────────────────────────────────────────────────
BG        = "#1a1a2e"
BG2       = "#16213e"
BG3       = "#0f3460"
ACCENT    = "#e94560"
ACCENT2   = "#53d8fb"
TEXT      = "#e8e8e8"
TEXT_DIM  = "#8888aa"
SUCCESS   = "#4ade80"
WARNING   = "#facc15"
ERROR     = "#f87171"
MATCH_BG  = "#e9456055"   # highlight de match (suportado pelo tkinter via tag)
MATCH_FG  = "#ffffff"
FONT_MONO = ("JetBrains Mono", 11) if "JetBrains Mono" in tk.font.families() \
            else ("Courier New", 11)
FONT_UI   = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI", 13, "bold")


# ── Cheatsheet ─────────────────────────────────────────────────────────────────
CHEATSHEET = [
    ("CARACTERES ESPECIAIS", None, None),
    (".",        "Qualquer caractere (exceto \\n)",  "a.c → abc, a1c, a!c"),
    ("\\d",      "Dígito [0-9]",                     "\\d{3} → 123, 007"),
    ("\\D",      "Não-dígito",                       "\\D+ → abc, !@#"),
    ("\\w",      "Alfanumérico + _",                 "\\w+ → hello_world"),
    ("\\W",      "Não-alfanumérico",                 "\\W → ! @ # espaço"),
    ("\\s",      "Espaço, tab, newline",              "kali\\s+tools"),
    ("\\S",      "Não-whitespace",                   "\\S{5} → hello"),

    ("QUANTIFICADORES", None, None),
    ("*",        "0 ou mais",                        "cats* → cat, cats, catsss"),
    ("+",        "1 ou mais",                        "go br+ → go br, go brrr"),
    ("?",        "0 ou 1 (opcional)",                "colou?r → color, colour"),
    ("{n}",      "Exatamente n vezes",               "z{3} → zzz"),
    ("{n,m}",    "Entre n e m vezes",                "\\d{2,4} → 12, 1234"),
    ("{n,}",     "n ou mais vezes",                  "\\w{3,} → cat, hello"),

    ("ÂNCORAS", None, None),
    ("^",        "Início da linha",                  "^username: → linha começa com"),
    ("$",        "Fim da linha",                     "EOF$ → linha termina com EOF"),
    ("\\b",      "Limite de palavra",                "\\bcat\\b → cat (não concatenar)"),

    ("CLASSES DE CARACTERES", None, None),
    ("[abc]",    "a, b ou c",                        "[cfh]at → cat, fat, hat"),
    ("[a-z]",    "Intervalo de a até z",             "[a-z]+ → minúsculas"),
    ("[^abc]",   "Negação — nada de a, b, c",        "[^0-9] → não-dígito"),
    ("[A-Za-z]", "Letras maiúsculas e minúsculas",   "[A-Za-z]+ → palavras"),

    ("GRUPOS E ALTERNÂNCIA", None, None),
    ("(abc)",    "Grupo de captura",                 "(\\w+)@(\\w+)\\.com"),
    ("(?:abc)",  "Grupo sem captura",                "(?:https?://)?\\w+"),
    ("a|b",      "a ou b",                           "nano|vim → nano ou vim"),
    ("(a|b){3}", "Grupo repetido",                   "(ab|cd){2} → abcd"),

    ("ESCAPE", None, None),
    ("\\.",      "Ponto literal",                    "cat\\.xyz → domínio real"),
    ("\\$",      "Cifrão literal",                   "\\$\\d → $5"),
    ("\\(",      "Parêntese literal",                "\\(\\w+\\)"),
]


# ── Helpers ────────────────────────────────────────────────────────────────────
def apply_style(widget, **kwargs):
    """Aplica configurações em lote."""
    widget.configure(**kwargs)


# ══════════════════════════════════════════════════════════════════════════════
class RegexTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Regex Tool")
        self.geometry("900x680")
        self.minsize(720, 500)
        self.configure(bg=BG)
        self._setup_styles()
        self._build_ui()

    # ── Estilos ttk ───────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure("TNotebook",        background=BG,  borderwidth=0)
        s.configure("TNotebook.Tab",
                    background=BG2, foreground=TEXT_DIM,
                    padding=[16, 8], font=FONT_UI)
        s.map("TNotebook.Tab",
              background=[("selected", BG3)],
              foreground=[("selected", ACCENT2)])

        s.configure("TFrame",  background=BG)
        s.configure("TLabel",  background=BG,  foreground=TEXT,     font=FONT_UI)
        s.configure("TButton", background=BG3, foreground=TEXT,     font=FONT_UI,
                    borderwidth=0, padding=[10, 6])
        s.map("TButton",
              background=[("active", ACCENT)],
              foreground=[("active", "#fff")])

        s.configure("Accent.TButton", background=ACCENT, foreground="#fff",
                    font=("Segoe UI", 10, "bold"), padding=[14, 7])
        s.map("Accent.TButton", background=[("active", "#c73350")])

        s.configure("TScrollbar", background=BG2, troughcolor=BG,
                    borderwidth=0, arrowsize=12)
        s.configure("TEntry",     fieldbackground=BG2, foreground=TEXT,
                    insertcolor=TEXT, borderwidth=1, relief="flat")
        s.configure("Treeview",   background=BG2, foreground=TEXT,
                    fieldbackground=BG2, rowheight=26, font=FONT_UI)
        s.configure("Treeview.Heading", background=BG3, foreground=ACCENT2,
                    font=("Segoe UI", 10, "bold"))
        s.map("Treeview", background=[("selected", BG3)],
                          foreground=[("selected", ACCENT2)])

    # ── UI principal ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # Cabeçalho
        hdr = tk.Frame(self, bg=BG3, height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚡ Regex Tool", font=("Segoe UI", 15, "bold"),
                 bg=BG3, fg=ACCENT2).pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text="tester · referência · busca no sistema",
                 font=("Segoe UI", 9), bg=BG3, fg=TEXT_DIM).pack(side="left", pady=14)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_tester(nb)
        self._build_reference(nb)
        self._build_search(nb)

    # ══════════════════════════════════════════════════════════════════════════
    # ABA 1 — TESTER
    # ══════════════════════════════════════════════════════════════════════════
    def _build_tester(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="  🔬 Tester  ")

        # Painel superior — regex input
        top = tk.Frame(frame, bg=BG2, pady=12, padx=16)
        top.pack(fill="x")

        tk.Label(top, text="Expressão regular", font=("Segoe UI", 9),
                 bg=BG2, fg=TEXT_DIM).grid(row=0, column=0, sticky="w")
        tk.Label(top, text="Flags", font=("Segoe UI", 9),
                 bg=BG2, fg=TEXT_DIM).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.regex_var = tk.StringVar()
        self.regex_var.trace_add("write", self._on_regex_change)
        regex_entry = tk.Entry(top, textvariable=self.regex_var,
                               font=FONT_MONO, bg=BG, fg=ACCENT2,
                               insertbackground=TEXT, relief="flat",
                               bd=0, highlightthickness=2,
                               highlightcolor=ACCENT, highlightbackground=BG3)
        regex_entry.grid(row=1, column=0, sticky="ew", ipady=6)

        # Flags
        flag_frame = tk.Frame(top, bg=BG2)
        flag_frame.grid(row=1, column=1, padx=(12, 0), sticky="w")
        self.flag_i = tk.BooleanVar()
        self.flag_m = tk.BooleanVar()
        self.flag_s = tk.BooleanVar()
        for text, var, tip in [("i", self.flag_i, "ignore case"),
                                ("m", self.flag_m, "multiline"),
                                ("s", self.flag_s, "dotall")]:
            cb = tk.Checkbutton(flag_frame, text=text, variable=var,
                                bg=BG2, fg=TEXT, selectcolor=BG3,
                                activebackground=BG2, activeforeground=ACCENT2,
                                font=FONT_MONO, command=self._update_tester)
            cb.pack(side="left", padx=4)

        top.columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Digite uma expressão acima")
        status = tk.Label(top, textvariable=self.status_var, font=("Segoe UI", 9),
                          bg=BG2, fg=TEXT_DIM, anchor="w")
        status.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Corpo — texto de teste + resultado
        body = tk.PanedWindow(frame, orient="vertical", bg=BG,
                              sashwidth=6, sashrelief="flat")
        body.pack(fill="both", expand=True)

        # Texto de teste
        test_frame = tk.Frame(body, bg=BG)
        tk.Label(test_frame, text="Texto de teste", font=("Segoe UI", 9),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", padx=16, pady=(10, 2))
        self.test_text = tk.Text(test_frame, font=FONT_MONO, bg=BG2, fg=TEXT,
                                 insertbackground=TEXT, relief="flat",
                                 bd=0, padx=12, pady=10, wrap="word",
                                 undo=True)
        self.test_text.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.test_text.bind("<KeyRelease>", self._update_tester)
        self.test_text.tag_configure("match",
                                     background="#e9456080",
                                     foreground="#ffffff")
        self.test_text.tag_configure("match_alt",
                                     background="#53d8fb60",
                                     foreground="#ffffff")
        # Texto padrão
        self.test_text.insert("1.0",
            "Teste seus padrões aqui!\n\n"
            "Emails: hello@tryhackme.com, user@domain.com\n"
            "IPs: 192.168.1.1, 10.0.0.254, 255.255.255.0\n"
            "Arquivos: File01, file12, File99, notes~, .bash_rc\n"
            "Misc: cats, catsss, regex go brrrrrr, Password:Abc1234xyz"
        )
        body.add(test_frame, minsize=120)

        # Resultado / grupos
        result_frame = tk.Frame(body, bg=BG)
        tk.Label(result_frame, text="Matches e grupos",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT_DIM).pack(
                 anchor="w", padx=16, pady=(10, 2))

        cols = ("n", "match", "start", "end", "grupos")
        self.result_tree = ttk.Treeview(result_frame, columns=cols,
                                        show="headings", height=6)
        for col, w, label in [("n", 40, "#"), ("match", 200, "Match"),
                               ("start", 60, "Início"), ("end", 60, "Fim"),
                               ("grupos", 300, "Grupos capturados")]:
            self.result_tree.heading(col, text=label)
            self.result_tree.column(col, width=w, minwidth=w)

        sb = ttk.Scrollbar(result_frame, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 8))
        self.result_tree.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        body.add(result_frame, minsize=100)

    def _get_flags(self):
        flags = 0
        if self.flag_i.get(): flags |= re.IGNORECASE
        if self.flag_m.get(): flags |= re.MULTILINE
        if self.flag_s.get(): flags |= re.DOTALL
        return flags

    def _on_regex_change(self, *_):
        self._update_tester()

    def _update_tester(self, *_):
        pattern = self.regex_var.get()
        text    = self.test_text.get("1.0", "end-1c")

        # Limpa highlights e tabela
        self.test_text.tag_remove("match",     "1.0", "end")
        self.test_text.tag_remove("match_alt", "1.0", "end")
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)

        if not pattern:
            self.status_var.set("Digite uma expressão acima")
            return

        try:
            rx = re.compile(pattern, self._get_flags())
        except re.error as e:
            self.status_var.set(f"⚠ Erro: {e}")
            self._set_entry_error(True)
            return

        self._set_entry_error(False)
        matches = list(rx.finditer(text))

        if not matches:
            self.status_var.set("Nenhum match encontrado")
            return

        self.status_var.set(f"✓  {len(matches)} match{'es' if len(matches) > 1 else ''} encontrado{'s' if len(matches) > 1 else ''}")

        for i, m in enumerate(matches):
            tag = "match" if i % 2 == 0 else "match_alt"
            start_idx = f"1.0 + {m.start()} chars"
            end_idx   = f"1.0 + {m.end()} chars"
            self.test_text.tag_add(tag, start_idx, end_idx)

            grupos = " | ".join(f"G{j+1}={g}" for j, g in enumerate(m.groups()) if g is not None) \
                     or "—"
            self.result_tree.insert("", "end",
                values=(i + 1, m.group(), m.start(), m.end(), grupos))

    def _set_entry_error(self, error: bool):
        # Muda cor do highlight do entry para indicar erro
        pass  # tkinter Entry não tem acesso fácil — status bar já cobre

    # ══════════════════════════════════════════════════════════════════════════
    # ABA 2 — REFERÊNCIA
    # ══════════════════════════════════════════════════════════════════════════
    def _build_reference(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="  📖 Referência  ")

        tk.Label(frame, text="Clique em qualquer exemplo para carregá-lo no Tester",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT_DIM).pack(
                 anchor="w", padx=16, pady=(12, 4))

        # Canvas com scroll
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True, padx=8)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        canvas.bind("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>",   lambda e: canvas.yview_scroll(1, "units"))

        for item in CHEATSHEET:
            if item[1] is None:
                # Cabeçalho de seção
                sec = tk.Frame(inner, bg=BG3, height=1)
                sec.pack(fill="x", pady=(18, 6), padx=8)
                tk.Label(inner, text=item[0], font=("Segoe UI", 10, "bold"),
                         bg=BG, fg=ACCENT2).pack(anchor="w", padx=12)
            else:
                token, desc, example = item
                row = tk.Frame(inner, bg=BG2, cursor="hand2")
                row.pack(fill="x", padx=8, pady=2)
                row.bind("<Enter>",  lambda e, r=row: r.configure(bg=BG3))
                row.bind("<Leave>",  lambda e, r=row: r.configure(bg=BG2))

                tk.Label(row, text=token, font=FONT_MONO, width=12,
                         bg=BG2, fg=ACCENT, anchor="w",
                         padx=12, pady=6).grid(row=0, column=0, sticky="w")
                tk.Label(row, text=desc, font=FONT_UI, bg=BG2,
                         fg=TEXT, anchor="w", padx=8).grid(row=0, column=1, sticky="w")
                ex_lbl = tk.Label(row, text=f"ex: {example}", font=FONT_MONO,
                                  bg=BG2, fg=TEXT_DIM, anchor="e",
                                  padx=12, cursor="hand2")
                ex_lbl.grid(row=0, column=2, sticky="e")
                row.columnconfigure(2, weight=1)

                # Clique → carrega no tester
                def _load(e, tok=token, ex=example):
                    # Extrai só o padrão (parte antes do →)
                    pattern = ex.split("→")[0].strip()
                    self.regex_var.set(tok)
                    # Muda pra aba tester
                    nb_widget = self.nametowidget(frame.winfo_parent())
                    nb_widget.select(0)

                row.bind("<Button-1>", _load)
                ex_lbl.bind("<Button-1>", _load)
                for child in row.winfo_children():
                    child.bind("<Enter>",  lambda e, r=row: r.configure(bg=BG3))
                    child.bind("<Leave>",  lambda e, r=row: r.configure(bg=BG2))
                    child.bind("<Button-1>", _load)

    # ══════════════════════════════════════════════════════════════════════════
    # ABA 3 — BUSCA NO SISTEMA
    # ══════════════════════════════════════════════════════════════════════════
    def _build_search(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="  🗂 Busca no sistema  ")

        # Controles
        ctrl = tk.Frame(frame, bg=BG2, padx=16, pady=12)
        ctrl.pack(fill="x")

        # Linha 1 — diretório
        tk.Label(ctrl, text="Diretório", font=("Segoe UI", 9),
                 bg=BG2, fg=TEXT_DIM).grid(row=0, column=0, sticky="w")
        tk.Label(ctrl, text="Padrão regex (nome do arquivo)",
                 font=("Segoe UI", 9), bg=BG2, fg=TEXT_DIM).grid(
                 row=0, column=1, sticky="w", padx=(12, 0))
        tk.Label(ctrl, text="Dentro do arquivo",
                 font=("Segoe UI", 9), bg=BG2, fg=TEXT_DIM).grid(
                 row=0, column=2, sticky="w", padx=(12, 0))

        self.dir_var = tk.StringVar(value=str(Path.home()))
        dir_entry = tk.Entry(ctrl, textvariable=self.dir_var, font=FONT_UI,
                             bg=BG, fg=TEXT, insertbackground=TEXT,
                             relief="flat", bd=0, highlightthickness=1,
                             highlightbackground=BG3, highlightcolor=ACCENT)
        dir_entry.grid(row=1, column=0, sticky="ew", ipady=5)

        tk.Button(ctrl, text="…", bg=BG3, fg=TEXT, relief="flat",
                  font=FONT_UI, cursor="hand2",
                  command=self._browse_dir).grid(row=1, column=0,
                  sticky="e", padx=(0, 0))

        self.fname_var = tk.StringVar()
        fname_entry = tk.Entry(ctrl, textvariable=self.fname_var, font=FONT_MONO,
                               bg=BG, fg=ACCENT2, insertbackground=TEXT,
                               relief="flat", bd=0, highlightthickness=1,
                               highlightbackground=BG3, highlightcolor=ACCENT)
        fname_entry.grid(row=1, column=1, sticky="ew", padx=(12, 0), ipady=5)

        self.content_var = tk.StringVar()
        content_entry = tk.Entry(ctrl, textvariable=self.content_var, font=FONT_MONO,
                                 bg=BG, fg=ACCENT2, insertbackground=TEXT,
                                 relief="flat", bd=0, highlightthickness=1,
                                 highlightbackground=BG3, highlightcolor=ACCENT)
        content_entry.grid(row=1, column=2, sticky="ew", padx=(12, 0), ipady=5)

        ctrl.columnconfigure(0, weight=2)
        ctrl.columnconfigure(1, weight=2)
        ctrl.columnconfigure(2, weight=2)

        # Linha 2 — opções + botão
        opt_frame = tk.Frame(ctrl, bg=BG2)
        opt_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))

        self.recur_var = tk.BooleanVar(value=True)
        self.hidden_var = tk.BooleanVar(value=False)
        self.case_var   = tk.BooleanVar(value=False)

        for text, var in [("Recursivo", self.recur_var),
                          ("Incluir ocultos", self.hidden_var),
                          ("Case-insensitive", self.case_var)]:
            tk.Checkbutton(opt_frame, text=text, variable=var,
                           bg=BG2, fg=TEXT, selectcolor=BG3,
                           activebackground=BG2, activeforeground=ACCENT2,
                           font=FONT_UI).pack(side="left", padx=(0, 16))

        self.search_btn = tk.Button(ctrl, text="🔍  Buscar",
                                    bg=ACCENT, fg="#fff",
                                    font=("Segoe UI", 10, "bold"),
                                    relief="flat", padx=18, pady=6,
                                    cursor="hand2",
                                    command=self._run_search)
        self.search_btn.grid(row=2, column=2, sticky="e", pady=(8, 0))

        # Barra de progresso / status
        self.search_status = tk.StringVar(value="Pronto para buscar")
        tk.Label(frame, textvariable=self.search_status, font=("Segoe UI", 9),
                 bg=BG, fg=TEXT_DIM, anchor="w").pack(fill="x", padx=16, pady=(6, 2))

        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=200)
        self.progress.pack(fill="x", padx=16)

        # Resultado
        res_frame = tk.Frame(frame, bg=BG)
        res_frame.pack(fill="both", expand=True, padx=12, pady=8)

        cols = ("caminho", "arquivo", "tamanho", "matches_conteudo")
        self.search_tree = ttk.Treeview(res_frame, columns=cols,
                                         show="headings")
        for col, w, label in [("caminho", 350, "Caminho"), ("arquivo", 200, "Arquivo"),
                               ("tamanho", 80, "Tamanho"), ("matches_conteudo", 80, "Ocorrências")]:
            self.search_tree.heading(col, text=label)
            self.search_tree.column(col, width=w, minwidth=60)

        vsb = ttk.Scrollbar(res_frame, command=self.search_tree.yview)
        hsb = ttk.Scrollbar(res_frame, orient="horizontal",
                             command=self.search_tree.xview)
        self.search_tree.configure(yscrollcommand=vsb.set,
                                    xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.search_tree.pack(fill="both", expand=True)

        # Duplo-clique → abre local
        self.search_tree.bind("<Double-1>", self._open_file_location)

        # Barra inferior
        self.count_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.count_var, font=("Segoe UI", 9),
                 bg=BG, fg=SUCCESS, anchor="w").pack(fill="x", padx=16, pady=(0, 8))

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _run_search(self):
        self.search_btn.configure(state="disabled", text="Buscando…")
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)
        self.count_var.set("")
        self.progress.start(12)
        t = threading.Thread(target=self._search_worker, daemon=True)
        t.start()

    def _search_worker(self):
        directory    = self.dir_var.get()
        fname_pat    = self.fname_var.get()
        content_pat  = self.content_var.get()
        recursive    = self.recur_var.get()
        show_hidden  = self.hidden_var.get()
        flags        = re.IGNORECASE if self.case_var.get() else 0

        results = []
        errors  = []

        # Compila padrões
        try:
            fname_rx = re.compile(fname_pat, flags) if fname_pat else None
        except re.error as e:
            self.after(0, lambda: self._search_done([], f"Erro no padrão de nome: {e}"))
            return

        try:
            content_rx = re.compile(content_pat, flags) if content_pat else None
        except re.error as e:
            self.after(0, lambda: self._search_done([], f"Erro no padrão de conteúdo: {e}"))
            return

        def _walk():
            p = Path(directory)
            if recursive:
                yield from p.rglob("*")
            else:
                yield from p.iterdir()

        count = 0
        try:
            for path in _walk():
                if not path.is_file():
                    continue
                if not show_hidden and path.name.startswith("."):
                    continue

                # Filtra por nome
                if fname_rx and not fname_rx.search(path.name):
                    continue

                # Filtra por conteúdo
                n_content_matches = 0
                if content_rx:
                    try:
                        text = path.read_text(encoding="utf-8", errors="ignore")
                        n_content_matches = len(content_rx.findall(text))
                        if n_content_matches == 0:
                            continue
                    except (PermissionError, OSError):
                        continue

                size = path.stat().st_size
                size_str = _fmt_size(size)
                results.append((
                    str(path.parent),
                    path.name,
                    size_str,
                    str(n_content_matches) if content_rx else "—"
                ))
                count += 1
                if count % 50 == 0:
                    self.after(0, lambda c=count: self.search_status.set(
                        f"Encontrados {c} arquivos…"))

        except Exception as e:
            errors.append(str(e))

        msg = f"✓ {len(results)} arquivo(s) encontrado(s)"
        if errors:
            msg += f"  ({len(errors)} erros de permissão ignorados)"
        self.after(0, lambda: self._search_done(results, msg))

    def _search_done(self, results, msg):
        self.progress.stop()
        self.search_status.set(msg)
        self.search_btn.configure(state="normal", text="🔍  Buscar")
        for row in results:
            self.search_tree.insert("", "end", values=row)
        self.count_var.set(f"{len(results)} resultado(s)")

    def _open_file_location(self, event):
        sel = self.search_tree.selection()
        if not sel:
            return
        vals = self.search_tree.item(sel[0])["values"]
        path = str(Path(vals[0]) / vals[1])
        try:
            os.system(f'xdg-open "{Path(vals[0])}"')
        except Exception:
            messagebox.showinfo("Caminho", path)


# ── Utilitários ────────────────────────────────────────────────────────────────
def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import tkinter.font  # noqa: F401 — necessário pro families()
    app = RegexTool()
    app.mainloop()
