# Theming Guide

Standardisiertes Theming für alle Helper Scripts mit Catppuccin Mocha Farbpalette und Nerd Font Icons.

## Catppuccin Mocha Farbpalette (24-bit True Color)

```bash
# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'    # #bac2de - Subtext
readonly NC='\033[0m'                         # No Color
```

## Farbverwendung

- **RED** (`#f38ba8`) - Fehler und kritische Meldungen
- **GREEN** (`#a6e3a1`) - Erfolg und positive Meldungen
- **YELLOW** (`#f9e2af`) - Warnungen
- **BLUE** (`#89b4fa`) - Informationen und Highlights
- **MAUVE** (`#cba6f7`) - Headers und Tags
- **SAPPHIRE** (`#74c7ec`) - Erfolgs-Highlights
- **TEXT** (`#cdd6f4`) - Normaler Text
- **SUBTEXT** (`#bac2de`) - Sekundärer Text

## Nerd Font Icons

```bash
# Nerd Font Icons
readonly CHECK=""      # \uf00c - Erfolg
readonly CROSS=""      # \uf00d - Fehler
readonly WARN=""       # \uf071 - Warnung
readonly INFO=""       # \uf05a - Information
readonly SERVER=""     # \uf233 - Server
readonly DOCKER=""     # \uf308 - Docker
readonly CONTAINER=""  # \uf1b2 - Container
readonly CHART="󰈙"      # \uf200 - Chart/Statistik
readonly CLOCK="󰥔"      # \uf64f - Zeit/Uptime
readonly MEM="󰍛"        # \uf538 - Memory
readonly CPU="󰻠"        # \uf2db - CPU
readonly NET="󰈀"        # \uf6ff - Network
readonly LOG=""        # \uf15c - Log
readonly FILE=""       # \uf15b - File
readonly DATABASE=""   # \uf1c0 - Database
readonly PLAY=""       # \uf04b - Start/Play
readonly STOP=""       # \uf04d - Stop
readonly RESTART=""    # \uf01e - Restart
readonly STATUS=""     # \uf05a - Status
readonly ROCKET=""     # \uf135 - Deployment
readonly FOLDER=""     # \uf07c - Folder
readonly QUESTION=""   # \uf128 - Question/Prompt
readonly SEARCH=""     # \uf002 - Search
readonly HAMMER=""     # \uf6e3 - Build/Rebuild
```

## Standard Log-Funktionen

```bash
log_success() {
    echo -e "${GREEN}${CHECK}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1" >&2
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_info() {
    echo -e "${BLUE}${INFO}  ${NC}$1"
}
```

## Header/Tag Format

```bash
echo -e "${MAUVE}[script-name]${NC} ${ICON}  Beschreibung..."
```

**Beispiele:**
```bash
echo -e "${MAUVE}[start]${NC} ${DOCKER}  Starting container..."
echo -e "${MAUVE}[status]${NC} ${SERVER}  Checking status..."
echo -e "${MAUVE}[logs]${NC} ${LOG}  Checking logs..."
```

## Verwendung in Python Scripts

```python
# Catppuccin Mocha color palette (24-bit true color)
class Colors:
    RED = '\033[38;2;243;139;168m'        # #f38ba8 - Errors
    GREEN = '\033[38;2;166;227;161m'      # #a6e3a1 - Success
    YELLOW = '\033[38;2;249;226;175m'     # #f9e2af - Warnings
    BLUE = '\033[38;2;137;180;250m'       # #89b4fa - Info
    MAUVE = '\033[38;2;203;166;247m'      # #cba6f7 - Headers
    SAPPHIRE = '\033[38;2;116;199;236m'   # #74c7ec - Success highlights
    TEXT = '\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
    SUBTEXT = '\033[38;2;186;194;222m'    # #bac2de - Subtext
    NC = '\033[0m'                         # No Color

# Nerd Font Icons
CHECK = '\uf00c'   #
CROSS = '\uf00d'   #
WARN = '\uf071'    #
INFO = '\uf05a'    #

def log_success(msg: str):
    print(f"{Colors.GREEN}{CHECK}  {Colors.NC}{msg}")

def log_error(msg: str):
    print(f"{Colors.RED}{CROSS}  {Colors.NC}{msg}", file=sys.stderr)

def log_warn(msg: str):
    print(f"{Colors.YELLOW}{WARN}  {Colors.NC}{msg}")

def log_info(msg: str):
    print(f"{Colors.BLUE}{INFO}  {Colors.NC}{msg}")
```

## Output Design Guidelines

**WICHTIG: Halte Output CLEAN und SIMPEL**

### Was NICHT zu tun ist

- **KEINE Separator-Linien** wie `==================== Title ====================`
- **KEINE Unicode Emojis** (wie „", „", „") - nur Nerd Font Icons!
- **KEINE übermäßigen Leerzeilen** oder Whitespace
- **KEINE verbose Erklärungen** - kurz und präzise

### Korrekte Output-Formatierung

```bash
# Gut - Clean und simpel
echo -e "${GREEN}${CHECK}${NC}  No skip file - proceeding with CI/CD"
echo -e "${BLUE}${INFO}${NC}  Checking configuration..."
echo -e "${YELLOW}${WARN}${NC}  Skip file invalid - proceeding for security"

# Schlecht - Übertrieben und verbose
echo -e "${MAUVE}==================== Title ====================${NC}"
echo ""
echo -e "${BLUE}${INFO}${NC}  Detailed explanation of what we're doing..."
echo -e "${BLUE}${INFO}${NC}  More detailed information..."
echo ""
echo -e "${MAUVE}=================================================${NC}"
```

### Format-Regel

Alle Ausgaben folgen dem Format:
```
<COLOR><ICON><NC>  <Message>
```

- Ein Icon
- Zwei Leerzeichen nach dem Icon
- Kurze, aussagekräftige Nachricht
- Keine Punkt am Ende bei Einzeilern
- Keine zusätzlichen Dekorationen

## Best Practices

1. **Konsistenz**: Verwende immer die gleichen Farben für die gleichen Zwecke
2. **Icons**: Wähle passende Icons für den Kontext
3. **Error Handling**: Fehler immer nach stderr (`>&2`)
4. **Reset**: Verwende immer `${NC}` am Ende von farbigen Texten
5. **Headers**: Format `[script-name]` in MAUVE für alle Scripts
6. **Clean Output**: Keine separator Linien, keine Emojis, keine verbose Texte

## Terminal Requirements

- Terminal mit 24-bit True Color Support
- Nerd Font installiert (z.B. JetBrains Mono Nerd Font, Fira Code Nerd Font)

## Beispiel Script

```bash
#!/bin/bash
set -e
set -o pipefail

# Catppuccin Mocha color palette
readonly RED='\033[38;2;243;139;168m'
readonly GREEN='\033[38;2;166;227;161m'
readonly YELLOW='\033[38;2;249;226;175m'
readonly BLUE='\033[38;2;137;180;250m'
readonly MAUVE='\033[38;2;203;166;247m'
readonly NC='\033[0m'

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""

log_success() {
    echo -e "${GREEN}${CHECK}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1" >&2
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_info() {
    echo -e "${BLUE}${INFO}  ${NC}$1"
}

main() {
    echo -e "${MAUVE}[example]${NC} ${INFO}  Running example script..."
    echo ""

    log_info "Processing..."
    log_success "Operation completed successfully"
    log_warn "This is a warning"
    log_error "This is an error"

    echo ""
}

main "$@"
```

## Referenzen

- [Catppuccin Mocha Theme](https://github.com/catppuccin/catppuccin)
- [Nerd Fonts](https://www.nerdfonts.com/)
