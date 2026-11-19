#!/bin/bash
rm -f /tmp/gh_auth.log /tmp/gh_status.log /tmp/gh_code.txt

echo "Starting gh auth login..."
# Start gh auth login in background with stdin ready
python3 -c "
import pty, os, re, time, subprocess

master, slave = pty.openpty()
proc = subprocess.Popen(
    ['gh', 'auth', 'login', '--web', '-p', 'https', '-s', 'repo,workflow'],
    stdin=slave,
    stdout=slave,
    stderr=slave,
    close_fds=True
)
os.close(slave)

output = b''
code = None
url = 'https://github.com/login/device'

# Read initial prompt
for _ in range(50):
    try:
        chunk = os.read(master, 1024)
        if not chunk:
            break
        output += chunk
        text = output.decode('utf-8', errors='ignore')
        # Check for user code
        m = re.search(r'([A-Z0-9]{4}-[A-Z0-9]{4})', text)
        if m:
            code = m.group(1)
            with open('/tmp/gh_code.txt', 'w') as f:
                f.write(code)
            # Press enter to acknowledge browser prompt
            os.write(master, b'\n')
            break
    except Exception:
        time.sleep(0.1)

# Keep polling in background until proc completes
while proc.poll() is None:
    try:
        chunk = os.read(master, 1024)
        if chunk:
            output += chunk
    except Exception:
        time.sleep(1)

with open('/tmp/gh_auth.log', 'w') as f:
    f.write(output.decode('utf-8', errors='ignore'))

if proc.returncode == 0:
    # Setup git credentials and push
    subprocess.run(['gh', 'auth', 'setup-git'], check=False)
    push_res = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
    with open('/tmp/gh_status.log', 'w') as f:
        f.write('SUCCESS:\n' + push_res.stdout + '\n' + push_res.stderr)
else:
    with open('/tmp/gh_status.log', 'w') as f:
        f.write('FAILED:\n' + output.decode('utf-8', errors='ignore'))
" &
