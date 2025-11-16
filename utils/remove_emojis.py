#!/usr/bin/env python3
"""
Remove Unicode Emojis from Files
Removes Unicode emoji characters while preserving Nerd Font icons
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

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
CLEAN = '\uf0c2'   #

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

def remove_emojis(text: str) -> str:
    """
    Remove Unicode emojis while preserving Nerd Font icons

    Nerd Font icons are in Private Use Area (U+E000-U+F8FF, U+F0000-U+FFFFD)
    and are NOT removed.

    Args:
        text: Input text containing emojis

    Returns:
        Text with emojis removed
    """
    # Emoji ranges to remove (preserves Nerd Font PUA ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001FAF8"  # Emoji & Pictographs (ALL emoji blocks)
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA70-\U0001FAF8"  # Extended Pictographs
        "\U00002600-\U000026FF"  # Miscellaneous Symbols (☁️, ⚡, ⌚, etc.)
        "\U00002700-\U000027BF"  # Dingbats (✨, ✳, ✴, ❌, etc.)
        "\U00002300-\U000023FF"  # Miscellaneous Technical
        "\U00002000-\U0000206F"  # General Punctuation (includes ZWJ)
        "\U000020A0-\U000020CF"  # Currency Symbols
        "\U00002100-\U0000214F"  # Letterlike Symbols
        "\U00002190-\U000021FF"  # Arrows
        "\U00002200-\U000022FF"  # Mathematical Operators
        "\U000025A0-\U000025FF"  # Geometric Shapes
        "\U00002900-\U0000297F"  # Supplemental Arrows-B
        "\U00002980-\U000029FF"  # Miscellaneous Mathematical Symbols-B
        "\U00002A00-\U00002AFF"  # Supplemental Mathematical Operators
        "\U00002B00-\U00002BFF"  # Miscellaneous Symbols and Arrows
        "\U00003000-\U0000303F"  # CJK Symbols and Punctuation
        "\U0001F1E6-\U0001F1FF"  # Regional Indicators (flags)
        "\U0000FE00-\U0000FE0F"  # Variation Selectors
        "\U0000200D"             # Zero Width Joiner
        "]+",
        flags=re.UNICODE
    )

    return emoji_pattern.sub('', text)

def remove_emojis_from_file(filepath: Path, keep_backup: bool = True) -> Tuple[bool, int]:
    """
    Remove emojis from a file

    Args:
        filepath: Path to the file
        keep_backup: Whether to keep backup file

    Returns:
        Tuple of (changed, emoji_count)
    """
    try:
        # Read file
        original_content = filepath.read_text(encoding='utf-8')

        # Remove emojis
        new_content = remove_emojis(original_content)

        # Check if changed
        if original_content == new_content:
            return False, 0

        # Count removed emojis (approximate)
        emoji_count = len(original_content) - len(new_content)

        # Create backup if requested
        if keep_backup:
            backup_path = filepath.with_suffix(filepath.suffix + '.emoji-backup')
            backup_path.write_text(original_content, encoding='utf-8')

        # Write cleaned content
        filepath.write_text(new_content, encoding='utf-8')

        return True, emoji_count

    except Exception as e:
        log_error(f"Error processing {filepath.name}: {e}")
        return False, 0

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Remove Unicode emojis from files while preserving Nerd Font icons',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Remove emojis from all files in current directory
  python3 remove_emojis.py

  # Remove emojis from specific directory
  python3 remove_emojis.py --path /path/to/scripts

  # Process specific file types
  python3 remove_emojis.py --types sh py md

  # Remove emojis recursively
  python3 remove_emojis.py --recursive

  # Don't keep backups
  python3 remove_emojis.py --no-backup
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to process (default: current directory)'
    )

    parser.add_argument(
        '-t', '--types',
        nargs='+',
        default=['sh', 'py', 'md', 'yml', 'yaml', 'txt'],
        help='File extensions to process (default: sh py md yml yaml txt)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )

    args = parser.parse_args()

    # Determine base path
    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    # Collect files
    files = []

    if base_path.is_file():
        files.append(base_path)
    elif base_path.is_dir():
        for ext in args.types:
            ext = ext.lstrip('*.')
            pattern = f'**/*.{ext}' if args.recursive else f'*.{ext}'
            files.extend(base_path.glob(pattern))
    else:
        log_error(f"Invalid path: {base_path}")
        return 1

    if not files:
        log_error(f"No files found matching types: {', '.join(args.types)}")
        return 1

    # Header
    tag = f"{Colors.MAUVE}[remove-emojis]{Colors.NC}"
    print(f"\n{tag} {CLEAN}  Removing Unicode emojis from files...\n")

    log_info(f"Processing {len(files)} file(s)")
    if not args.no_backup:
        log_info("Backups will be created with .emoji-backup extension")
    print()

    # Process files
    cleaned_count = 0
    unchanged_count = 0
    total_emojis = 0

    for filepath in sorted(files):
        changed, emoji_count = remove_emojis_from_file(
            filepath,
            keep_backup=not args.no_backup
        )

        if changed:
            cleaned_count += 1
            total_emojis += emoji_count
            log_success(f"Cleaned {filepath.name} (removed ~{emoji_count} chars)")
            if not args.no_backup:
                print(f"  {Colors.SUBTEXT}Backup: {filepath.name}.emoji-backup{Colors.NC}")
        else:
            unchanged_count += 1
            print(f"  {Colors.TEXT}{filepath.name}{Colors.NC} {Colors.SUBTEXT}(no emojis){Colors.NC}")

    # Summary
    print(f"\n{Colors.GREEN}Summary:{Colors.NC}\n")
    print(f"{Colors.BLUE}  Total files:     {Colors.NC}{len(files)}")
    print(f"{Colors.GREEN}  Cleaned:         {Colors.NC}{cleaned_count}")
    print(f"{Colors.TEXT}  No emojis:       {Colors.NC}{unchanged_count}")
    print(f"{Colors.SAPPHIRE}  Chars removed:   {Colors.NC}~{total_emojis}")
    print()

    if cleaned_count > 0:
        log_success("Emoji removal complete!")
        if not args.no_backup:
            log_warn("Review changes before deleting .emoji-backup files!")
    else:
        log_success("No emojis found!")

    return 0

if __name__ == '__main__':
    sys.exit(main())
