"""Original placeholder music bed for edits: upbeat, playful, 120 BPM, C major.

Synthesised from scratch (no samples), so it is safe to use as a guide track.
The trending sound is swapped in inside the Instagram app at posting time.

Usage: python3 make-placeholder-music.py out.wav [bars]
Writes a 48 kHz stereo WAV and prints the beat grid (seconds per beat).
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 120
BEAT = 60 / BPM
out = sys.argv[1]
bars = int(sys.argv[2]) if len(sys.argv) > 2 else 32
n = int(SR * BEAT * 4 * bars) + SR
mix = np.zeros((n, 2))
rng = np.random.default_rng(7)


def place(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    j = min(n, i + len(sig))
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:j, 0] += sig[: j - i] * gain * left
    mix[i:j, 1] += sig[: j - i] * gain * right


def env(length, attack=0.003, decay=0.15):
    t = np.arange(int(length * SR)) / SR
    return np.minimum(t / attack, 1) * np.exp(-t / decay)


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.35, 0.001, 0.12)


def clap():
    noise = rng.standard_normal(int(0.25 * SR))
    e = env(0.25, 0.001, 0.06)
    for k in (0.0, 0.012, 0.024):  # three quick bursts
        e += np.roll(env(0.25, 0.001, 0.01), int(k * SR)) * 0.6
    return np.convolve(noise, [1, -0.9], "same") * e * 0.5


def shaker():
    noise = rng.standard_normal(int(0.08 * SR))
    return np.diff(noise, prepend=0) * env(0.08, 0.004, 0.02) * 0.25


def marimba(midi, length=0.3):
    t = np.arange(int(length * SR)) / SR
    f = hz(midi)
    tone = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 40)
    return tone * env(length, 0.002, 0.09)


def bass(midi, length=0.22):
    t = np.arange(int(length * SR)) / SR
    f = hz(midi)
    tone = np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + np.sin(2 * np.pi * f * t)
    return np.tanh(tone) * env(length, 0.004, 0.08)


# I-vi-IV-V in C, bouncy
chords = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [59, 62, 67])]
# playful pentatonic hook, one bar = 8 eighth notes (None = rest)
hooks = [
    [72, None, 76, 79, None, 76, 74, None],
    [72, None, 69, 72, None, 74, 76, None],
    [77, None, 76, 74, None, 72, 74, 76],
    [79, None, None, 76, 74, None, 71, None],
]

for bar in range(bars):
    t0 = bar * 4 * BEAT
    root, triad = chords[bar % 4]
    intro = bar < 2
    for b in range(4):
        tb = t0 + b * BEAT
        if not intro:
            place(kick(), tb, 0, 0.9)
            if b in (1, 3):
                place(clap(), tb, 0.05, 0.8)
        # bass on the beat and the "and"
        place(bass(root if b % 2 == 0 else root + 12), tb, -0.1, 0.35)
        place(bass(root + 7), tb + BEAT / 2, -0.1, 0.22)
    for s in range(16):
        if not intro or s % 2 == 0:
            place(shaker(), t0 + s * BEAT / 4, 0.4, 0.9 if s % 2 else 0.5)
    # chord stabs on the off-beats
    for b in range(4):
        for note in triad:
            place(marimba(note, 0.2), t0 + b * BEAT + BEAT / 2, -0.35, 0.12)
    # hook from bar 2, call-and-response every other phrase
    if bar >= 2:
        for k, note in enumerate(hooks[bar % 4]):
            if note is not None:
                place(marimba(note), t0 + k * BEAT / 2, 0.25, 0.32)

mix /= np.max(np.abs(mix)) * 1.12
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"wrote {out}: {bars} bars at {BPM} BPM, beat every {BEAT:.3f}s, {n / SR:.1f}s")
