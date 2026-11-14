import os
import subprocess
import cv2

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

VIDEO = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\flat_global_ecco2_2028x1024_comp_p30.mp4'
AUDIO = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\sst_track.wav'
OUT_SILENT = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\sst_playhead_silent.mp4'
OUT = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\sst_jukebox.mp4'

STEPS = 64             # must match sst_from_frame.py
STEP_SECONDS = 0.5     # must match sst_to_sound.py
TAIL_SECONDS = 1.0
SWEEP_SECONDS = STEPS * STEP_SECONDS

cap = cv2.VideoCapture(VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
n_frames = int((SWEEP_SECONDS + TAIL_SECONDS) * fps)

writer = cv2.VideoWriter(OUT_SILENT, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
written = 0
for k in range(n_frames):
    ok, frame = cap.read()
    if not ok:
        break
    t = k / fps
    if t <= SWEEP_SECONDS:
        x = int(t / SWEEP_SECONDS * (w - 1))
        cv2.line(frame, (x, 0), (x, h - 1), (255, 255, 255), 3)
    writer.write(frame)
    written += 1
cap.release()
writer.release()
print('Frames written:', written)

cmd = ['ffmpeg', '-y', '-i', OUT_SILENT, '-i', AUDIO,
       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', OUT]
try:
    subprocess.run(cmd, check=True)
    print('Saved', OUT)
except FileNotFoundError:
    print('ffmpeg was not found. Is it installed and on your PATH?')