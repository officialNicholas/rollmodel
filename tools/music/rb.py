"""Rubber Band (the system's librubberband 3, through its C API) as an offline time-stretcher with a key-frame map"""
import ctypes, numpy as np
lib = ctypes.CDLL('librubberband.so.2')
V = ctypes.c_void_p; U = ctypes.c_uint; FP = ctypes.POINTER(ctypes.c_float); FPP = ctypes.POINTER(FP)
lib.rubberband_new.restype = V; lib.rubberband_new.argtypes = [U, U, ctypes.c_int, ctypes.c_double, ctypes.c_double]
lib.rubberband_delete.argtypes = [V]
lib.rubberband_get_engine_version.argtypes = [V]; lib.rubberband_get_engine_version.restype = ctypes.c_int
lib.rubberband_set_expected_input_duration.argtypes = [V, U]
lib.rubberband_set_max_process_size.argtypes = [V, U]
lib.rubberband_set_key_frame_map.argtypes = [V, U, ctypes.POINTER(U), ctypes.POINTER(U)]
lib.rubberband_study.argtypes = [V, FPP, U, ctypes.c_int]
lib.rubberband_process.argtypes = [V, FPP, U, ctypes.c_int]
lib.rubberband_available.argtypes = [V]; lib.rubberband_available.restype = ctypes.c_int
lib.rubberband_retrieve.argtypes = [V, FPP, U]; lib.rubberband_retrieve.restype = U
lib.rubberband_get_start_delay.argtypes = [V]; lib.rubberband_get_start_delay.restype = U
OFFLINE, FINER, FASTER, CH_TOGETHER, PITCH_HQ = 0, 0x20000000, 0, 0x10000000, 0x02000000
def stretch(x, sr, ratio, kf_from=None, kf_to=None, finer=True, together=True, block=8192):
    """x: (channels, n) float32. ratio: output/input duration. kf_*: sample frames, input -> output"""
    x = np.ascontiguousarray(x, np.float32); ch, n = x.shape
    opts = OFFLINE | (FINER if finer else FASTER) | (CH_TOGETHER if together else 0) | PITCH_HQ
    st = lib.rubberband_new(sr, ch, opts, ratio, 1.0)
    eng = lib.rubberband_get_engine_version(st)
    lib.rubberband_set_expected_input_duration(st, n); lib.rubberband_set_max_process_size(st, block)
    def ptrs(a, i0, i1):
        arr = (FP * ch)(*[a[c, i0:i1].ctypes.data_as(FP) for c in range(ch)]); return arr
    chunks = [(i, min(n, i + block)) for i in range(0, n, block)]
    for i0, i1 in chunks: lib.rubberband_study(st, ptrs(x, i0, i1), i1 - i0, int(i1 == n))
    if kf_from is not None:
        f = (U * len(kf_from))(*[int(v) for v in kf_from]); t = (U * len(kf_to))(*[int(v) for v in kf_to]); lib.rubberband_set_key_frame_map(st, len(kf_from), f, t)
    out = [[] for _ in range(ch)]
    def drain():
        while True:
            av = lib.rubberband_available(st)
            if av <= 0: return av
            buf = np.zeros((ch, av), np.float32); got = lib.rubberband_retrieve(st, (FP * ch)(*[buf[c].ctypes.data_as(FP) for c in range(ch)]), av)
            for c in range(ch): out[c].append(buf[c, :got].copy())
    for i0, i1 in chunks:
        lib.rubberband_process(st, ptrs(x, i0, i1), i1 - i0, int(i1 == n)); drain()
    while drain() != -1: pass
    lib.rubberband_delete(st)
    return np.stack([np.concatenate(o) for o in out]), eng
