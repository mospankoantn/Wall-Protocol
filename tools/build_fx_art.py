"""Procedural effect sprites for Wall Protocol 1.3 (white + alpha, tinted in GML via image_blend).

Creates seven native GameMaker sprites and registers them in `Wall Protocol.yyp`:

    spr_glow      soft round light (additive blend)
    spr_flare     four-point sparkle
    spr_ring      soft expanding shock-wave ring
    spr_runering  rune circle drawn on the ground under towers / pads
    spr_puff      irregular soft puff (smoke, dust)
    spr_mist      tileable fog noise
    spr_vignette  dark edge gradient for the battlefield

Deterministic and idempotent: re-running rewrites the same PNGs and does not duplicate entries.
Requires numpy and Pillow only. Does not touch any existing sprite.
"""
from pathlib import Path
import copy, json, math, re, uuid
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(1303)


def grid(w, h=None):
    h = h or w
    y, x = np.mgrid[0:h, 0:w].astype(float)
    return (x - (w - 1) / 2) / (w / 2), (y - (h - 1) / 2) / (h / 2)


def rgba(alpha):
    a = np.clip(alpha, 0, 1)
    out = np.zeros(a.shape + (4,), dtype=np.uint8)
    out[..., :3] = 255
    out[..., 3] = np.round(a * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def make_glow():
    x, y = grid(128); r = np.hypot(x, y)
    return rgba((np.exp(-(r / .40) ** 2) * .8 + np.exp(-(r / .8) ** 2) * .3) * (1 - smooth(.78, 1.0, r)))


def make_flare():
    x, y = grid(96); r = np.hypot(x, y)
    core = np.exp(-(r / .12) ** 2)
    h = np.exp(-(y / .035) ** 2) * np.exp(-(np.abs(x) / .55) ** 1.4)
    v = np.exp(-(x / .035) ** 2) * np.exp(-(np.abs(y) / .55) ** 1.4)
    u, w = (x + y) / 1.414, (x - y) / 1.414
    d = (np.exp(-(w / .03) ** 2) * np.exp(-(np.abs(u) / .28) ** 1.6) + np.exp(-(u / .03) ** 2) * np.exp(-(np.abs(w) / .28) ** 1.6)) * .55
    halo = np.exp(-(r / .3) ** 2) * .35
    return rgba((core + h + v + d + halo) * (1 - smooth(.85, 1.0, r)))


def make_ring():
    x, y = grid(128); r = np.hypot(x, y)
    return rgba((np.exp(-((r - .74) / .055) ** 2) + np.exp(-((r - .74) / .2) ** 2) * .18) * (1 - smooth(.88, 1.0, r)))


def make_runering():
    S, big = 160, 4; N = S * big; img = Image.new('L', (N, N), 0); d = ImageDraw.Draw(img); c = N / 2
    def circ(rad, width, fill=255):
        d.ellipse((c - rad * c, c - rad * c, c + rad * c, c + rad * c), outline=fill, width=int(width * big))
    circ(.96, 1.6); circ(.89, 1.0, 190); circ(.50, 1.2, 200); circ(.30, 1.0, 150)
    for i in range(48):                                   # outer tick marks
        a = i / 48 * 2 * math.pi; r0, r1 = (.89, .93) if i % 4 else (.84, .94)
        d.line((c + math.cos(a) * r0 * c, c + math.sin(a) * r0 * c, c + math.cos(a) * r1 * c, c + math.sin(a) * r1 * c), fill=230 if i % 4 == 0 else 150, width=int(1.2 * big))
    for k in range(6):                                    # broken inner arc ring
        a0 = k * 60 + 8; d.arc((c - .74 * c, c - .74 * c, c + .74 * c, c + .74 * c), a0, a0 + 38, fill=235, width=int(1.8 * big))
    for k in range(8):                                    # diamond glyphs between the rings
        a = k / 8 * 2 * math.pi + math.pi / 8; px, py = c + math.cos(a) * .63 * c, c + math.sin(a) * .63 * c; s = .055 * c
        d.polygon([(px, py - s), (px + s * .7, py), (px, py + s), (px - s * .7, py)], outline=255, fill=120)
    for ph in (0, math.pi / 6):                           # hexagram
        pts = [(c + math.cos(ph + k * 2 * math.pi / 3 - math.pi / 2) * .5 * c, c + math.sin(ph + k * 2 * math.pi / 3 - math.pi / 2) * .5 * c) for k in range(3)]
        d.polygon(pts, outline=190)
    a = np.asarray(img.resize((S, S), Image.Resampling.LANCZOS), dtype=float) / 255
    return rgba(a * .95)


def fbm(w, h, octaves, seed, base=4):
    r = np.random.default_rng(seed); out = np.zeros((h, w)); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o
        small = r.random((n, n))
        big = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BICUBIC), dtype=float) / 255
        out += big * amp; tot += amp; amp *= .5
    return out / tot


def make_puff():
    x, y = grid(64); r = np.hypot(x, y); n = fbm(64, 64, 4, 5, 3)
    return rgba(np.clip((1 - r * 1.05), 0, 1) ** 1.3 * (.45 + .9 * n) * .9)


def make_mist():
    S = 256; white = rng.standard_normal((S, S)); f = np.fft.fft2(white)
    fy = np.fft.fftfreq(S)[:, None]; fx = np.fft.fftfreq(S)[None, :]; k = np.sqrt(fx ** 2 + fy ** 2); k[0, 0] = 1
    n = np.real(np.fft.ifft2(f / k ** 1.95 * np.exp(-(k / .12) ** 2))); n = (n - n.mean()) / n.std()   # periodic -> tileable, soft
    return rgba(smooth(-1.6, 2.4, n) * .8)


def make_vignette():
    w, h = 256, 144; x, y = grid(w, h); d = (np.abs(x) ** 2.4 + np.abs(y) ** 2.4) ** (1 / 2.4)
    a = np.clip((d - .52) / .62, 0, 1) ** 1.7
    img = np.zeros((h, w, 4), dtype=np.uint8); img[..., 3] = np.round(np.clip(a, 0, 1) * 255)
    return Image.fromarray(img, 'RGBA')


# --------------------------------------------------------------------------- registration
def read(path):
    return json.loads(re.sub(r',\s*([}\]])', r'\1', Path(path).read_text(encoding='utf-8-sig')))


def write_sprite(name, im, origin_center=True):
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
    for old in directory.rglob('*.png') if directory.exists() else []: old.unlink()
    (directory / 'layers' / frame).mkdir(parents=True, exist_ok=True)
    im.save(directory / f'{frame}.png'); im.save(directory / 'layers' / frame / f'{layer}.png')
    key = str(uuid.uuid5(uuid.NAMESPACE_URL, f'wallprotocol/{name}/key'))
    seq['tracks'][0]['keyframes']['Keyframes'] = [{'$Keyframe<SpriteFrameKeyframe>': '', 'Channels': {'0': {'$SpriteFrameKeyframe': '', 'Id': {'name': frame, 'path': f'sprites/{name}/{name}.yy'}, 'resourceType': 'SpriteFrameKeyframe', 'resourceVersion': '2.0'}}, 'Disabled': False, 'id': key, 'IsCreationKey': False, 'Key': 0.0, 'Length': 1.0, 'resourceType': 'Keyframe<SpriteFrameKeyframe>', 'resourceVersion': '2.0', 'Stretch': False}]
    data['parent'] = {'name': 'Art', 'path': 'folders/Art.yy'}
    (directory / f'{name}.yy').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def register(names):
    path = ROOT / 'Wall Protocol.yyp'; text = path.read_text(encoding='utf-8')
    for name in names:
        if f'"name":"{name}"' in text: continue
        line = f'    {{"id":{{"name":"{name}","path":"sprites/{name}/{name}.yy",}},}},\n'
        existing = sorted(re.findall(r'^    \{"id":\{"name":"(spr_\w+)"', text, re.M)); later = [s for s in existing if s > name]
        if later: anchor = f'    {{"id":{{"name":"{later[0]}"'; text = text.replace(anchor, line + anchor, 1)
        else:
            m = re.search(rf'^    \{{"id":\{{"name":"{existing[-1]}".*\n', text, re.M); text = text[:m.end()] + line + text[m.end():]
    path.write_text(text, encoding='utf-8', newline='\n')


SPRITES = {'spr_glow': make_glow, 'spr_flare': make_flare, 'spr_ring': make_ring, 'spr_runering': make_runering,
           'spr_puff': make_puff, 'spr_mist': make_mist, 'spr_vignette': make_vignette}

if __name__ == '__main__':
    for name, make in SPRITES.items():
        write_sprite(name, make(), origin_center=(name != 'spr_vignette'))
    register(list(SPRITES))
    print('wrote', ', '.join(SPRITES))
