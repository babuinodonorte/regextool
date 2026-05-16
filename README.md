# Regex Tool

```
╔══════════════════════════════════════╗
║       REGEX TOOL — Linux GUI         ║
║  Tester · Referência · Busca         ║
╚══════════════════════════════════════╝
```

Ferramenta desktop para Linux com interface gráfica (tkinter).  
Teste expressões regulares em tempo real, consulte referência interativa e busque arquivos no sistema usando regex.

---

## Índice

- [Como funciona](#como-funciona)
- [Instalação](#instalação)
- [Abas e funcionalidades](#abas-e-funcionalidades)
- [Referência rápida de regex](#referência-rápida-de-regex)
- [Requisitos](#requisitos)
- [Desinstalação](#desinstalação)

---

## Como funciona

O **Regex Tool** tem três abas integradas:

| Aba | O que faz |
|-----|-----------|
| 🔬 Tester | Digita o padrão e o texto — matches são destacados em tempo real com grupos capturados |
| 📖 Referência | Cheatsheet completa de metacaracteres, quantificadores, âncoras e grupos. Clique em qualquer item para carregar no Tester |
| 🗂 Busca no sistema | Filtra arquivos por nome (regex) e/ou conteúdo interno, recursivamente |

Tudo roda localmente. Nenhum dado sai da máquina.

---

## Instalação

**Via script (recomendado):**

```bash
git clone https://github.com/BabuinoDoNorte/RegexTool.git
cd RegexTool
chmod +x install.sh
./install.sh
```

> Após instalar, o comando `regextool` fica disponível globalmente.

**One-liner:**

```bash
curl -fsSL https://raw.githubusercontent.com/BabuinoDoNorte/RegexTool/main/install.sh | bash
```

---

## Abas e funcionalidades

### 🔬 Tester

- Campo de regex com feedback visual de erro imediato
- Flags toggleáveis: `i` (ignore case), `m` (multiline), `s` (dotall)
- Matches destacados em dois tons alternados no texto
- Tabela com: número do match, texto, posição início/fim, grupos capturados

### 📖 Referência

- Seções: Caracteres especiais · Quantificadores · Âncoras · Classes · Grupos · Escape
- Cada item mostra símbolo, descrição e exemplo de uso
- **Clique em qualquer linha** → carrega o padrão direto no Tester

### 🗂 Busca no sistema

- Escolha o diretório (botão `…` ou digitando o caminho)
- **Padrão de nome**: filtra arquivos pelo nome usando regex (ex: `[Ff]ile\d+`)
- **Dentro do arquivo**: busca o padrão dentro do conteúdo dos arquivos de texto
- Opções: recursivo · incluir ocultos · case-insensitive
- Busca roda em thread separada — UI não trava
- Duplo-clique no resultado abre o gerenciador de arquivos no diretório

---

## Referência rápida de regex

| Padrão | Significado | Exemplo |
|--------|-------------|---------|
| `.` | Qualquer caractere (exceto `\n`) | `a.c` → `abc`, `a1c` |
| `\d` | Dígito [0-9] | `\d{3}` → `123` |
| `\w` | Alfanumérico + `_` | `\w+` → `hello_world` |
| `\s` | Whitespace | `kali\s+tools` |
| `*` | 0 ou mais | `cats*` → `cat`, `catsss` |
| `+` | 1 ou mais | `br+` → `br`, `brrrrr` |
| `?` | Opcional (0 ou 1) | `colou?r` → `color`, `colour` |
| `{n,m}` | Entre n e m vezes | `\d{2,4}` → `12`, `1234` |
| `^` | Início da linha | `^user:` |
| `$` | Fim da linha | `EOF$` |
| `[abc]` | a, b ou c | `[cfh]at` → `cat`, `fat` |
| `[^abc]` | Negação | `[^0-9]` → não-dígito |
| `(a\|b)` | a ou b | `nano\|vim` |
| `(\w+)` | Grupo de captura | `(\w+)@(\w+)\.com` |

---

## Requisitos

- Ubuntu 20.04+ (ou qualquer distro com Python 3.8+)
- Python 3.8+
- `python3-tk` (instalado automaticamente pelo `install.sh` se ausente)

Sem dependências externas — apenas biblioteca padrão do Python.

---

## Desinstalação

```bash
./uninstall.sh
```

Ou manualmente:

```bash
sudo rm /usr/local/bin/regextool
```

---

## Licença

MIT — livre para usar, modificar e distribuir.
