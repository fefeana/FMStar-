import pty
import os
import re
import sys
import time
import subprocess

def main():
    master, slave = pty.openpty()
    proc = subprocess.Popen(
        ['gh', 'auth', 'login', '--web', '-p', 'https', '-s', 'repo,workflow'],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True
    )
    os.close(slave)

    buffer = ""
    code_found = False

    while True:
        try:
            data = os.read(master, 1024)
            if not data:
                break
            text = data.decode('utf-8', errors='ignore')
            buffer += text
            sys.stdout.write(text)
            sys.stdout.flush()

            if not code_found:
                m = re.search(r'([A-Z0-9]{4}-[A-Z0-9]{4})', buffer)
                if m:
                    code = m.group(1)
                    with open('device_code.txt', 'w') as f:
                        f.write(code)
                    code_found = True
                    # Send newline to trigger the wait
                    os.write(master, b'\n')

            if proc.poll() is not None:
                break
        except Exception:
            break

    if proc.returncode == 0:
        subprocess.run(['gh', 'auth', 'setup-git'], check=False)
        res = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
        with open('push_result.txt', 'w') as f:
            f.write("SUCCESS:\n" + res.stdout + "\n" + res.stderr)
    else:
        with open('push_result.txt', 'w') as f:
            f.write(f"FAILED (code {proc.returncode}):\n" + buffer)

if __name__ == '__main__':
    main()
