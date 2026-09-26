"""
Small, dependency-free helpers used across the app. Kept as plain
functions (not classes) because they carry no state — they're
already trivial to test and reuse as-is.
"""

import ctypes
import os
import socket
import subprocess
import sys


def is_admin():

    try:
        return bool(
            ctypes.windll.shell32.IsUserAnAdmin()
        )
    except Exception:
        return False


def relaunch_as_admin():
    """
    Re-launches the current script with a UAC elevation prompt.
    Returns True if Windows actually launched the elevated process,
    False if the user declined the UAC prompt or it otherwise failed
    (ShellExecuteW returns a value <= 32 on failure — it doesn't
    raise). Does not exit the current process itself.
    """

    script = os.path.abspath(
        sys.argv[0]
    )

    params = " ".join(
        f'"{arg}"'
        for arg in sys.argv[1:]
    )

    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        f'"{script}" {params}',
        None,
        1
    )

    return int(result) > 32


def run_command(command, timeout=15):

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return (
            result.returncode,
            result.stdout,
            result.stderr
        )

    except Exception as e:
        return (
            -1,
            "",
            str(e)
        )


def normalize_ip(ip):

    ip = ip.strip()

    if ip.startswith("("):
        ip = ip[1:]

    if ip.endswith(")"):
        ip = ip[:-1]

    return ip


def is_ipv4(ip):

    try:
        socket.inet_aton(ip)

        parts = ip.split(".")

        return (
            len(parts) == 4
            and all(
                0 <= int(x) <= 255
                for x in parts
            )
        )

    except Exception:
        return False
