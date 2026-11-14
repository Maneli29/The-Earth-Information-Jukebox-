import os
import csv
import cv2
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

VIDEO = r"C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\AirQuality_SphereWithLabels_5760x3240.mp4"
FRAME_INDEX = 1350
SCALE = 0.25                 # 5760x3240 becomes 1440x810, much faster

# Measure these in Paint on the full-size image (pixels at 5760 x 3240)
GLOBE_LEFT, GLOBE_RIGHT = 1453, 4300
GLOBE_TOP, GLOBE_BOTTOM = 173, 3066
BAND_EDGES = [1453, 2430, 3600, 4300]  # left edge, CO|PM2.5, PM2.5|NOx, right edge
POLLUTANTS = ['co', 'pm25', 'nox']

STEPS = 64
BANDS = 5
MIN_FRACTION = 0.3           # a cell needs this much valid area, else silence


def read_frame(path, index):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise SystemExit(f'Could not read frame {index} from {path}')
    return frame


def intensity_warm(h_deg, s):
    # CO and PM2.5: pale yellow = low, orange = middle, red = high
    hue_part = np.clip((60 - h_deg) / 60, 0, 1)
    return np.clip(0.6 * hue_part + 0.4 * s / 255, 0, 1)


def intensity_nox(v):
    # NOx (green): lighter = low, darker = high
    return np.clip(1 - v / 255, 0, 1)


def pixel_intensity(small, L, R, T, B, edges):
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    h = hsv[:, :, 0].astype(float) * 2
    s = hsv[:, :, 1].astype(float)
    v = hsv[:, :, 2].astype(float)
    H, W = h.shape
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = (L + R) / 2, (T + B) / 2
    r = min(R - L, B - T) / 2 * 0.98
    in_globe = (xx - cx) ** 2 + (yy - cy) ** 2 <= r ** 2
    has_data = in_globe & (v > 20)
    inten = np.full((H, W), np.nan)
    for k in range(3):
        cols = (xx >= edges[k]) & (xx < edges[k + 1]) & has_data
        if k < 2:
            inten[cols] = intensity_warm(h, s)[cols]
        else:
            inten[cols] = intensity_nox(v)[cols]
    return inten


def build_grid(inten, L, R, T, B, edges):
    xe = np.linspace(L, R, STEPS + 1, dtype=int)
    ye = np.linspace(T, B, BANDS + 1, dtype=int)
    grid = np.full((STEPS, BANDS), np.nan)
    which = []
    for i in range(STEPS):
        xc = (xe[i] + xe[i + 1]) / 2
        k = 0 if xc < edges[1] else (1 if xc < edges[2] else 2)
        which.append(k)
        for j in range(BANDS):
            cell = inten[ye[j]:ye[j + 1], xe[i]:xe[i + 1]]
            vals = cell[~np.isnan(cell)]
            if vals.size >= MIN_FRACTION * cell.size:
                grid[i, j] = vals.mean()
    return grid, which


if __name__ == '__main__':
    frame = read_frame(VIDEO, FRAME_INDEX)
    small = cv2.resize(frame, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
    sc = lambda x: int(round(x * SCALE))
    L, R, T, B = sc(GLOBE_LEFT), sc(GLOBE_RIGHT), sc(GLOBE_TOP), sc(GLOBE_BOTTOM)
    edges = [sc(x) for x in BAND_EDGES]

    inten = pixel_intensity(small, L, R, T, B, edges)
    grid, which = build_grid(inten, L, R, T, B, edges)

    vis = np.clip(np.nan_to_num(inten, nan=0), 0, 1)
    img = cv2.applyColorMap((vis * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    img[np.isnan(inten)] = (40, 40, 40)
    for x in edges:
        cv2.line(img, (x, 0), (x, img.shape[0] - 1), (255, 255, 255), 2)
    os.makedirs('data/samples', exist_ok=True)
    cv2.imwrite('data/samples/aq_check.png', img)

    with open('data/aq_grid.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['step', 'pollutant'] + [f'band{j + 1}' for j in range(BANDS)])
        for i in range(STEPS):
            row = ['' if np.isnan(x) else round(float(x), 3) for x in grid[i]]
            w.writerow([i, POLLUTANTS[which[i]]] + row)

    for k, name in enumerate(POLLUTANTS):
        vals = grid[[i for i in range(STEPS) if which[i] == k]]
        print(name, 'mean intensity: %.2f' % np.nanmean(vals),
              '| silent cells:', int(np.isnan(vals).sum()))
    print('Saved data/samples/aq_check.png and data/aq_grid.csv')