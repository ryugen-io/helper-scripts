#!/usr/bin/env python3
"""
Interactive script to generate custom skip file hashes for Claude CI/CD workflows.
Uses Catppuccin Mocha theming for consistent visual output.
"""

import sys
import hashlib
import secrets
import os

# Add theme directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '.sys', 'theme'))
from theme import Colors, Icons, log_success, log_error, log_warn, log_info, log_header

def calculate_hash(content: str) -> str:
    """Calculate SHA256 hash of content."""
    return hashlib.sha256(content.encode()).hexdigest()

def generate_random_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(32)

def print_menu():
    """Display the main menu."""
    log_header(f"\n{Icons.ROCKET}  Skip File Hash Generator")
    print(f"\n{Colors.TEXT}Select a skip file to customize:{Colors.NC}\n")
    print(f"  {Colors.SAPPHIRE}1.{Colors.NC} {Colors.TEXT}.skip.all{Colors.NC}           {Colors.SUBTEXT}(skip all workflows){Colors.NC}")
    print(f"  {Colors.SAPPHIRE}2.{Colors.NC} {Colors.TEXT}.skip.claude{Colors.NC}        {Colors.SUBTEXT}(skip @claude comments){Colors.NC}")
    print(f"  {Colors.SAPPHIRE}3.{Colors.NC} {Colors.TEXT}.skip.claude-review{Colors.NC}  {Colors.SUBTEXT}(skip automatic reviews){Colors.NC}")
    print(f"  {Colors.SAPPHIRE}4.{Colors.NC} {Colors.TEXT}.skip.update-readme{Colors.NC}  {Colors.SUBTEXT}(skip README updates){Colors.NC}")
    print(f"  {Colors.RED}5.{Colors.NC} {Colors.TEXT}Exit{Colors.NC}\n")

def get_skip_file_info(choice: str) -> tuple:
    """Return (filename, secret_name, description) for a choice."""
    mapping = {
        '1': ('.skip.all', 'SKIP_FILE_HASH_ALL', 'all workflows'),
        '2': ('.skip.claude', 'SKIP_FILE_HASH_CLAUDE', '@claude comments'),
        '3': ('.skip.claude-review', 'SKIP_FILE_HASH_CLAUDE_REVIEW', 'automatic code reviews'),
        '4': ('.skip.update-readme', 'SKIP_FILE_HASH_UPDATE_README', 'README updates'),
    }
    return mapping.get(choice)

def main():
    """Main interactive flow."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    while True:
        print_menu()

        choice = input(f"{Colors.MAUVE}Enter your choice (1-5):{Colors.NC} ").strip()

        if choice == '5':
            log_info("Exiting...")
            sys.exit(0)

        skip_info = get_skip_file_info(choice)
        if not skip_info:
            log_error("Invalid choice! Please select 1-5.")
            continue

        filename, secret_name, description = skip_info
        filepath = os.path.join(script_dir, filename)

        log_header(f"\n{Icons.HAMMER}  Customizing {filename}")
        log_info(f"This will skip: {description}")

        # Ask for content type
        print(f"\n{Colors.TEXT}How do you want to generate the content?{Colors.NC}\n")
        print(f"  {Colors.SAPPHIRE}1.{Colors.NC} {Colors.TEXT}Enter custom text{Colors.NC}")
        print(f"  {Colors.SAPPHIRE}2.{Colors.NC} {Colors.TEXT}Generate random secure token{Colors.NC} {Colors.SUBTEXT}(recommended){Colors.NC}\n")

        content_choice = input(f"{Colors.MAUVE}Enter your choice (1-2):{Colors.NC} ").strip()

        if content_choice == '1':
            custom_content = input(f"\n{Colors.MAUVE}Enter your custom content:{Colors.NC} ").strip()
            if not custom_content:
                log_error("Content cannot be empty!")
                continue
        elif content_choice == '2':
            custom_content = generate_random_token()
            log_success(f"Generated random token: {Colors.YELLOW}{custom_content}{Colors.NC}")
        else:
            log_error("Invalid choice!")
            continue

        # Calculate hash
        content_hash = calculate_hash(custom_content)

        # Write skip file
        try:
            with open(filepath, 'w') as f:
                f.write(custom_content)
            log_success(f"Skip file created: {filepath}")
        except Exception as e:
            log_error(f"Failed to write file: {e}")
            continue

        # Display results
        print(f"\n{Colors.MAUVE}{'='*70}{Colors.NC}")
        log_header(f"{Icons.CHECK}  Configuration Complete!")
        print(f"{Colors.MAUVE}{'='*70}{Colors.NC}\n")

        print(f"{Colors.TEXT}File created:{Colors.NC}        {Colors.SAPPHIRE}{filepath}{Colors.NC}")
        print(f"{Colors.TEXT}SHA256 Hash:{Colors.NC}        {Colors.YELLOW}{content_hash}{Colors.NC}\n")

        log_header(f"{Icons.INFO}  Next Steps:")
        print(f"\n{Colors.TEXT}1. Add this hash as a GitHub Secret:{Colors.NC}\n")
        print(f"   {Colors.SUBTEXT}Go to: Settings > Secrets and variables > Actions > New repository secret{Colors.NC}")
        print(f"   {Colors.TEXT}Name:{Colors.NC}  {Colors.GREEN}{secret_name}{Colors.NC}")
        print(f"   {Colors.TEXT}Value:{Colors.NC} {Colors.YELLOW}{content_hash}{Colors.NC}\n")

        print(f"{Colors.TEXT}2. Commit and push the skip file:{Colors.NC}\n")
        print(f"   {Colors.SUBTEXT}git add {filepath}{Colors.NC}")
        print(f"   {Colors.SUBTEXT}git commit -m \"feat: Add custom skip for {description}\"{Colors.NC}")
        print(f"   {Colors.SUBTEXT}git push{Colors.NC}\n")

        log_warn(f"The workflow will be SKIPPED once you push this file AND set the GitHub Secret!")

        print(f"\n{Colors.MAUVE}{'='*70}{Colors.NC}\n")

        # Ask if user wants to continue
        another = input(f"{Colors.MAUVE}Generate another skip file? (y/n):{Colors.NC} ").strip().lower()
        if another != 'y':
            log_success("Done! Have a great day!")
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log_info("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        sys.exit(1)
