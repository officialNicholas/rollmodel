"""Before/after listening demo of lobby -> locker -> lobby, mixed the way the game plays it (levels, offsets, fades)"""
import subprocess, numpy as np, soundfile as sf
SR = 48000
def dec(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()
def player(x, a, b):
    def at(pos, n):  # n samples from position pos (seconds), looping a..b
        out = np.zeros((2, n), np.float32); L = b - a
        for i in range(0, n, 4800):
            m = min(4800, n - i); p = pos + i / SR
            if p >= b: p = a + (p - a) % L
            j = int(round(p * SR)); seg = x[:, j:j + m]
            if seg.shape[1] < m:  # wraps inside this block
                k = seg.shape[1]; seg = np.concatenate([seg, x[:, int(round(a * SR)):int(round(a * SR)) + m - k]], axis=1)
            out[:, i:i + m] = seg
        return out
    return at
menu = dec('/home/claude/music/menu.mp3'); new = dec('spook_new.mp3'); old = dec('spook_old.mp3')
M = (6.928, 43.72223, 0.923 * 0.26)
def render(sp, S, X, curve, carry):
    pm, ps = player(menu, M[0], M[1]), player(sp, S[0], S[1])
    T1, T2, T3 = 9.0, 19.0, 29.0; n = int(T3 * SR); t = np.arange(n) / SR
    mpos = M[0] + t  # the lobby song from its loop start
    # the locker cut joins at T1 at the carried spot and stays on its own clock after that
    s_off = carry(M[0] + T1); spos = s_off + (t - T1)
    # back to the lobby at T2: the lobby song comes back in at the spot the locker cut has reached
    m_off2 = carry_back(S, s_off + (T2 - T1), carry)
    a = pm(M[0], n); b = ps(s_off, n); c = pm(m_off2, n)
    b = np.concatenate([np.zeros((2, int(T1 * SR)), np.float32), ps(s_off, n - int(T1 * SR))], axis=1)
    c = np.concatenate([np.zeros((2, int(T2 * SR)), np.float32), pm(m_off2, n - int(T2 * SR))], axis=1)
    def fade(t0, up):
        x = np.clip((t - t0) / X, 0, 1); return (np.sin(x * np.pi / 2) if up else np.cos(x * np.pi / 2)) if curve == 'power' else (x if up else 1 - x)
    ga = fade(T1, False) * M[2]; gb = fade(T1, True) * fade(T2, False) * S[2]; gc = fade(T2, True) * M[2]
    return a * ga + b * gb + c * gc
def carry_back(S, spos, carry): return carry.back(spos)
class NewCarry:
    def __call__(self, mp): return 1.0 + (mp - M[0]) % (M[1] - M[0])
    def back(self, sp): return M[0] + (sp - 1.0) % (M[1] - M[0])
class OldCarry:
    A, B = (6.928, 43.72223), (7.32, 46.21)
    def __call__(self, mp): return max(0, self.B[0] + (mp - self.A[0]) / (self.A[1] - self.A[0]) * (self.B[1] - self.B[0]))
    def back(self, sp): return max(0, self.A[0] + (sp - self.B[0]) / (self.B[1] - self.B[0]) * (self.A[1] - self.A[0]))
y_new = render(new, (1.0, 37.79423, 0.785 * 0.26), 1.4, 'power', NewCarry())
y_old = render(old, (7.32, 46.21, 0.795 * 0.26), 0.45, 'linear', OldCarry())
for nm, y in [('switch_after', y_new), ('switch_before', y_old)]:
    y = y / max(1e-9, np.abs(y).max()) * 0.89
    sf.write(nm + '.wav', y.T, SR); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', nm + '.wav', '-c:a', 'libmp3lame', '-b:a', '192k', nm + '.mp3'], check=True)
print('ok')
