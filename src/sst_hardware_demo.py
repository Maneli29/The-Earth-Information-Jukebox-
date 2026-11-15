# First draft written with help from Claude (Anthropic) during NASA Space Apps 2026.
# Tested and adjusted by Emmanuel.
import os
import csv
import time
import cv2
import numpy as np
import serial
import sounddevice as sd
from scipy.io import wavfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

PORT = 'COM4'            # change to your Arduino's port
GRID = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\sst_grid.csv'
WAV = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\sst_track.wav'
VIDEO = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\sst_playhead_silent.mp4'
STEP_SECONDS = 0.5       # must match sst_to_sound.py
WARM_C = 20.0            # a latitude LED lights at or above this temperature
TEMP_MAX = 32.0
WINDOW_WIDTH = 1100


def read_grid(path):
    rows = []
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            rows.append([float(x) if x != '' else np.nan for x in row[1:]])
    return np.array(rows)


def send(ser, text):
    ser.write((text + '\n').encode())


def apply_step(ser, row):
    valid = row[~np.isnan(row)]
    if valid.size:
        level = int(round(valid.mean() / TEMP_MAX * 100))
        label = 'Avg %d C' % round(valid.mean())
    else:
        level = 0
        label = 'Land / ice'
    mask = 0
    for j, t in enumerate(row):
        if not np.isnan(t) and t >= WARM_C:
            mask |= 1 << j
    send(ser, f'LEVEL,{level}')
    send(ser, f'LEDS,{mask}')
    send(ser, f'T2,{label}')


if __name__ == '__main__':
    grid = read_grid(GRID)
    sr, data = wavfile.read(WAV)
    data = data.astype(np.float32) / 32768.0

    cap = cv2.VideoCapture(VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    ser = serial.Serial(PORT, 9600, timeout=0.05)
    time.sleep(2)  # the Arduino restarts when the port opens
    send(ser, 'FREQ,0')
    send(ser, 'T1,Sea surface')
    send(ser, 'T2,Ready')
    input('Press Enter to start (press q in the video window to stop)...')

    quit_early = False
    sd.play(data, sr)
    start = time.perf_counter()
    last_step = -1
    try:
        for k in range(n_frames):
            while time.perf_counter() - start < k / fps:
                time.sleep(0.001)
            ok, frame = cap.read()
            if not ok:
                break
            step = int((time.perf_counter() - start) / STEP_SECONDS)
            if step != last_step and step < len(grid):
                last_step = step
                ser.reset_input_buffer()   # discard knob messages we are not using
                apply_step(ser, grid[step])
            h, w = frame.shape[:2]
            frame = cv2.resize(frame, (WINDOW_WIDTH, int(h * WINDOW_WIDTH / w)))
            cv2.imshow('Earth Jukebox', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                quit_early = True
                break
        if quit_early:
            sd.stop()
        else:
            sd.wait()
    finally:
        send(ser, 'LEVEL,0')
        send(ser, 'LEDS,0')
        send(ser, 'T2,Done')
        ser.close()
        cap.release()
        cv2.destroyAllWindows()