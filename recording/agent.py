#!/usr/bin/env python3
# Session recorder for the Guide. Runs on tty1 of cyborg as cybsec.
import json, os, re, shutil, struct, subprocess, sys, time, zlib, glob
S = '/mnt/share'
CWD = os.path.expanduser('~')
HOME = CWD
ENVF = HOME + '/.recorder_env'
COLS, ROWS = shutil.get_terminal_size((160, 45))
def w(s):
    sys.stdout.write(s); sys.stdout.flush()
def tilde(p):
    return '~' + p[len(HOME):] if p == HOME or p.startswith(HOME + '/') else p
def prompt(c):
    return f'\033[1;32mcybsec@cyborg\033[0m:\033[1;34m{tilde(c)}\033[0m$ '
def plain_prompt(c):
    return f'cybsec@cyborg:{tilde(c)}$ '
def wrap(line):
    out = []
    while len(line) > COLS - 1:
        out.append(line[:COLS - 1]); line = line[COLS - 1:]
    out.append(line)
    return out
def png(path):
    size = open('/sys/class/graphics/fb0/virtual_size').read().strip().split(',')
    W, H = int(size[0]), int(size[1])
    stride = int(open('/sys/class/graphics/fb0/stride').read())
    d = subprocess.run(['sudo', 'cat', '/dev/fb0'], stdout=subprocess.PIPE).stdout
    rows = bytearray()
    for y in range(H):
        r = d[y * stride:y * stride + W * 4]
        px = bytearray(W * 3); px[0::3] = r[2::4]; px[1::3] = r[1::4]; px[2::3] = r[0::4]
        rows += b'\0' + px
    def ch(t, b):
        c = struct.pack('>I', len(b)) + t + b
        return c + struct.pack('>I', zlib.crc32(t + b))
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(bytes(rows), 6)) + ch(b'IEND', b''))
def run(job):
    global CWD
    i, cmd = job['id'], job['cmd']
    before = CWD
    w('\033[2J\033[H' + prompt(CWD) + cmd + '\n')
    t0 = time.time()
    script = (f'[ -f {ENVF} ] && . {ENVF}\ncd "{CWD}"\n' + cmd + '\n__rc=$?\npwd > /tmp/.rec_cwd\nexit $__rc\n')
    p = subprocess.Popen(['bash', '-l', '-c', script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env={**os.environ, 'TERM': 'linux', 'LC_ALL': 'C.UTF-8'})
    buf = b''
    for chunk in iter(lambda: p.stdout.read1(4096), b''):
        buf += chunk; sys.stdout.buffer.write(chunk); sys.stdout.flush()
    rc = p.wait(); secs = round(time.time() - t0, 1)
    try: CWD = open('/tmp/.rec_cwd').read().strip() or CWD
    except OSError: pass
    out = buf.decode('utf-8', 'replace')
    json.dump({'id': i, 'cmd': cmd, 'cwd': before, 'after': CWD, 'out': out, 'rc': rc, 'secs': secs, 'ts': t0}, open(f'{S}/rec.d/{i}.json', 'w'), indent=0)
    # screenshots: show the whole result, one screen at a time
    body = []
    for l in (cmd + '\n' + out.rstrip('\n')).split('\n'):
        body += wrap(l.replace('\t', '    ').replace('\r', ''))
    n = ROWS - 1
    pages = [body[k:k + n] for k in range(0, len(body), n)] or [[]]
    for k, pg in enumerate(pages, 1):
        t = '\033[2J\033[H'
        if k == 1:
            t += prompt(before) + pg[0][:COLS].replace('', '') + '\n' + '\n'.join(pg[1:])
        else:
            t += '\n'.join(pg)
        w(t.rstrip('\n'))
        time.sleep(0.25)
        png(f'{S}/shots/{i}_{k}.png')
    w('\n' + prompt(CWD))
def main():
    os.makedirs(S + '/rec.d', exist_ok=True)
    w(f'recorder up {COLS}x{ROWS}\n')
    open(S + '/agent.up', 'w').write(f'{COLS}x{ROWS} {time.ctime()}\n')
    while True:
        js = sorted(glob.glob(S + '/q/*.json'))
        if not js:
            if os.path.exists(S + '/stop'): return
            time.sleep(1); continue
        f = js[0]
        job = json.load(open(f))
        os.replace(f, S + '/done/' + os.path.basename(f))
        try:
            run(job)
        except Exception as e:
            open(S + '/agent.err', 'a').write(repr(e) + '\n')
main()
