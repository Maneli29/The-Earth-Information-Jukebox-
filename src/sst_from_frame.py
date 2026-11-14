import os
import csv
import cv2
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

VIDEO = r'C:\Users\Quantam Waffle\OneDrive\Documents\GitHub\The-Earth-Information-Jukebox-\data\flat_global_ecco2_2028x1024_comp_p30.mp4'
FRAME_INDEX = 0

# Legend measurements in pixels (from Paint)
LEG_X0, LEG_X1 = 42, 321         # x of the "0" and "32" labels
LEG_TEMP0, LEG_TEMP1 = 0.0, 32.0
LEG_ROWS = (978, 988)            # rows through the middle of the colour bar
BAR_X_FROM, BAR_X_TO = 50, 314   # stay clear of the bar's edges

COLUMNS = 64      # sweep steps, west to east
BANDS = 5         # latitude bands, north to south
MIN_PIXELS = 30   # fewer coloured pixels than this = land, so silence


def read_frame(path, index):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise SystemExit(f'Could not read frame {index} from {path}')
    return frame


def hsv_parts(frame_bgr):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    h = hsv[:, :, 0].astype(float)
    h[h > 150] -= 180            # make red continuous around 0
    return h, hsv[:, :, 1], hsv[:, :, 2]


def build_legend(h):
    xs = np.arange(BAR_X_FROM, BAR_X_TO + 1)
    strip = h[LEG_ROWS[0]:LEG_ROWS[1], BAR_X_FROM:BAR_X_TO + 1]
    hue_profile = np.median(strip, axis=0)
    hue_profile = np.minimum.accumulate(hue_profile)  # blue on the left falls to red on the right
    temps = (xs - LEG_X0) / (LEG_X1 - LEG_X0) * (LEG_TEMP1 - LEG_TEMP0) + LEG_TEMP0
    # np.interp needs increasing x values, so flip both
    hue_inc = hue_profile[::-1] + np.arange(len(xs)) * 1e-6
    temp_inc = temps[::-1]
    return hue_inc, temp_inc


def to_temperature(frame):
    h, s, v = hsv_parts(frame)
    hue_axis, temp_axis = build_legend(h)
    coloured = (s > 120) & (v > 70)
    coloured[930:, :340] = False      # ignore the legend itself
    temp = np.interp(h, hue_axis, temp_axis)
    temp[~coloured] = np.nan
    return temp


def grid_means(temp):
    H, W = temp.shape
    out = np.full((COLUMNS, BANDS), np.nan)
    xe = np.linspace(0, W, COLUMNS + 1, dtype=int)
    ye = np.linspace(0, H, BANDS + 1, dtype=int)
    for i in range(COLUMNS):
        for j in range(BANDS):
            cell = temp[ye[j]:ye[j + 1], xe[i]:xe[i + 1]]
            vals = cell[~np.isnan(cell)]
            if vals.size >= MIN_PIXELS:
                out[i, j] = vals.mean()
    return out


def save_check(temp):
    t = np.nan_to_num(temp, nan=-1)
    img = np.clip(t / 32 * 255, 0, 255).astype(np.uint8)
    img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
    img[np.isnan(temp)] = (40, 40, 40)
    os.makedirs('data/samples', exist_ok=True)
    cv2.imwrite('data/samples/sst_check.png', img)


if __name__ == '__main__':
    frame = read_frame(VIDEO, FRAME_INDEX)
    print('Frame size:', frame.shape[1], 'x', frame.shape[0])
    temp = to_temperature(frame)
    print('Coloured ocean pixels:', int((~np.isnan(temp)).sum()))
    print('Temperature range found: %.1f to %.1f C' % (np.nanmin(temp), np.nanmax(temp)))
    grid = grid_means(temp)
    save_check(temp)
    with open('data/sst_grid.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['step'] + [f'band{j + 1}' for j in range(BANDS)])
        for i in range(COLUMNS):
            w.writerow([i] + ['' if np.isnan(x) else round(float(x), 1) for x in grid[i]])
    for i in range(0, COLUMNS, 8):
        print('step', i, [None if np.isnan(x) else round(float(x), 1) for x in grid[i]])
    print('Saved data/samples/sst_check.png and data/sst_grid.csv')