import os, pty, sys, select, json, fcntl, termios, struct, signal
cols, rows, cwd = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
cmd = sys.argv[4:]
pid, fd = pty.fork()
if pid == 0:
    os.chdir(cwd)
    os.environ['TERM'] = 'xterm-256color'
    os.environ['COLORTERM'] = 'truecolor'
    os.execvp(cmd[0], cmd)
def rs(c, r):
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', r, c, 0, 0))
rs(cols, rows)
buf = b''
while True:
    try:
        r, _, _ = select.select([fd, 0], [], [])
    except InterruptedError:
        continue
    if fd in r:
        try:
            d = os.read(fd, 65536)
        except OSError:
            break
        if not d:
            break
        os.write(1, d)
    if 0 in r:
        d = os.read(0, 65536)
        if not d:
            try: os.kill(pid, signal.SIGHUP)
            except OSError: pass
            break
        buf += d
        while b'\n' in buf:
            l, buf = buf.split(b'\n', 1)
            try: m = json.loads(l)
            except ValueError: continue
            if 'd' in m: os.write(fd, m['d'].encode())
            elif 'r' in m: rs(*m['r'])
try: os.waitpid(pid, 0)
except OSError: pass
