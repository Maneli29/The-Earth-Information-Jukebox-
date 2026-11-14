import os
import csv
import numpy as np
from scipy.io import wavfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

SAMPLE_RATE = 44100
STEP_SECONDS = 0.5     # time per west-to-east step
NOTE_SECONDS = 0.35    # length of each note
BAND_STAGGER = 0.05    # delay between latitude bands (north plays first)
PENTATONIC = [0, 2, 4, 7, 9]
BASE_MIDI = 48         # C3
OCTAVES = 3
TEMP_MAX = 32.0


def scale_notes():
    notes = []
    for o in range(OCTAVES):
        for d in PENTATONIC:
            notes.append(BASE_MIDI + 12 * o + d)
    notes.append(BASE_MIDI + 12 * OCTAVES)
    return notes


def midi_to_freq(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tone(freq, dur, amp, brightness):
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) + brightness * np.sin(2 * np.pi * 2 * freq * t)
    env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.02) * np.exp(-2.5 * t / dur)
    return amp * wave * env


def read_grid(path):
    rows = []
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            rows.append([float(x) if x != '' else np.nan for x in row[1:]])
    return np.array(rows)


if __name__ == '__main__':
    grid = read_grid('data/sst_grid.csv')
    steps, bands = grid.shape
    total = int(SAMPLE_RATE * (steps * STEP_SECONDS + 1.0))
    left = np.zeros(total)
    right = np.zeros(total)
    notes = scale_notes()
    played = 0

    for i in range(steps):
        pan = i / (steps - 1)               # 0 = left speaker (west), 1 = right (east)
        for j in range(bands):
            temp = grid[i, j]
            if np.isnan(temp):
                continue                    # land or ice: silence
            t = float(np.clip(temp, 0, TEMP_MAX))
            midi = notes[int(round(t / TEMP_MAX * (len(notes) - 1)))]
            sig = tone(midi_to_freq(midi), NOTE_SECONDS, 0.15, 0.6 * t / TEMP_MAX)
            start = int(SAMPLE_RATE * (i * STEP_SECONDS + j * BAND_STAGGER))
            end = start + len(sig)
            left[start:end] += sig * (1 - pan)
            right[start:end] += sig * pan
            played += 1

    audio = np.stack([left, right], axis=1)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.9
    wavfile.write('data/sst_track.wav', SAMPLE_RATE, (audio * 32767).astype(np.int16))
    print('Notes played:', played)
    print('Length: %.1f seconds' % (total / SAMPLE_RATE))
    print('Saved data/sst_track.wav')