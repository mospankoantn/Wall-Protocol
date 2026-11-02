"""Deterministic procedural audio for Wall Protocol 1.3 (numpy + scipy, no samples, no downloads).

Writes 44.1 kHz 16-bit WAV files into sounds/<name>/<name>.wav, updates each GameMaker
sound .yy (duration / channel format) and registers new sounds in `Wall Protocol.yyp`.
Safe to re-run: output is deterministic and registration is idempotent.

    python tools/build_audio.py            # everything
    python tools/build_audio.py --report   # also print level / loop-seam statistics

Sound effects are mono. The two music layers are stereo and loop sample-accurately:
every tail is wrapped around the loop point (circular reverb), constant tones use whole
cycles and noise is cross-faded, so there is no click or gap when the loop restarts.
"""
from pathlib import Path
import json, re, sys, wave
import numpy as np
from scipy import signal
from scipy.fft import rfft, irfft

ROOT = Path(__file__).resolve().parents[1]
SR = 44100
rng = np.random.default_rng(130)          # fixed seed -> identical files on every run


# ----------------------------------------------------------------------------- DSP
def tt(d): return np.arange(int(round(SR * d))) / SR
def midi(n): return 440.0 * 2 ** ((np.asarray(n, dtype=float) - 69) / 12)
def noise(d): return rng.standard_normal(int(round(SR * d)))
def _sos(kind, fc, order): return signal.butter(order, fc, btype=kind, fs=SR, output='sos')
def lp(x, fc, order=2): return signal.sosfilt(_sos('low', min(fc, SR * .45), order), x, axis=0)
def hp(x, fc, order=2): return signal.sosfilt(_sos('high', fc, order), x, axis=0)
def bp(x, lo, hi, order=2): return signal.sosfilt(_sos('band', [lo, min(hi, SR * .45)], order), x, axis=0)
def env(d, a=.003, tau=.1):
    t = tt(d); return np.minimum(t / max(a, 1e-5), 1.0) * np.exp(-t / tau)
def sweep_phase(f0, f1, d, curve=3.0):
    """Exponentially settling pitch glide from f0 to f1."""
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t * curve / d)
    return 2 * np.pi * np.cumsum(f) / SR
def saw(f, d, detune_cents=0.0, phase=0.0):
    t = tt(d); return signal.sawtooth(2 * np.pi * f * 2 ** (detune_cents / 1200) * t + phase)
def bell(f, d, ratio=3.51, index=3.0, tau=.5, a=.002):
    """Two-operator FM bell with a decaying modulation index (struck metal / glass)."""
    t = tt(d); idx = index * np.exp(-t / (tau * .6))
    return fade_out(np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t)) * env(d, a, tau), .03)
def pluck(f, d, g=.996, soften=.45):
    """Karplus-Strong string."""
    n = int(SR * d); N = max(2, int(round(SR / f)))
    x = np.zeros(n); burst = lp(rng.uniform(-1, 1, N), 1500 + soften * 6000, 1)
    x[:N] = burst
    a = np.zeros(N + 2); a[0] = 1; a[N] = -g / 2; a[N + 1] = -g / 2
    return fade_out(signal.lfilter([1.0], a, x), .05)
def tv_lp(x, curve, cutoffs=(180, 280, 450, 700, 1100, 1700, 2600, 4000, 6000)):
    """Time-varying low-pass: cross-fade between fixed filters following `curve` (Hz per sample)."""
    ys = np.stack([lp(x, c, 2) for c in cutoffs]); lc = np.log(np.asarray(cutoffs, float))
    pos = np.interp(np.log(np.clip(curve, cutoffs[0], cutoffs[-1])), lc, np.arange(len(cutoffs)))
    lo = np.floor(pos).astype(int).clip(0, len(cutoffs) - 2); w = pos - lo
    idx = np.arange(len(x)); return ys[lo, idx] * (1 - w) + ys[lo + 1, idx] * w
def make_ir(rt60, seed, pre=.018, damp=.55, stereo=True):
    n = int(SR * rt60 * 1.15); t = np.arange(n) / SR; r = np.random.default_rng(seed); out = []
    for _ in range(2 if stereo else 1):
        w = r.standard_normal(n); low = lp(w, 1400, 1); high = w - low
        ir = low * np.exp(-6.9 * t / rt60) + high * np.exp(-6.9 * t / (rt60 * damp))
        ir *= np.minimum(t / .03, 1); ir = np.roll(ir, int(SR * pre)); ir[:int(SR * pre)] = 0
        out.append(ir / np.sqrt(np.sum(ir ** 2)))
    return np.stack(out, axis=-1) if stereo else out[0]
def reverb(x, ir):
    """Linear convolution; returns len(x)+len(ir) so the tail can ring out."""
    if x.ndim == 1 and ir.ndim == 2: x = np.stack([x, x], axis=-1)
    if x.ndim == 1: return signal.fftconvolve(x, ir)
    return np.stack([signal.fftconvolve(x[:, c], ir[:, c % ir.shape[1]]) for c in range(x.shape[1])], axis=-1)
def reverb_circ(x, ir):
    """Circular convolution: the tail wraps to the start, so loops are seamless."""
    N = x.shape[0]; out = np.zeros_like(x)
    for c in range(x.shape[1]):
        h = np.zeros(N); h[:min(N, ir.shape[0])] = ir[:N, c % ir.shape[1]]
        out[:, c] = irfft(rfft(x[:, c]) * rfft(h), N)
    return out
def place(buf, snd, pos, gain=1.0):
    """Add `snd` into `buf` at sample `pos` (clipped at the end)."""
    pos = int(pos)
    if pos >= len(buf): return
    n = min(len(snd), len(buf) - pos); buf[pos:pos + n] += snd[:n] * gain
def place_circ(buf, snd, pos, gain=1.0):
    idx = (int(pos) + np.arange(len(snd))) % buf.shape[0]
    if buf.ndim == 2 and snd.ndim == 1: snd = snd[:, None]
    buf[idx] += snd * gain
def fit(x, peak):
    m = np.max(np.abs(x)); return x * (peak / m) if m > 0 else x
def fade_out(x, d=.01):
    n = min(len(x), int(SR * d)); x = x.copy(); x[-n:] *= np.linspace(1, 0, n); return x
def loop_noise(N, fade=SR // 2):
    x = rng.standard_normal(N + fade); out = x[:N].copy()
    r = np.linspace(0, 1, fade); out[:fade] = x[:fade] * np.sqrt(r) + x[N:N + fade] * np.sqrt(1 - r); return out


# ----------------------------------------------------------------------------- SFX
def drum(f0=135, f1=52, tau=.2, d=.6, snap=.5):
    t = tt(d); body = np.sin(sweep_phase(f0, f1, d, 5)) * np.exp(-t / tau)
    skin = bp(noise(d), 300, 1800) * np.exp(-t / .025) * snap
    return body + skin

def s_click():
    d = .08; t = tt(d)
    return bp(noise(d), 1800, 5200) * env(d, .001, .012) * .7 + np.sin(2 * np.pi * 1150 * t) * env(d, .001, .02) * .35
def s_hover():
    d = .045; t = tt(d); return np.sin(2 * np.pi * 2600 * t) * env(d, .001, .012) * .5 + hp(noise(d), 5000) * env(d, .001, .008) * .1
def s_build():
    d = 1.0; out = np.zeros(int(SR * d)); t = tt(d)
    place(out, np.sin(sweep_phase(120, 52, .5, 6)) * env(.5, .002, .13) * .9, 0)
    place(out, lp(noise(.3), 700) * env(.3, .001, .05) * .8, 0)                       # stone settling
    place(out, bell(1320, .6, 2.76, 2.2, .18) * .32, SR * .035)                       # hammer on iron
    for i, f in enumerate([587.33, 880, 1174.66]):                                    # rising aether shimmer
        n = tt(.7); vib = 1 + .004 * np.sin(2 * np.pi * 6 * n)
        place(out, np.sin(2 * np.pi * f * n * vib) * env(.7, .12, .22) * .11, SR * (.1 + i * .045))
    return reverb(out, make_ir(.7, 11, stereo=False))[:len(out) + int(SR * .3)]
def s_upgrade():
    d = 1.3; out = np.zeros(int(SR * d))
    for i, n in enumerate([74, 77, 81, 86]):                                          # D5 F5 A5 D6
        place(out, bell(midi(n), .9, 3.51, 2.4, .35) * (.42 - i * .02), SR * i * .085)
    place(out, hp(noise(.5), 6500) * env(.5, .004, .12) * .18, SR * .3)
    place(out, np.sin(2 * np.pi * 293.66 * tt(.9)) * env(.9, .15, .3) * .12, 0)
    return reverb(out, make_ir(.9, 12, stereo=False))[:len(out) + int(SR * .4)]
def s_sell():
    d = .6; out = np.zeros(int(SR * d))
    for i, (a, b) in enumerate([(2100, 3150), (2650, 3975)]):
        t = tt(.4); c = (np.sin(2 * np.pi * a * t) + .6 * np.sin(2 * np.pi * b * t)) * env(.4, .001, .07)
        place(out, c * .35, SR * i * .075)
    place(out, hp(noise(.03), 3000) * env(.03, .001, .01) * .4, 0)
    return out
def s_error():
    d = .3; out = np.zeros(int(SR * d))
    for i in range(2):
        s = lp(saw(118, .1), 520) * env(.1, .004, .06); place(out, s * .7, SR * i * .115)
    return out
def s_arrow():
    d = .4; out = np.zeros(int(SR * d))
    place(out, pluck(196, .25, .985) * .75, 0)                                        # bowstring
    w = (bp(noise(.3), 2400, 6000) * env(.3, .02, .06) + bp(noise(.3), 600, 1600) * env(.3, .09, .09)) * .26
    place(out, w, SR * .01)
    place(out, hp(noise(.02), 2500) * env(.02, .001, .006) * .5, 0)                  # release click
    return out
def s_rune():
    d = 1.0; out = np.zeros(int(SR * d)); t = tt(d)
    place(out, np.sin(sweep_phase(95, 36, .8, 4)) * env(.8, .003, .3) * 1.0, 0)
    place(out, lp(noise(.4), 900) * env(.4, .002, .1) * .6, 0)
    for f, g in [(440, .12), (659.25, .09), (880, .07), (1318.5, .05)]:
        n = tt(.7); vib = 1 + .006 * np.sin(2 * np.pi * 7 * n)
        place(out, np.sin(2 * np.pi * f * n * vib) * env(.7, .03, .22) * g, SR * .02)
    return reverb(out, make_ir(1.0, 13, stereo=False))[:len(out) + int(SR * .5)]
def s_frost():
    d = .8; out = np.zeros(int(SR * d))
    for i, f in enumerate([2637, 3520, 4186, 5274, 6272]):
        place(out, np.sin(2 * np.pi * f * tt(.5)) * env(.5, .001, .1 + .02 * (i % 2)) * (.26 - i * .03), SR * i * .018)
    place(out, hp(noise(.3), 5200) * env(.3, .001, .06) * .3, 0)
    place(out, bp(noise(.35), 1400, 3200) * env(.35, .02, .1) * .25, SR * .02)       # creaking ice
    return reverb(out, make_ir(.6, 14, stereo=False))[:len(out) + int(SR * .2)]
def s_hit():
    d = .3; out = np.zeros(int(SR * d))
    place(out, bp(noise(.08), 900, 5200) * env(.08, .001, .016) * 1.25, 0)           # bone crack
    place(out, np.sin(sweep_phase(210, 85, .2, 5)) * env(.2, .001, .05) * .5, 0)
    place(out, lp(noise(.2), 500) * env(.2, .002, .05) * .45, SR * .01)
    return out
def s_death():                                                                       # bigger finish than a plain hit
    d = .6; out = np.zeros(int(SR * d))
    place(out, bp(noise(.1), 600, 3000) * env(.1, .001, .02) * .8, 0)
    place(out, np.sin(sweep_phase(150, 45, .45, 4)) * env(.45, .001, .1) * .9, 0)
    place(out, hp(noise(.4), 2500) * env(.4, .05, .12) * .12, SR * .03)               # dissolving rattle
    return out
def s_breach():
    d = 1.8; out = np.zeros(int(SR * d))
    place(out, np.sin(sweep_phase(78, 30, 1.2, 3)) * env(1.2, .004, .5) * 1.0, 0)
    for f, g in [(110, .3), (164.8, .22), (247.4, .17), (331, .12), (452, .08)]:
        place(out, np.sin(2 * np.pi * f * tt(1.5)) * env(1.5, .003, .7) * g, 0)
    place(out, lp(noise(.8), 420) * env(.8, .01, .3) * .7, 0)
    return reverb(out, make_ir(1.4, 15, stereo=False))[:len(out) + int(SR * .6)]
def s_wave():                                                                        # war-drum double hit
    out = np.zeros(int(SR * 1.6))
    place(out, drum(125, 50, .24, .8) * .9, 0); place(out, drum(110, 46, .3, 1.0) * 1.0, SR * .32)
    return reverb(out, make_ir(1.1, 16, stereo=False))[:len(out) + int(SR * .5)]
def brass(f, d, a=.18, rel=.35, bright=2200, vib=.004):
    t = tt(d); v = 1 + vib * np.sin(2 * np.pi * 5.2 * t) * np.minimum(t / .4, 1)
    src = sum(signal.sawtooth(2 * np.pi * f * 2 ** (c / 1200) * np.cumsum(v) / SR) for c in (-8, 0, 7)) / 3
    cut = 300 + (bright - 300) * np.minimum(t / (a * 2.2), 1) ** .7
    e = np.minimum(t / a, 1) * np.minimum((d - t) / rel, 1).clip(0, 1)
    return tv_lp(src, cut) * e
def s_horn():
    out = np.zeros(int(SR * 3.0))
    place(out, brass(146.83, 1.1, .2, .3, 1800) * .55 + brass(220, 1.1, .22, .3, 1500) * .35, 0)
    place(out, brass(220, 1.7, .12, .7, 2600) * .55 + brass(293.66, 1.7, .14, .7, 2200) * .3 + brass(110, 1.7, .2, .7, 900) * .35, SR * 1.0)
    return reverb(out, make_ir(1.6, 17, stereo=False))[:len(out) + int(SR * .8)]
def s_clear():
    d = 2.0; out = np.zeros(int(SR * d))
    place(out, bell(220, 1.8, 3.51, 1.6, .9) * .5, 0); place(out, bell(329.63, 1.6, 3.51, 1.6, .8) * .38, SR * .22)
    place(out, bell(554.37, 1.4, 3.51, 1.2, .6) * .22, SR * .44)
    place(out, np.sin(2 * np.pi * 440 * tt(1.2)) * env(1.2, .25, .5) * .08, SR * .1)
    return reverb(out, make_ir(1.3, 18, stereo=False))[:len(out) + int(SR * .6)]
def s_boss():
    d = 3.0; out = np.zeros(int(SR * d)); t = tt(d)
    f = 46 + 5 * np.sin(2 * np.pi * 13 * t) + 8 * np.exp(-t * 1.2)
    growl = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    gate = np.minimum(t / .35, 1) * np.minimum((d - t) / 1.1, 1).clip(0, 1) * (.75 + .25 * np.sin(2 * np.pi * 8 * t))
    formant = bp(growl, 250, 450) * 1.0 + bp(growl, 700, 1100) * .7 + bp(growl, 1700, 2300) * .25
    out += np.tanh(2.2 * formant * gate) * .55
    out += bp(noise(d), 120, 700) * gate * .35
    place(out, np.sin(sweep_phase(80, 28, 1.4, 3)) * env(1.4, .003, .6), 0)
    return reverb(out, make_ir(1.8, 19, stereo=False))[:len(out) + int(SR * .9)]
def s_victory():
    out = np.zeros(int(SR * 7.0))
    place(out, drum(110, 46, .4, 1.2) * .9, 0)
    chords = [(0.0, [146.83, 220, 293.66, 369.99], 1.0), (.95, [196, 246.94, 392, 493.88], 1.0), (1.9, [220, 277.18, 329.63, 440, 554.37], 1.0),
              (2.85, [146.83, 220, 293.66, 369.99, 587.33], 3.6)]
    for start, notes, dur in chords:
        for n in notes: place(out, brass(n, dur, .14, .5 if dur > 2 else .15, 2600) * (.2 / len(notes) * 4.2), SR * start)
    for i, n in enumerate([81, 85, 88, 93]): place(out, bell(midi(n), 2.2, 3.51, 1.6, .9) * .16, SR * (2.85 + i * .12))
    place(out, drum(100, 44, .5, 1.5) * 1.0, SR * 2.85)
    return reverb(out, make_ir(2.4, 20, stereo=False))[:len(out) + int(SR * 1.5)]
def s_defeat():
    out = np.zeros(int(SR * 6.0))
    for i, f in enumerate([146.83, 110, 73.42]):
        place(out, bell(f, 3.2, 2.76, 2.0, 1.4) * (.55 + i * .08), SR * i * 1.0)
    place(out, np.sin(sweep_phase(60, 28, 2.5, 2)) * env(2.5, .01, 1.0) * .8, SR * 2.0)
    t = tt(4.0); drone = lp(saw(55, 4.0), 260) * np.minimum(t / .8, 1) * np.exp(-t / 1.6) * .45
    drone += lp(saw(58.27, 4.0), 260) * np.minimum(t / 1.0, 1) * np.exp(-t / 1.4) * .25      # minor-second dread
    place(out, drone, SR * .3)
    return reverb(out, make_ir(2.8, 21, stereo=False))[:len(out) + int(SR * 1.5)]

SFX = {  # name: (generator, peak)
    'snd_click': (s_click, .55), 'snd_hover': (s_hover, .22), 'snd_build': (s_build, .85), 'snd_upgrade': (s_upgrade, .75),
    'snd_sell': (s_sell, .6), 'snd_error': (s_error, .5), 'snd_arrow': (s_arrow, .7), 'snd_rune': (s_rune, .88),
    'snd_frost': (s_frost, .72), 'snd_hit': (s_hit, .78), 'snd_death': (s_death, .8), 'snd_breach': (s_breach, .95),
    'snd_wave': (s_wave, .85), 'snd_horn': (s_horn, .85), 'snd_clear': (s_clear, .7), 'snd_boss': (s_boss, .92),
    'snd_victory': (s_victory, .88), 'snd_defeat': (s_defeat, .88),
}


# ----------------------------------------------------------------------------- music
BPM = 72; BEAT = 60 / BPM; BARS = 16
N = int(round(BARS * 4 * BEAT * SR)); LOOP_S = N / SR
# Dm - Bb - Gm - A, two bars each, played twice (A major dominant resolves to Dm at the loop point).
CHORDS = [  # (bass midi, chord tones midi ascending)
    (38, [50, 57, 62, 65, 69]), (34, [46, 53, 58, 62, 65]), (31, [43, 50, 55, 58, 62]), (33, [45, 52, 57, 61, 64]),
]
VOWELS = {'ah': [(800, 90, 1.0), (1150, 110, .5), (2800, 200, .25)], 'oh': [(500, 70, 1.0), (1000, 100, .45), (2800, 200, .15)]}
def vowel(x, which):
    return sum(bp(x, f - w, f + w, 2) * g for f, w, g in VOWELS[which])
def whole_cycles(f): return round(f * LOOP_S) / LOOP_S

def music_ambience():
    L = np.zeros((N, 2)); bar = 4 * BEAT; seg = 2 * bar
    # --- sustained drone with wind (whole cycles => seamless)
    t = np.arange(N) / SR
    for f, g, pan in [(73.42, .5, 0), (110.0, .3, 1), (146.83, .22, 0), (147.4, .12, 1)]:
        f = whole_cycles(f); s = np.sin(2 * np.pi * f * t) * g * (.8 + .2 * np.sin(2 * np.pi * 2 / LOOP_S * t + f))
        L[:, pan] += s * .75; L[:, 1 - pan] += s * .35
    for c in range(2):
        wind = lp(loop_noise(N), 500, 2) * (.55 + .45 * np.sin(2 * np.pi * (3 + c) / LOOP_S * t + c))
        L[:, c] += wind * .35
    # --- choir pad, one chord per two bars with long cross-fades, stereo from different detune sets
    pad = np.zeros((N, 2)); fade = 1.8
    for k in range(8):
        bass, tones = CHORDS[k % 4]; start = k * seg - fade; d = seg + 2 * fade
        tp = tt(d); e = np.minimum(tp / fade, 1) * np.minimum((d - tp) / fade, 1)
        e = np.sin(np.clip(e, 0, 1) * np.pi / 2) ** 1.3
        for ch, dets in enumerate([(-11, -2, 6), (-6, 3, 12)]):
            src = sum(saw(midi(n), d, c, rng.uniform(0, 6.28)) for n in tones[:4] for c in dets) / 12
            src = lp(src, 3500, 1)
            place_circ(pad[:, ch], vowel(src, 'ah' if k % 2 == 0 else 'oh') * e, start * SR)
    L += pad * 3.2
    # --- harp arpeggio (plucked strings), up and down over the chord
    harp = np.zeros((N, 2)); pattern = [0, 1, 2, 3, 4, 3, 2, 1]
    for k in range(8):
        bass, tones = CHORDS[k % 4]
        for i in range(16):
            n = tones[pattern[i % 8]]; accent = 1.0 if i % 4 == 0 else .62
            note = pluck(midi(n), 2.6, .993, .8) * accent * (.92 + .16 * rng.random())
            note = fade_out(note, .2); pan = (pattern[i % 8] / 4)
            pos = (k * seg + i * BEAT / 2) * SR
            place_circ(harp, note[:, None] * np.array([1 - pan * .6, .4 + pan * .6]), pos, .5)
    # --- celesta-like bells, one per four bars on the chord's top tone
    bells = np.zeros((N, 2))
    for k in range(0, 8, 2):
        bass, tones = CHORDS[k % 4]; place_circ(bells, bell(midi(tones[4] + 12), 5.0, 3.51, 1.8, 1.4)[:, None] * np.array([.8, 1.0]), k * seg * SR + 1.5 * BEAT * SR, .35)
    # --- flute-like lead in the second half
    lead = np.zeros((N, 2)); mel = [  # (start beat, beats, midi)  over bars 9-16
        (0, 3, 69), (3, 1, 67), (4, 2, 65), (6, 1, 64), (7, 1, 62),   # Dm
        (8, 3, 65), (11, 1, 67), (12, 2, 69), (14, 2, 70),            # Bb
        (16, 3, 74), (19, 1, 72), (20, 2, 70), (22, 1, 69), (23, 1, 67),  # Gm
        (24, 3, 76), (27, 1, 74), (28, 2, 73), (30, 1, 71), (31, 1, 69),  # A
    ]
    for sb, nb, n in mel:
        d = nb * BEAT + .6; t2 = tt(d); f = midi(n); vib = 1 + .0065 * np.sin(2 * np.pi * 5.1 * t2) * np.minimum(t2 / .7, 1)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        tone = np.sin(ph) + .28 * np.sin(2 * ph) + .08 * np.sin(3 * ph)
        tone += bp(noise(d), f * .9, f * 3, 1) * .25                       # breath
        tone *= np.minimum(t2 / .14, 1) * np.minimum((d - t2) / .5, 1).clip(0, 1)
        place_circ(lead, tone[:, None] * np.array([1.0, .9]), (8 * 4 * BEAT + sb * BEAT) * SR, .21)
    # --- reverb (circular so the tail wraps) and mixdown
    ir_big = make_ir(4.2, 31, pre=.025, damp=.5); ir_small = make_ir(1.6, 32, pre=.012, damp=.6)
    mix = L * .55 + reverb_circ(pad * 3.2, ir_big) * 1.1
    mix += harp * .55 + reverb_circ(harp, ir_big) * .9 + bells * .5 + reverb_circ(bells, ir_big) * 1.1
    mix += lead * 1.0 + reverb_circ(lead, ir_small) * .9
    mix = hp(mix, 28, 1)
    return fit(mix, .60)

def music_battle():
    M = np.zeros((N, 2)); bar = 4 * BEAT; seg = 2 * bar
    # --- taiko / war drums (pattern per bar; fills every 4th bar)
    hits = [(0, 1.0, 0), (1.5, .42, 1), (2, .8, 1), (3, .55, 0), (3.5, .5, 1)]
    for b in range(BARS):
        for pos, vel, side in hits:
            d = drum(rng.uniform(112, 128), 50, .22, .9) * vel * .85
            place_circ(M, d[:, None] * np.array([1 - .35 * side, .65 + .35 * side]), (b * bar + pos * BEAT) * SR)
        if b % 4 == 3:   # crescendo roll
            for i in range(8):
                d = drum(rng.uniform(150, 175), 70, .09, .3, .8) * (.25 + .09 * i)
                place_circ(M, d[:, None] * np.array([.8, .8]), (b * bar + 3 * BEAT + i * BEAT / 8) * SR)
    # --- driving low-string ostinato (palm-muted saws on the chord root)
    acc = [1, .5, .7, .5, .9, .5, .7, .6]
    for k in range(8):
        bass, tones = CHORDS[k % 4]
        for i in range(16):
            f = midi(bass); d = BEAT * .5
            n = (saw(f, d + .25) + .35 * saw(2 * f, d + .25, 6)) * env(d + .25, .004, .16)
            n = lp(n, 650 + 500 * acc[i % 8], 2) * acc[i % 8] * .6
            place_circ(M, n[:, None] * np.array([.9, .9]), (k * seg + i * BEAT / 2) * SR)
    # --- low brass swells on every chord change
    for k in range(8):
        bass, tones = CHORDS[k % 4]; d = seg + 2.0; t2 = tt(d)
        src = sum(saw(midi(n), d, c) for n in (bass + 12, bass + 19, bass + 24) for c in (-9, 8)) / 6
        cut = 350 + 1500 * np.sin(np.pi * np.minimum(t2 / d, 1)) ** 1.2
        sw = tv_lp(src, cut) * np.sin(np.pi * np.clip(t2 / d, 0, 1)) ** 1.5
        place_circ(M, sw[:, None] * np.array([1.0, 1.0]), (k * seg - 1.0) * SR, .5)
    # --- tension riser into the loop point
    d = 2.6; t2 = tt(d); r = bp(noise(d), 500, 5000) * (t2 / d) ** 2.2
    r = fade_out(r, .05)                                           # no hard cut at the loop point
    place_circ(M, r[:, None] * np.array([.6, .6]), (LOOP_S - d) * SR, .22)
    # --- sparse anvil / chain clangs on the off-beats
    for b in range(BARS):
        if b % 2 == 1: place_circ(M, bell(660 if b % 4 == 1 else 495, 1.2, 4.11, 3.2, .35)[:, None] * np.array([.5, 1.0]), (b * bar + 2.5 * BEAT) * SR, .13)
    ir = make_ir(2.0, 41, pre=.015, damp=.5)
    mix = M * .85 + reverb_circ(M, ir) * .75
    mix = hp(mix, 30, 1)
    return fit(mix, .62)


# ----------------------------------------------------------------------------- output & registration
def write_wav(name, data, stereo=False):
    data = np.clip(data, -.97, .97); pcm = (data * 32767).astype('<i2')
    folder = ROOT / 'sounds' / name; folder.mkdir(parents=True, exist_ok=True)
    with wave.open(str(folder / f'{name}.wav'), 'wb') as f:
        f.setnchannels(2 if stereo else 1); f.setsampwidth(2); f.setframerate(SR); f.writeframes(pcm.tobytes())
    return len(pcm) / SR

def update_yy(name, duration, stereo=False, music=False):
    path = ROOT / 'sounds' / name / f'{name}.yy'
    if not path.exists():
        template = (ROOT / 'sounds/snd_click/snd_click.yy').read_text(encoding='utf-8')
        path.write_text(template.replace('snd_click', name), encoding='utf-8', newline='\n')
    text = path.read_text(encoding='utf-8')
    def setv(key, value):
        nonlocal text
        text, n = re.subn(rf'("{key}":\s*)([^,\n]+)', lambda m: m.group(1) + value, text, count=1)
        assert n == 1, (name, key)
    setv('duration', repr(round(float(duration), 6)))
    setv('channelFormat', '1' if stereo else '0'); setv('compression', '0'); setv('preload', 'true')   # uncompressed: compressed codecs can add a gap/click at the loop point
    path.write_text(text, encoding='utf-8', newline='\n')

def register(names):
    path = ROOT / 'Wall Protocol.yyp'; text = path.read_text(encoding='utf-8')
    for name in names:
        if f'"name":"{name}"' in text: continue
        line = f'    {{"id":{{"name":"{name}","path":"sounds/{name}/{name}.yy",}},}},\n'
        existing = re.findall(r'^    \{"id":\{"name":"(snd_\w+)"', text, re.M)
        later = [s for s in sorted(existing) if s > name]
        if later: anchor = f'    {{"id":{{"name":"{later[0]}"'; text = text.replace(anchor, line + anchor, 1)
        else:
            last = sorted(existing)[-1]; m = re.search(rf'^    \{{"id":\{{"name":"{last}".*\n', text, re.M); text = text[:m.end()] + line + text[m.end():]
    path.write_text(text, encoding='utf-8', newline='\n')

def main():
    report = '--report' in sys.argv; names = []
    for name, (gen, peak) in SFX.items():
        x = fit(fade_out(gen(), .02), peak); d = write_wav(name, x); update_yy(name, d); names.append(name)
        if report: print(f'{name:12s} {d:5.2f}s peak {np.max(np.abs(x)):.2f} rms {np.sqrt(np.mean(x ** 2)):.3f}')
    for name, fn in (('snd_ambience', music_ambience), ('snd_battle', music_battle)):
        x = fn(); d = write_wav(name, x, True); update_yy(name, d, True, True); names.append(name)
        if report:
            seam = np.max(np.abs(x[0] - x[-1])); step = np.max(np.abs(np.diff(x, axis=0)))
            print(f'{name:12s} {d:5.2f}s peak {np.max(np.abs(x)):.2f} rms {np.sqrt(np.mean(x ** 2)):.3f} loop-seam jump {seam:.4f} (max normal step {step:.4f})')
    register(names)

if __name__ == '__main__':
    main()
