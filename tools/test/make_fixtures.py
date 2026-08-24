"""Synthetic frames that look like what the phone will actually see:
white stickers carrying markers, stuck near the corners of a model,
sitting on a tray, shot from above with some perspective."""
import json, os
import cv2, numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
os.makedirs(OUT, exist_ok=True)
D = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
rng = np.random.default_rng(7)


def sticker(marker_id, marker_px):
    """A marker on its white quiet zone, same 10mm-on-16mm ratio as the sheet."""
    quiet = max(2, round(marker_px * 3.0 / 9.91))
    side = marker_px + quiet * 2
    tile = np.full((side, side), 255, np.uint8)
    m = cv2.aruco.generateImageMarker(D, marker_id, marker_px, borderBits=1)
    tile[quiet:quiet + marker_px, quiet:quiet + marker_px] = m
    return tile, quiet


def scene(w, h, marker_px, model_rect, warp, blur=0, noise=0, vignette=0.0, bg=90):
    """Lay four stickers on the corners of model_rect, then warp the whole
    plane so the model sits at an arbitrary pose under the camera."""
    img = np.full((h, w), bg, np.uint8)
    x0, y0, x1, y1 = model_rect
    cv2.rectangle(img, (x0, y0), (x1, y1), 205, -1)          # the model body
    for i in range(6):                                        # some vessel-ish clutter
        p = (rng.integers(x0 + 40, x1 - 40), rng.integers(y0 + 40, y1 - 40))
        q = (rng.integers(x0 + 40, x1 - 40), rng.integers(y0 + 40, y1 - 40))
        cv2.line(img, tuple(map(int, p)), tuple(map(int, q)), 120, 7)

    tile, quiet = sticker(0, marker_px)
    side = tile.shape[0]
    inset = side // 2 + 6
    spots = {0: (x0 + inset, y0 + inset), 1: (x1 - inset, y0 + inset),
             2: (x1 - inset, y1 - inset), 3: (x0 + inset, y1 - inset)}
    truth = {}
    for mid, (cx, cy) in spots.items():
        tile, quiet = sticker(mid, marker_px)
        a, b = cy - side // 2, cx - side // 2
        img[a:a + side, b:b + side] = tile
        truth[mid] = (float(cx), float(cy))

    if warp is not None:
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        H = cv2.getPerspectiveTransform(src, np.float32(warp))
        img = cv2.warpPerspective(img, H, (w, h), borderValue=bg)
        for mid, (cx, cy) in truth.items():
            p = H @ np.array([cx, cy, 1.0])
            truth[mid] = (float(p[0] / p[2]), float(p[1] / p[2]))

    if vignette:
        yy, xx = np.mgrid[0:h, 0:w]
        r = np.hypot(xx - w / 2, yy - h / 2) / np.hypot(w / 2, h / 2)
        img = np.clip(img * (1 - vignette * r ** 2), 0, 255).astype(np.uint8)
    if blur:
        img = cv2.GaussianBlur(img, (blur | 1, blur | 1), 0)
    if noise:
        img = np.clip(img.astype(np.int16) + rng.normal(0, noise, img.shape), 0, 255).astype(np.uint8)
    return img, truth


CASES = {}


def add(name, **kw):
    img, truth = scene(**kw)
    cv2.imwrite(f"{OUT}/{name}.png", img)
    CASES[name] = truth


# 1920x1080 with a 49px marker is the real budget: 28cm from an iPhone
# main camera across the inside of the box.
add("flat", w=1920, h=1080, marker_px=49, model_rect=(430, 150, 1490, 930), warp=None)
add("tilted", w=1920, h=1080, marker_px=49, model_rect=(430, 150, 1490, 930),
    warp=[[120, 40], [1810, 150], [1700, 1040], [210, 950]])
add("rotated", w=1920, h=1080, marker_px=49, model_rect=(560, 210, 1360, 870),
    warp=[[430, 60], [1830, 430], [1470, 1020], [80, 640]])
add("noisy", w=1920, h=1080, marker_px=49, model_rect=(430, 150, 1490, 930),
    warp=[[150, 60], [1780, 130], [1690, 1010], [230, 970]], blur=3, noise=6)
add("vignette", w=1920, h=1080, marker_px=49, model_rect=(430, 150, 1490, 930),
    warp=None, vignette=0.55, blur=3)
add("small", w=1920, h=1080, marker_px=30, model_rect=(430, 150, 1490, 930), warp=None)
add("uhd", w=3840, h=2160, marker_px=99, model_rect=(860, 300, 2980, 1860), warp=None)

json.dump(CASES, open(f"{OUT}/truth.json", "w"), indent=1)
print(json.dumps({k: sorted(v) for k, v in CASES.items()}, indent=0)[:200])
print("wrote", len(CASES), "fixtures")

# --- robustness / negative cases -------------------------------------------
def write(name, img, truth):
    cv2.imwrite(f"{OUT}/{name}.png", img); CASES[name] = truth

# clutter with no markers at all: must not invent any
img = np.full((1080, 1920), 90, np.uint8)
cv2.rectangle(img, (430, 150), (1490, 930), 205, -1)
for _ in range(40):
    p = tuple(int(v) for v in rng.integers([440, 160], [1480, 920]))
    q = tuple(int(v) for v in rng.integers([440, 160], [1480, 920]))
    cv2.rectangle(img, p, q, int(rng.integers(0, 255)), int(rng.choice([-1, 3])))
write("clutter", img, {})

# white tray: the sticker's quiet zone merges into the background, so the
# black square has to survive on its own
img, truth = scene(1920, 1080, 49, (430, 150, 1490, 930), None, bg=235)
write("whitebg", img, truth)

# one marker hidden by a hand: expect the other three, no crash
img, truth = scene(1920, 1080, 49, (430, 150, 1490, 930), None)
cv2.circle(img, (int(truth[2][0]), int(truth[2][1])), 70, 40, -1)
del truth[2]
write("occluded", img, truth)

json.dump(CASES, open(f"{OUT}/truth.json", "w"), indent=1)
print("total fixtures:", len(CASES))
