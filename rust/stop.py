#!/usr/bin/env python3
"""
Stop Rust server
"""

import sys
import subprocess
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'utils'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)
from xdg_paths import get_pid_file  # noqa: E402


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from sys/env/.env file"""
    env_file = repo_root / 'sys' / 'env' / '.env'

    if not env_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {env_file}\n"
            f"Copy sys/env/.env.example to sys/env/.env and configure it."
        )

    config = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip('"').strip("'")
                config[key] = value

    # Validate required keys
    required_keys = ['SERVER_BINARY', 'DISPLAY_NAME']
    missing = [key for key in required_keys if key not in config]
    if missing:
        raise ValueError(f"Missing required config keys in .env: {', '.join(missing)}")

    return config


def is_running(pid: int) -> bool:
    """Check if process is running"""
    try:
        subprocess.run(['kill', '-0', str(pid)], check=True,
                       capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main execution"""
    config = load_env_config(REPO_ROOT)
    server_binary = config['SERVER_BINARY']
    display_name = config['DISPLAY_NAME']
    app_name = 'sysrat'

    # Get XDG-compliant PID file path
    pid_file = get_pid_file(app_name, config)

    # Handle relative paths from config
    if not pid_file.is_absolute():
        pid_file = REPO_ROOT / pid_file

    print()
    print(f"{Colors.MAUVE}[stop]{Colors.NC}   stopping sysrat...")
    print()

    # Check PID file
    server_stopped = False
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())

            if is_running(old_pid):
                log_info(f"stopping pid {old_pid}")
                subprocess.run(['kill', str(old_pid)], check=True,
                               capture_output=True)
                time.sleep(1)

                # Force kill if still running
                if is_running(old_pid):
                    log_warn("force killing")
                    subprocess.run(['kill', '-9', str(old_pid)],
                                   capture_output=True)
                    time.sleep(1)

                if not is_running(old_pid):
                    server_stopped = True
                else:
                    log_error("failed to stop")
                    sys.exit(1)
            else:
                log_warn("pid file exists but process not running")

            pid_file.unlink()

        except (ValueError, IOError) as e:
            log_error(f"error reading pid file: {e}")
            pid_file.unlink()
    else:
        # Try to find and kill by name
        try:
            result = subprocess.run(['pgrep', '-f', server_binary],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                log_info(f"found {len(pids)} server(s), stopping...")
                subprocess.run(['pkill', '-f', server_binary],
                               capture_output=True)
                time.sleep(1)
                server_stopped = True
            else:
                log_warn("no running server found")
                print()
                sys.exit(0)
        except FileNotFoundError:
            log_warn("no running server found")
            print()
            sys.exit(0)

    if server_stopped:
        print()
        log_success("sysrat stopped")
    else:
        log_warn("server may still be running")
        log_info(f"check with: ps aux | grep {server_binary}")

    print()
    print(f" {Colors.RED}{Icons.STOP}{Colors.NC}  done")
    print()


if __name__ == '__main__':
    main()
