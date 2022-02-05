import shlex
import subprocess


def file_contains(file: str, text: str) -> bool:
    with open(file, "r") as f:
        contents = f.read()
    return contents == text


def run_cmd(cmd: str) -> str:
    """run a command return stdout"""
    resp = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print(resp)
    out = resp.stdout
    return out
