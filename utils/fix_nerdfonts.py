#!/usr/bin/env python3
"""
Nerd Font Icon Fixer for Shell Scripts
Replaces empty icon strings with correct Nerd Font Unicode characters
"""

import sys
import re
from pathlib import Path

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

# Nerd Font Icon mappings (Unicode codepoints)
NERD_FONTS = {
    'CHECK': '\uf00c',      #
    'CROSS': '\uf00d',      #
    'WARN': '\uf071',       #
    'INFO': '\uf05a',       #
    'SERVER': '\uf233',     # 󰒋
    'DOCKER': '\uf308',     #
    'CONTAINER': '\uf1b2',  #
    'CHART': '\uf200',      # 󰈙
    'CLOCK': '\uf64f',      # 󰥔
    'MEM': '\uf538',        # 󰍛
    'CPU': '\uf2db',        # 󰻠
    'NET': '\uf6ff',        # 󰈀
    'LOG': '\uf15c',        #
    'FILE': '\uf15b',       #
    'DATABASE': '\uf1c0',   #
    'PLAY': '\uf04b',       #
    'STOP': '\uf04d',       #
    'RESTART': '\uf01e',    #
    'STATUS': '\uf05a',     #
}

def log_success(msg: str):
    """Log success message with icon"""
    print(f"{Colors.GREEN}{CHECK}  {Colors.NC}{msg}")

def log_error(msg: str):
    """Log error message with icon"""
    print(f"{Colors.RED}{CROSS}  {Colors.NC}{msg}", file=sys.stderr)

def log_warn(msg: str):
    """Log warning message with icon"""
    print(f"{Colors.YELLOW}{WARN}  {Colors.NC}{msg}")

def log_info(msg: str):
    """Log info message with icon"""
    print(f"{Colors.BLUE}{INFO}  {Colors.NC}{msg}")

def get_patterns_for_filetype(filepath: Path, icon_name: str) -> list:
    """
    Get appropriate regex patterns based on file extension

    Args:
        filepath: Path to the file
        icon_name: Name of the icon (e.g., 'CHECK', 'WARN')

    Returns:
        List of (pattern, description) tuples to try in order
    """
    suffix = filepath.suffix.lower()
    patterns = []

    if suffix == '.sh':
        # Shell scripts: readonly ICON=""
        patterns.append((
            rf'(readonly\s+{icon_name}=)""\s*$',
            'shell readonly'
        ))
    elif suffix in ['.yml', '.yaml']:
        # YAML files: ICON="" (no readonly, used in GitHub Actions)
        patterns.append((
            rf'(\s+{icon_name}=)""\s*$',
            'yaml assignment'
        ))
    elif suffix == '.py':
        # Python: ICON = "" (with spaces around =)
        patterns.append((
            rf'({icon_name}\s*=\s*)""\s*$',
            'python assignment'
        ))
    elif suffix == '.md':
        # Markdown: Could have various patterns
        # - Code blocks with readonly ICON=""
        # - Inline code `ICON=""`
        patterns.append((
            rf'(readonly\s+{icon_name}=)""\s*$',
            'markdown shell code'
        ))
        patterns.append((
            rf'(`{icon_name}=)""`',
            'markdown inline code'
        ))
    else:
        # Generic: try common patterns
        patterns.append((
            rf'(readonly\s+{icon_name}=)""\s*$',
            'generic readonly'
        ))
        patterns.append((
            rf'({icon_name}=)""\s*$',
            'generic assignment'
        ))

    return patterns

def fix_icons_in_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Fix Nerd Font icons in a file based on file type

    Args:
        filepath: Path to the file
        dry_run: If True, only show what would be changed

    Returns:
        True if changes were made, False otherwise
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        changes_made = False

        # Pattern to match: readonly ICON_NAME=""
        # We'll replace the empty string with the actual icon
        for icon_name, icon_char in NERD_FONTS.items():
            # Match patterns like: readonly CHECK=""
            # Pattern 1: With readonly (shell scripts)
            pattern1 = rf'(readonly\s+{icon_name}=)""\s*$'
            # Pattern 2: Without readonly (YAML, other formats)
            pattern2 = rf'({icon_name}=)""\s*$'
            replacement = rf'\1"{icon_char}"'

            # Try pattern 1 first (with readonly)
            new_content = re.sub(pattern1, replacement, content, flags=re.MULTILINE)

            # If no changes, try pattern 2 (without readonly)
            if new_content == content:
                new_content = re.sub(pattern2, replacement, content, flags=re.MULTILINE)

            if new_content != content:
                changes_made = True
                if not dry_run:
                    log_success(f"Fixed {icon_name} in {filepath.name}")
                else:
                    log_warn(f"Would fix {icon_name} in {filepath.name}")
                content = new_content

        if changes_made and not dry_run:
            filepath.write_text(content, encoding='utf-8')
            return True

        return changes_made

    except Exception as e:
        log_error(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix Nerd Font icons in shell scripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Fix all .sh files in current directory
  python3 fix_nerdfonts.py

  # Fix multiple file types
  python3 fix_nerdfonts.py sh md py

  # Fix files in a specific directory
  python3 fix_nerdfonts.py --path /path/to/scripts

  # Fix files recursively
  python3 fix_nerdfonts.py --recursive --path /path/to/scripts

  # Fix a specific file
  python3 fix_nerdfonts.py --path /path/to/script.sh
        '''
    )

    parser.add_argument(
        'filetypes',
        nargs='*',
        help='File types to fix (e.g., sh md py txt). Default: sh'
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        help='Path to file or directory to process. Default: current directory'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    args = parser.parse_args()

    # Determine base path
    base_path = Path(args.path) if args.path else Path('.')

    # Determine which files to process
    files = []

    # Check if base_path is a specific file
    if base_path.is_file():
        files.append(base_path)
    elif base_path.is_dir():
        if not args.filetypes:
            # Default: scan .sh files
            pattern = '**/*.sh' if args.recursive else '*.sh'
            files = list(base_path.glob(pattern))
        else:
            # Check if arguments are files or file types
            for arg in args.filetypes:
                arg_path = Path(arg)
                if arg_path.exists() and arg_path.is_file():
                    # It's a specific file
                    files.append(arg_path)
                else:
                    # It's a file type - scan for files with this extension
                    ext = arg.lstrip('*.')
                    pattern = f'**/*.{ext}' if args.recursive else f'*.{ext}'
                    files.extend(list(base_path.glob(pattern)))
    else:
        log_error(f"Path not found: {base_path}")
        return 1

    if not files:
        if args.filetypes:
            log_error(f"No files found matching types: {', '.join(args.filetypes)}")
        else:
            log_error("No files found!")
        return 1

    # Header
    tag = f"{Colors.MAUVE}[fix-nerdfonts]{Colors.NC}"
    print(f"{tag} Fixing Nerd Font icons...")
    print()

    total_files = 0
    fixed_files = 0

    for filepath in sorted(files):
        if not filepath.exists():
            log_error(f"File not found: {filepath}")
            continue

        if not filepath.is_file():
            log_error(f"Not a file: {filepath}")
            continue

        total_files += 1
        print(f"{Colors.BLUE}Processing{Colors.NC} {filepath.name}...")

        if fix_icons_in_file(filepath, dry_run=False):
            fixed_files += 1
        else:
            log_info(f"No changes needed for {filepath.name}")

        print()

    # Summary
    print(f"{Colors.GREEN}Summary:{Colors.NC}")
    print()
    print(f"{Colors.BLUE}  Total files:     {Colors.NC}{total_files}")
    print(f"{Colors.GREEN}  Files fixed:     {Colors.NC}{fixed_files}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
