import subprocess

from config.settings import CPP_STANDARD


def run_cppcheck_analysis(file_path):
    command = [
        "cppcheck",
        "--enable=all",
        f"--std={CPP_STANDARD}",
        str(file_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError:
        return "cppcheck unavailable: executable not found on PATH."
    except subprocess.TimeoutExpired:
        return "cppcheck failed: analysis timed out after 30 seconds."

    messages = []
    for stream in (result.stderr, result.stdout):
        for line in stream.splitlines():
            if "error:" in line or "warning:" in line or "style:" in line:
                messages.append(line)

    return "\n".join(messages)
