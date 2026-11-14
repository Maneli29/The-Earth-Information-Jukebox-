# First draft written with help from Claude (Anthropic) during NASA Space Apps 2026.
# Tested and adjusted by Emmanuel.
import os
import csv
import numpy as np
from scipy.io import wavfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

SAMPLE_RATE = 44100
STEP_SECONDS = 0.5
BAND_STAGGER = 0.1
PENTATONIC = [0, 2, 4, 7, 9]

VOICES = {
    'co':   {'base': 48, 'octaves': 2, 'dur': 0.45},   # warm pluck
    'pm25': {'base': 55, 'octaves': 2, 'dur': 0.90},   # soft pad
    'nox':  {'base': 72, 'octaves': 2, 'dur': 0.80},   # bell
}


def midi_to_freq(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def make_scale(base, octaves):
    notes = [base + 12 * o + d for o in range(octaves) for d in PENTATONIC]
    notes.append(base + 12 * octaves)
    return notes


def pluck(freq, dur, amp):
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    wave = (np.sin(2 * np.pi * freq * t)
            + 0.5 * np.sin(2 * np.pi * 2 * freq * t)
            + 0.25 * np.sin(2 * np.pi * 3 * freq * t))
    env = np.minimum(1, t / 0.005) * np.exp(-6 * t / dur)
    return amp * wave * env


def pad(freq, dur, amp):
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    wave = 0.5 * (np.sin(2 * np.pi * freq * t) + np.sin(2 * np.pi * freq * 1.004 * t))
    env = np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.3)
    return amp * wave * env


def bell(freq, dur, amp):
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    wave = (np.sin(2 * np.pi * freq * t)
            + 0.5 * np.sin(2 * np.pi * freq * 2.76 * t)
            + 0.25 * np.sin(2 * np.pi * freq * 5.4 * t))
    env = np.minimum(1, t / 0.003) * np.exp(-4 * t / dur)
    return amp * wave * env


MAKERS = {'co': pluck, 'pm25': pad, 'nox': bell}


def read_grid(path):
    pollutants, rows = [], []
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            pollutants.append(row[1])
            rows.append([float(x) if x != '' else np.nan for x in row[2:]])
    return pollutants, np.array(rows)


if __name__ == '__main__':
    pollutants, grid = read_grid('data/aq_grid.csv')
    steps, bands = grid.shape
    total = int(SAMPLE_RATE * (steps * STEP_SECONDS + 2.0))
    left = np.zeros(total)
    right = np.zeros(total)
    played = 0

    for i in range(steps):
        pan = i / (steps - 1)
        voice = VOICES[pollutants[i]]
        notes = make_scale(voice['base'], voice['octaves'])
        maker = MAKERS[pollutants[i]]
        for j in range(bands):
            val = grid[i, j]
            if np.isnan(val):
                continue
            x = float(np.clip(val, 0, 1))
            midi = notes[int(round(x * (len(notes) - 1)))]
            sig = maker(midi_to_freq(midi), voice['dur'], 0.1 + 0.2 * x)
            start = int(SAMPLE_RATE * (i * STEP_SECONDS + j * BAND_STAGGER))
            end = start + len(sig)
            left[start:end] += sig * (1 - pan)
            right[start:end] += sig * pan
            played += 1

    audio = np.stack([left, right], axis=1)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.9
    wavfile.write('data/aq_track.wav', SAMPLE_RATE, (audio * 32767).astype(np.int16))
    print('Notes played:', played)
    print('Length: %.1f seconds' % (total / SAMPLE_RATE))
    print('Saved data/aq_track.wav')