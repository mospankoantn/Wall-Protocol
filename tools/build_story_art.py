"""Procedural art for Wall Protocol 1.4 story mode (numpy + Pillow only).

* spr_ground_marsh / snow / ash / throne : colour-graded, seamless variants of the forest ground tile
  (the detail of the painted original is kept; only the palette and a few periodic features change).
* spr_scene_0 .. spr_scene_4 : silhouette landscapes (1024x576) used behind briefings and epilogues.

Deterministic and idempotent; registers the sprites in `Wall Protocol.yyp`.  Needs spr_ground to exist.
"""
from pathlib import Path
import copy, json, math, re, uuid
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(re.sub(r',\s*([}\]])', r'\1', Path(path).read_text(encoding='utf-8-sig')))


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def periodic_noise(size, seed, falloff=2.0, cutoff=.12):
    """Seamless tileable noise, zero mean / unit std."""
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((size, size)))
    fy = np.fft.fftfreq(size)[:, None]; fx = np.fft.fftfreq(size)[None, :]
    k = np.sqrt(fx ** 2 + fy ** 2); k[0, 0] = 1
    n = np.real(np.fft.ifft2(f / k ** falloff * np.exp(-(k / cutoff) ** 2)))
    return (n - n.mean()) / n.std()


def ground_source():
    d = ROOT / 'sprites' / 'spr_ground'
    png = sorted(p for p in d.glob('*.png'))[0]
    return np.asarray(Image.open(png).convert('RGB'), dtype=float) / 255


def lum(a):
    return (a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11)[..., None]


def tint(a, shadow, light, gamma=1.0, gain=1.0):
    """Map the luminance of the source onto a shadow -> light colour ramp (keeps all painted detail)."""
    l = np.clip(lum(a) / .35, 0, 1.6) ** gamma * gain
    l = np.clip(l, 0, 1)
    s = np.array(shadow) / 255; h = np.array(light) / 255
    return s + (h - s) * l


def finish(a):
    return Image.fromarray(np.round(np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGB').convert('RGBA')


def make_marsh():
    a = ground_source(); n = periodic_noise(512, 31, 2.2, .07)
    base = tint(a, (22, 30, 20), (112, 128, 70), 1.05, 1.0)
    base = base * .55 + (a * np.array([1.15, 1.1, .75])) * .45          # keep some of the original greens, warmed up
    pool = smooth(.8, 1.5, n)[..., None]                               # still water pools
    water = np.array([34, 56, 58]) / 255 * (.7 + .5 * lum(a) / .35)
    sheen = smooth(.2, 1.0, periodic_noise(512, 32, 1.2, .2))[..., None] * .06
    out = base * (1 - pool * .8) + water * pool * .8 + sheen * pool
    return finish(out)


def make_snow():
    a = ground_source(); n = periodic_noise(512, 41, 2.0, .06); rng = np.random.default_rng(42)
    base = tint(a, (64, 80, 104), (196, 211, 228), .85, 1.0)
    drift = (n[..., None] * .045)
    sparkle = (rng.random((512, 512, 1)) > .997) * .35
    out = base + drift + sparkle
    return finish(out)


def make_ash():
    a = ground_source(); n = periodic_noise(512, 51, 1.8, .08)
    base = tint(a, (18, 14, 15), (88, 74, 70), 1.0, 1.0)
    ridge = 1 - np.abs(periodic_noise(512, 52, 1.6, .1))                 # thin crack lines
    cracks = smooth(.955, .993, ridge)[..., None]
    ember = np.array([255, 110, 40]) / 255
    out = base * (1 - cracks * .4) + ember * cracks * .4 * (.4 + .6 * smooth(-.2, 1.2, n))[..., None]
    out += (smooth(0, 1.4, n)[..., None]) * np.array([.05, .02, .015])
    return finish(out)


def make_throne():
    a = ground_source(); n = periodic_noise(512, 61, 1.9, .07)
    base = tint(a, (16, 12, 28), (92, 78, 128), 1.0, 1.0)
    ridge = 1 - np.abs(periodic_noise(512, 62, 1.5, .12))
    veins = smooth(.95, .995, ridge)[..., None]
    glow = np.array([150, 120, 255]) / 255
    out = base + glow * veins * .42 * (.4 + .6 * smooth(-.3, 1.1, n))[..., None]
    return finish(out)


# ------------------------------------------------------------------------------------------ scenes
W, H = 1024, 576


def ridge_line(seed, base, amp, rough=3.0, w=W):
    rng = np.random.default_rng(seed); x = np.linspace(0, 1, w); y = np.zeros(w)
    for o in range(6):
        f = 2 ** o * rough * .5
        y += np.sin(x * f * 2 * math.pi + rng.uniform(0, 6.28)) * amp / (1.7 ** o)
    return base + y


def lerp3(a, b, t):
    return np.array(a) + (np.array(b) - np.array(a)) * t


def scene(spec):
    """spec: sky top/bottom colours, eclipse (x, y, radius, glow colour), layers [(colour, base, amp, seed, rough)],
    extras: list of callables(img_array) for hand-placed silhouettes, fog colour."""
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    t = (yy / H)[..., None]
    img = lerp3(spec['sky'][0], spec['sky'][1], t) / 255.0
    ex, ey, er = spec['eclipse'][:3]; gc = np.array(spec['eclipse'][3]) / 255
    d = np.hypot(xx - ex, yy - ey)
    img += (np.exp(-(d / (er * 3.2)) ** 2) * .55 + np.exp(-(d / (er * 1.5)) ** 2) * .45)[..., None] * gc
    disk = smooth(er + 1.5, er - 1.5, d)                                  # dark disk with bright rim
    rim = np.exp(-((d - er) / 3.0) ** 2)
    img = img * (1 - disk[..., None]) + np.array([5, 5, 10]) / 255 * disk[..., None]
    img += rim[..., None] * gc * 1.1
    rng = np.random.default_rng(spec['seed'])
    for _ in range(spec.get('stars', 90)):                                # faint stars
        sx, sy = rng.integers(0, W), rng.integers(0, int(H * .5))
        if np.hypot(sx - ex, sy - ey) > er * 3:
            img[sy, sx] += rng.uniform(.15, .5)
    for i, (col, base, amp, seed, rough) in enumerate(spec['layers']):
        ridge = ridge_line(seed, base, amp, rough)
        mask = (yy > ridge[None, :])
        fogmix = spec.get('fog_mix', .55) * (1 - i / max(1, len(spec['layers'])))
        c = np.array(col) / 255 * (1 - fogmix * .4) + np.array(spec['fog']) / 255 * fogmix * .4
        img = np.where(mask[..., None], c, img)
    for extra in spec.get('extras', []):
        img = extra(img, xx, yy)
    glow = spec.get('fog')
    low = smooth(H * .55, H, yy)[..., None]
    img = img * (1 - low * .25) + np.array(glow) / 255 * low * .10         # ground haze
    vig = 1 - .55 * smooth(.55, 1.15, np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)))
    img *= vig[..., None]
    out = Image.fromarray(np.round(np.clip(img, 0, 1) * 255).astype(np.uint8), 'RGB')
    return out.filter(ImageFilter.GaussianBlur(.8)).convert('RGBA')


def poly(mask_fn):
    return mask_fn


def shape_tower(cx, base, w, h, col, crown=True):
    def f(img, xx, yy):
        m = (np.abs(xx - cx) < w / 2) & (yy > base - h) & (yy < base + 40)
        if crown:
            m |= (np.abs(xx - cx) < w / 2 + 8) & (yy > base - h - 12) & (yy < base - h + 8)
            for k in (-1, 0, 1):
                m |= (np.abs(xx - (cx + k * w * .38)) < 5) & (yy > base - h - 24) & (yy < base - h)
        img = np.where(m[..., None], np.array(col) / 255, img)
        return img
    return f


def shape_wall(x0, x1, base, h, col):
    def f(img, xx, yy):
        m = (xx > x0) & (xx < x1) & (yy > base - h) & (yy < base + 60)
        n = int((x1 - x0) / 26)
        for k in range(n):
            if k % 2 == 0:
                m |= (xx > x0 + k * 26) & (xx < x0 + k * 26 + 14) & (yy > base - h - 14) & (yy <= base - h)
        return np.where(m[..., None], np.array(col) / 255, img)
    return f


def shape_crystal(cx, base, h, col, glow):
    def f(img, xx, yy):
        rel = (yy - (base - h)) / h
        wid = np.where(rel < 0, 0, np.where(rel < .35, rel / .35 * 22, 22 * (1 - (rel - .35) / .65 * .55)))
        m = (np.abs(xx - cx) < wid) & (rel > 0) & (rel < 1)
        d = np.hypot(xx - cx, yy - (base - h * .5))
        img = img + (np.exp(-(d / (h * .9)) ** 2) * .5)[..., None] * (np.array(glow) / 255)
        return np.where(m[..., None], np.array(col) / 255, img)
    return f


def shape_pines(seed, n, base_lo, base_hi, hmin, hmax, col, xs=(0, W)):
    r = np.random.default_rng(seed)
    pines = [(r.uniform(*xs), r.uniform(base_lo, base_hi), r.uniform(hmin, hmax)) for _ in range(n)]
    def f(img, xx, yy):
        m = np.zeros(xx.shape, bool)
        for px, pb, ph in pines:
            rel = (pb - yy) / ph
            m |= (rel > 0) & (rel < 1) & (np.abs(xx - px) < (1 - rel) * ph * .22 * (1 + .25 * np.sin(rel * 30)))
            m |= (np.abs(xx - px) < 2.5) & (yy > pb - 6) & (yy < pb + 10)
        return np.where(m[..., None], np.array(col) / 255, img)
    return f


def shape_reeds(seed, n, base, h, col):
    r = np.random.default_rng(seed)
    reeds = [(r.uniform(0, W), r.uniform(.5, 1) * h, r.uniform(-.2, .2)) for _ in range(n)]
    def f(img, xx, yy):
        m = np.zeros(xx.shape, bool)
        for rx, rh, lean in reeds:
            rel = (base - yy) / rh
            m |= (rel > 0) & (rel < 1) & (np.abs(xx - (rx + lean * (base - yy))) < 1.8)
        return np.where(m[..., None], np.array(col) / 255, img)
    return f


def shape_lanterns(seed, n, y0, y1, col):
    r = np.random.default_rng(seed)
    pts = [(r.uniform(60, W - 60), r.uniform(y0, y1)) for _ in range(n)]
    def f(img, xx, yy):
        for px, py in pts:
            d = np.hypot(xx - px, yy - py)
            img = img + (np.exp(-(d / 16) ** 2) * .9 + np.exp(-(d / 4) ** 2))[..., None] * np.array(col) / 255
        return img
    return f


def shape_ruins(seed, n, base, col):
    r = np.random.default_rng(seed)
    parts = [(r.uniform(40, W - 40), r.uniform(26, 60), r.uniform(60, 190)) for _ in range(n)]
    def f(img, xx, yy):
        m = np.zeros(xx.shape, bool)
        for px, pw, ph in parts:
            top = base - ph + 14 * np.sin((xx - px) * .21)
            m |= (np.abs(xx - px) < pw / 2) & (yy > top) & (yy < base + 80)
            m |= (np.abs(xx - px) < pw / 2 - 6) & (np.abs(yy - (base - ph * .55)) < 15) & (np.abs(xx - px) < 7) & False
        return np.where(m[..., None], np.array(col) / 255, img)
    return f


def shape_throne(cx, base, col, glow):
    def f(img, xx, yy):
        m = np.zeros(xx.shape, bool)
        m |= (np.abs(xx - cx) < 120 - (base - yy) * .35) & (yy > base - 70) & (yy < base + 90)               # stepped dais
        m |= (np.abs(xx - cx) < 46) & (yy > base - 250) & (yy < base - 60)                                    # high back
        m |= (np.abs(xx - cx) < 22 - (base - 250 - yy) * 0.0) & (yy > base - 320) & (yy < base - 250)
        for dx in (-70, 70):
            m |= (np.abs(xx - (cx + dx)) < 12) & (yy > base - 190) & (yy < base - 60)
        d = np.hypot(xx - cx, yy - (base - 150))
        img = img + (np.exp(-(d / 130) ** 2) * .22)[..., None] * np.array(glow) / 255
        return np.where(m[..., None], np.array(col) / 255, img)
    return f


SCENES = {
    0: dict(seed=1, sky=((10, 22, 34), (46, 60, 70)), eclipse=(730, 150, 54, (92, 207, 204)), fog=(110, 150, 160), stars=110,
            layers=[((24, 36, 46), 330, 26, 3, 2.0), ((16, 26, 32), 400, 20, 4, 3.0), ((9, 15, 19), 470, 12, 5, 4.0)],
            extras=[shape_wall(330, 560, 462, 82, (7, 11, 14)), shape_tower(330, 462, 44, 150, (7, 11, 14)), shape_tower(560, 462, 44, 130, (7, 11, 14)),
                    shape_crystal(445, 468, 74, (130, 235, 235), (92, 207, 204)), shape_pines(8, 14, 520, 570, 90, 170, (4, 7, 9))]),
    1: dict(seed=2, sky=((12, 24, 22), (58, 78, 62)), eclipse=(260, 170, 48, (150, 230, 120)), fog=(130, 175, 135), stars=60,
            layers=[((30, 46, 38), 360, 22, 13, 2.5), ((20, 32, 26), 425, 16, 14, 3.5), ((10, 17, 14), 490, 10, 15, 5.0)],
            extras=[shape_pines(21, 7, 440, 500, 90, 160, (8, 14, 11), (0, W)), shape_reeds(22, 170, 560, 110, (5, 9, 7)), shape_lanterns(23, 7, 400, 500, (170, 255, 140))]),
    2: dict(seed=3, sky=((14, 22, 40), (92, 112, 140)), eclipse=(620, 130, 58, (170, 210, 255)), fog=(190, 215, 240), stars=130,
            layers=[((118, 138, 168), 250, 70, 33, 2.2), ((68, 86, 112), 340, 46, 34, 3.0), ((30, 40, 58), 430, 24, 35, 4.0), ((12, 18, 28), 500, 12, 36, 5.0)],
            extras=[shape_pines(31, 30, 520, 580, 80, 190, (6, 9, 15))]),
    3: dict(seed=4, sky=((26, 12, 14), (110, 52, 40)), eclipse=(790, 190, 60, (255, 150, 80)), fog=(200, 120, 90), stars=70,
            layers=[((70, 34, 30), 360, 30, 43, 2.0), ((40, 20, 20), 430, 20, 44, 3.0), ((16, 9, 10), 500, 10, 45, 4.0)],
            extras=[shape_ruins(41, 12, 470, (12, 7, 8)), shape_wall(120, 330, 478, 74, (8, 5, 6)), shape_tower(690, 482, 60, 190, (8, 5, 6), True), shape_tower(780, 482, 38, 120, (8, 5, 6), True),
                    shape_lanterns(42, 6, 440, 530, (255, 160, 80))]),
    4: dict(seed=5, sky=((16, 8, 30), (70, 40, 110)), eclipse=(512, 205, 92, (180, 130, 255)), fog=(150, 110, 210), stars=150,
            layers=[((48, 28, 80), 370, 36, 53, 2.0), ((28, 16, 50), 440, 22, 54, 3.0), ((10, 6, 18), 505, 10, 55, 4.0)],
            extras=[shape_throne(512, 470, (6, 4, 11), (190, 140, 255)), shape_ruins(51, 8, 495, (7, 4, 12)), shape_lanterns(52, 8, 420, 540, (200, 150, 255))]),
}


# ------------------------------------------------------------------------------------------ registration
def write_sprite(name, im, origin_center=False):
    template = read(ROOT / 'sprites/spr_button/spr_button.yy')
    data = copy.deepcopy(template); w, h = im.size
    data['%Name'] = data['name'] = name
    data.update(width=w, height=h, bbox_left=0, bbox_right=w - 1, bbox_top=0, bbox_bottom=h - 1, origin=4 if origin_center else 0)
    layer = str(uuid.uuid5(uuid.NAMESPACE_URL, f'wallprotocol/{name}/layer'))
    frame = str(uuid.uuid5(uuid.NAMESPACE_URL, f'wallprotocol/{name}/frame'))
    data['layers'][0].update({'%Name': layer, 'name': layer})
    seq = data['sequence']; seq['%Name'] = seq['name'] = name; seq['length'] = 1.0; seq['playbackSpeed'] = 5
    seq['xorigin'], seq['yorigin'] = (w // 2, h // 2) if origin_center else (0, 0)
    data['frames'] = [{'$GMSpriteFrame': 'v1', '%Name': frame, 'name': frame, 'resourceType': 'GMSpriteFrame', 'resourceVersion': '2.0'}]
    directory = ROOT / 'sprites' / name
    for old in directory.rglob('*.png') if directory.exists() else []:
        old.unlink()
    (directory / 'layers' / frame).mkdir(parents=True, exist_ok=True)
    im.save(directory / f'{frame}.png'); im.save(directory / 'layers' / frame / f'{layer}.png')
    key = str(uuid.uuid5(uuid.NAMESPACE_URL, f'wallprotocol/{name}/key'))
    seq['tracks'][0]['keyframes']['Keyframes'] = [{'$Keyframe<SpriteFrameKeyframe>': '', 'Channels': {'0': {'$SpriteFrameKeyframe': '', 'Id': {'name': frame, 'path': f'sprites/{name}/{name}.yy'}, 'resourceType': 'SpriteFrameKeyframe', 'resourceVersion': '2.0'}}, 'Disabled': False, 'id': key, 'IsCreationKey': False, 'Key': 0.0, 'Length': 1.0, 'resourceType': 'Keyframe<SpriteFrameKeyframe>', 'resourceVersion': '2.0', 'Stretch': False}]
    data['parent'] = {'name': 'Art', 'path': 'folders/Art.yy'}
    (directory / f'{name}.yy').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def register(names):
    path = ROOT / 'Wall Protocol.yyp'; text = path.read_text(encoding='utf-8')
    for name in names:
        if f'"name":"{name}"' in text:
            continue
        line = f'    {{"id":{{"name":"{name}","path":"sprites/{name}/{name}.yy",}},}},\n'
        existing = sorted(re.findall(r'^    \{"id":\{"name":"(spr_\w+)"', text, re.M)); later = [s for s in existing if s > name]
        if later:
            anchor = f'    {{"id":{{"name":"{later[0]}"'; text = text.replace(anchor, line + anchor, 1)
        else:
            m = re.search(rf'^    \{{"id":\{{"name":"{existing[-1]}".*\n', text, re.M); text = text[:m.end()] + line + text[m.end():]
    path.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    made = {'spr_ground_marsh': make_marsh, 'spr_ground_snow': make_snow, 'spr_ground_ash': make_ash, 'spr_ground_throne': make_throne}
    for name, fn in made.items():
        write_sprite(name, fn())
    for i, spec in SCENES.items():
        write_sprite(f'spr_scene_{i}', scene(spec))
    register(list(made) + [f'spr_scene_{i}' for i in SCENES])
    print('wrote', ', '.join(list(made) + [f'spr_scene_{i}' for i in SCENES]))
