import os
import subprocess
import cv2

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

VIDEO = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\AirQuality_SphereWithLabels_5760x3240.mp4'
FRAME_INDEX = 1350
AUDIO = 'data/aq_track.wav'
OUT_SILENT = 'data/aq_playhead_silent.mp4'
OUT = 'data/aq_jukebox.mp4'

SCALE = 0.25                           # 5760x3240 becomes 1440x810
GLOBE_LEFT, GLOBE_RIGHT = 1453, 4300   # same values as aq_from_frame.py
GLOBE_TOP, GLOBE_BOTTOM = 173, 3066
STEPS = 64
STEP_SECONDS = 0.5                     # must match aq_to_sound.py
TAIL_SECONDS = 2.0
FPS = 30

cap = cv2.VideoCapture(VIDEO)
cap.set(cv2.CAP_PROP_POS_FRAMES, FRAME_INDEX)
ok, frame = cap.read()
cap.release()
if not ok:
    raise SystemExit('Could not read the frame from ' + VIDEO)

frame = cv2.resize(frame, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
h, w = frame.shape[:2]
L, R = int(GLOBE_LEFT * SCALE), int(GLOBE_RIGHT * SCALE)
T, B = int(GLOBE_TOP * SCALE), int(GLOBE_BOTTOM * SCALE)

sweep = STEPS * STEP_SECONDS
total = int((sweep + TAIL_SECONDS) * FPS)
writer = cv2.VideoWriter(OUT_SILENT, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (w, h))
for k in range(total):
    t = k / FPS
    img = frame.copy()
    if t <= sweep:
        x = int(L + t / sweep * (R - L))
        cv2.line(img, (x, T), (x, B), (255, 255, 255), 3)
    writer.write(img)
writer.release()
print('Frames written:', total)

cmd = ['ffmpeg', '-y', '-i', OUT_SILENT, '-i', AUDIO,
       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', OUT]
try:
    subprocess.run(cmd, check=True)
    print('Saved', OUT)
except FileNotFoundError:
    print('ffmpeg was not found. Is it installed and on your PATH?')