import shlex
import subprocess


def file_contains(file: str, text: str) -> bool:
    with open(file, "r") as f:
        contents = f.read()
    return contents == text


def run_cmd(cmd: str, stdin: str = None) -> str:
    """run a command return stdout"""
    if stdin is None:
        resp = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        out = resp.stdout
        return out
    else:
        resp = subprocess.run(
            cmd, capture_output=True, text=True, shell=True, input=stdin
        )
        out = resp.stdout
        return out
