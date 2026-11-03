"""Story-mode map authoring for Wall Protocol 1.4.

Single source of truth for the four extra maps (ids 1-4; id 0 is the room-authored forest map).
Running this tool:
  * auto-places build pads (greedy coverage of the road) and decorations (seeded, deterministic);
  * checks geometry (pads/decor clear of the road, spacing, field bounds, core/portal visibility);
  * writes scripts/scr_maps/scr_maps.gml (map data + themes) and registers the script in the .yyp;
  * renders previews to docs/maps/*.png and a coverage report (--report).

Requires numpy and Pillow only.  Deterministic and idempotent.
"""
from pathlib import Path
import json, math, random, re, sys, uuid

ROOT = Path(__file__).resolve().parents[1]
FIELD = (0, 77, 1060, 696)                 # playable rectangle (HUD covers the rest)
ROAD_HALF = 39                              # outer road pass is 78 px wide
TOWER_RANGE = 175                           # ballista, level 1 (for the coverage metric)
SPR_R = {0: 50, 1: 38, 2: 30, 3: 46, 4: 26}  # rough collision radius of decor sprites
TREE, ROCKS, BRAZIER, WALL, GRAVE = range(5)

MAP0 = dict(route=[(70, 385), (145, 385), (145, 210), (350, 210), (350, 525), (560, 525), (560, 300), (775, 300), (775, 475), (965, 475)],
            pads=[(84, 266), (248, 320), (250, 116), (454, 159), (460, 406), (469, 635), (660, 413), (670, 203), (870, 203), (885, 365), (891, 611), (711, 619)],
            core=(966, 475), portal=(70, 385))

# --------------------------------------------------------------------------------------------- maps
MAPS = {
    1: dict(
        key='mirewood', name_en='Mirewood Ford', name_uk='Туманний Брід', seed=11, pad_count=12,
        route=[(60, 150), (230, 150), (330, 255), (205, 360), (330, 470), (500, 560), (650, 465), (585, 335), (725, 215), (880, 275), (905, 430), (810, 560), (940, 610)],
        decor=dict(tree=15, rocks=4, grave=3, brazier=0), core_guards=2,
        theme=dict(ground='spr_ground_marsh', blend=(190, 200, 190), road=[(14, 22, 20), (50, 58, 50), (70, 76, 62)], stone=[(54, 62, 54), (82, 88, 74)],
                   fog=[(150, 190, 150), (120, 165, 140)], fog_a=[.16, .11], mote=[(150, 230, 120), (92, 207, 204)], weather=3, tree=(170, 195, 165))),
    2: dict(
        key='frostline', name_en='Frostline Pass', name_uk='Крижаний Перевал', seed=23, pad_count=12,
        route=[(1000, 140), (800, 205), (630, 135), (430, 215), (235, 140), (105, 265), (300, 365), (520, 305), (740, 380), (570, 490), (345, 520), (190, 610), (430, 650), (740, 610), (940, 520)],
        decor=dict(tree=9, rocks=10, grave=0, brazier=0), core_guards=2,
        theme=dict(ground='spr_ground_snow', blend=(175, 185, 200), road=[(40, 52, 66), (88, 104, 120), (118, 134, 148)], stone=[(98, 112, 126), (150, 166, 180)],
                   fog=[(200, 225, 245), (170, 205, 235)], fog_a=[.14, .10], mote=[(210, 235, 255), (150, 210, 255)], weather=1, tree=(190, 215, 235))),
    3: dict(
        key='ashen', name_en='Ashen Citadel', name_uk='Попелясте Місто', seed=37, pad_count=13,
        route=[(60, 640), (420, 640), (420, 500), (125, 500), (125, 240), (440, 240), (440, 365), (700, 365), (700, 165), (925, 165), (925, 440), (955, 440)],
        decor=dict(tree=4, rocks=5, grave=6, brazier=0, wall=9), core_guards=2,
        theme=dict(ground='spr_ground_ash', blend=(205, 190, 185), road=[(18, 14, 15), (58, 48, 48), (84, 70, 66)], stone=[(64, 52, 50), (98, 82, 76)],
                   fog=[(210, 150, 120), (150, 110, 100)], fog_a=[.12, .09], mote=[(255, 150, 70), (255, 205, 130)], weather=2, tree=(95, 82, 82))),
    4: dict(
        key='throne', name_en='The Hollow Throne', name_uk='Порожній Трон', seed=53, pad_count=14,
        route=[(70, 135), (990, 135), (990, 650), (70, 650), (70, 300), (745, 300), (745, 500), (335, 500), (335, 400), (500, 400)],
        decor=dict(tree=0, rocks=5, grave=8, brazier=0, wall=8), core_guards=0,
        theme=dict(ground='spr_ground_throne', blend=(200, 185, 215), road=[(14, 11, 22), (48, 42, 62), (74, 66, 92)], stone=[(54, 48, 72), (92, 82, 116)],
                   fog=[(170, 140, 220), (120, 95, 180)], fog_a=[.15, .11], mote=[(190, 140, 255), (92, 207, 204)], weather=4, tree=(110, 100, 130))),
}
KIND = dict(tree=TREE, rocks=ROCKS, brazier=BRAZIER, wall=WALL, grave=GRAVE)


# --------------------------------------------------------------------------------------------- geometry
def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    sq = dx * dx + dy * dy
    t = 0 if sq == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / sq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def route_dist(p, route):
    return min(seg_dist(p, route[i], route[i + 1]) for i in range(len(route) - 1))


def samples(route, step=8):
    out = []
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    out.append(route[-1])
    return out


def route_length(route):
    return sum(math.dist(route[i], route[i + 1]) for i in range(len(route) - 1))


def exposure(pad, pts, rng=TOWER_RANGE, step=8):
    return sum(step for q in pts if math.dist(pad, q) <= rng)


def place_pads(route, core, portal, count, taken_extra=()):
    pts = samples(route)
    cands = []
    for x in range(52, 1010, 10):
        for y in range(112, 668, 10):
            d = route_dist((x, y), route)
            if 64 <= d <= 120 and math.dist((x, y), core) > 105 and math.dist((x, y), portal) > 90:
                cands.append((x, y))
    counts = [0] * len(pts)
    w = [1.0, .55, .3, .12]
    chosen = []
    for _ in range(count):
        best, best_gain = None, -1
        for c in cands:
            if any(math.dist(c, p) < 92 for p in chosen) or any(math.dist(c, p) < 70 for p in taken_extra):
                continue
            gain = sum(w[min(counts[i], 3)] for i, q in enumerate(pts) if math.dist(c, q) <= TOWER_RANGE)
            if gain > best_gain + 1e-9:
                best, best_gain = c, gain
        if best is None:
            break
        chosen.append(best)
        for i, q in enumerate(pts):
            if math.dist(best, q) <= TOWER_RANGE:
                counts[i] += 1
    return chosen


def place_decor(m, pads, core, portal, route):
    rnd = random.Random(m['seed'])
    items = []
    # braziers flank the core, perpendicular to the last road segment
    a, b = route[-2], route[-1]
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    px, py = -math.sin(ang), math.cos(ang)
    dx, dy = math.cos(ang), math.sin(ang)
    def free_of_pads(x, y): return all(math.dist((x, y), p) >= 70 for p in pads)
    for s in (-1, 1) if m['core_guards'] else ():
        x, y = round(core[0] + px * 100 * s - dx * 25), round(core[1] + py * 100 * s - dy * 25)
        if free_of_pads(x, y) and FIELD[1] + 30 < y < FIELD[3] - 10: items.append((BRAZIER, x, y))
    for s in (-1, 1) if m['key'] in ('mirewood', 'frostline', 'ashen') else ():
        x, y = round(portal[0] + (62 if portal[0] < 500 else -62)), round(portal[1] + 88 * s)
        if free_of_pads(x, y) and 100 < y < 680: items.append((GRAVE if m['key'] != 'frostline' else ROCKS, x, y))
    todo = []
    for name, n in m['decor'].items():
        todo += [KIND[name]] * n
    rnd.shuffle(todo)
    for kind in todo:
        r = SPR_R[kind]
        for _try in range(600):
            x, y = rnd.randint(25, 1040), rnd.randint(90, 690)
            if route_dist((x, y), route) < ROAD_HALF + r + 14:
                continue
            if any(math.dist((x, y), p) < max(62, r + 46) for p in pads):
                continue
            if math.dist((x, y), core) < r + 110 or math.dist((x, y), portal) < r + 80:
                continue
            if any(math.dist((x, y), (ix, iy)) < (r + SPR_R[ik]) * .8 + (14 if kind != TREE or ik != TREE else -12) for ik, ix, iy in items):
                continue
            items.append((kind, x, y))
            break
    return items


def build():
    out = {}
    for mid, m in MAPS.items():
        route = list(m['route']); core = route[-1]; portal = route[0]
        pads = place_pads(route, core, portal, m['pad_count'])
        decor = place_decor(m, pads, core, portal, route)
        out[mid] = dict(m, core=core, portal=portal, pads=pads, decor=decor)
    return out


# --------------------------------------------------------------------------------------------- checks
def check(maps):
    problems = []
    for mid, m in maps.items():
        route, pads, decor = m['route'], m['pads'], m['decor']
        tag = f"map {mid} ({m['key']})"
        for x, y in route:
            if not (30 <= x <= 1030 and 100 <= y <= 672):
                problems.append(f'{tag}: node {x},{y} outside the field')
        cx, cy = m['core']
        if not (80 <= cx <= 985 and 150 <= cy <= 620):
            problems.append(f'{tag}: core sprite would leave the field ({cx},{cy})')
        if len(pads) != m['pad_count']:
            problems.append(f"{tag}: only {len(pads)} of {m['pad_count']} pads placed")
        for i, p in enumerate(pads):
            d = route_dist(p, route)
            if d < 60:
                problems.append(f'{tag}: pad {i} only {d:.0f}px from the road')
            if not (45 <= p[0] <= 1015 and 105 <= p[1] <= 668):
                problems.append(f'{tag}: pad {i} out of bounds {p}')
            for j in range(i):
                if math.dist(p, pads[j]) < 85:
                    problems.append(f'{tag}: pads {i} and {j} too close')
        for k, x, y in decor:
            if k in (TREE, ROCKS, WALL, GRAVE) and route_dist((x, y), route) < ROAD_HALF + SPR_R[k] * .5:
                problems.append(f'{tag}: decor {k} at {x},{y} sits on the road')
            for p in pads:
                if math.dist((x, y), p) < 52:
                    problems.append(f'{tag}: decor {k} at {x},{y} covers a pad')
        # self-intersection of the road would make a confusing map
        for i in range(len(route) - 1):
            for j in range(i + 2, len(route) - 1):
                if seg_cross(route[i], route[i + 1], route[j], route[j + 1]):
                    problems.append(f'{tag}: road segments {i} and {j} cross')
    return problems


def seg_cross(a, b, c, d):
    def o(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def report(maps):
    base_pts = samples(MAP0['route'])
    base = sum(exposure(p, base_pts) for p in MAP0['pads'])
    print(f"map 0 forest   route {route_length(MAP0['route']):5.0f}px  pads {len(MAP0['pads']):2d}  total tower exposure {base:6.0f}px  (avg {base/len(MAP0['pads']):.0f}/pad)")
    for mid, m in maps.items():
        pts = samples(m['route'])
        tot = sum(exposure(p, pts) for p in m['pads'])
        print(f"map {mid} {m['key']:9s} route {route_length(m['route']):5.0f}px  pads {len(m['pads']):2d}  total tower exposure {tot:6.0f}px  (avg {tot/len(m['pads']):.0f}/pad)  decor {len(m['decor'])}")
    print('map 0 clearance check (calibration): min pad-road', round(min(route_dist(p, MAP0['route']) for p in MAP0['pads'])))


# --------------------------------------------------------------------------------------------- preview
def sprite_png(name):
    d = ROOT / 'sprites' / name
    for f in sorted(d.glob('*.png')):
        return f
    return None


def preview(maps):
    from PIL import Image, ImageDraw
    out = ROOT / 'docs' / 'maps'; out.mkdir(parents=True, exist_ok=True)
    allmaps = {0: dict(MAP0, key='forest', theme=dict(ground='spr_ground', blend=(155, 175, 175), road=[(16, 26, 29), (53, 63, 63), (73, 79, 75)], tree=(255, 255, 255)),
                        decor=[(TREE, 65, 110), (TREE, 167, 93), (ROCKS, 360, 100), (TREE, 553, 110), (TREE, 601, 150), (TREE, 752, 120), (TREE, 958, 156), (TREE, 1002, 261), (TREE, 84, 555), (TREE, 170, 607), (TREE, 280, 669), (TREE, 554, 687), (TREE, 1000, 641), (TREE, 52, 696), (BRAZIER, 970, 350), (BRAZIER, 1000, 542), (WALL, 975, 420), (WALL, 975, 595), (ROCKS, 243, 454), (ROCKS, 669, 517), (GRAVE, 393, 650)])}
    allmaps.update(maps)
    names = ['spr_tree', 'spr_rocks', 'spr_brazier', 'spr_wall', 'spr_grave']
    for mid, m in allmaps.items():
        t = m['theme']
        gp = sprite_png(t['ground']) or sprite_png('spr_ground')
        g = Image.open(gp).convert('RGB')
        W, H = 1060, 768
        base = Image.new('RGB', (W, H))
        for ty in range(0, H, 512):
            for tx in range(0, W, 512):
                base.paste(g, (tx, ty))
        bl = t['blend']
        base = Image.merge('RGB', [c.point(lambda v, k=k: v * k // 255) for c, k in zip(base.split(), bl)])
        dr = ImageDraw.Draw(base, 'RGBA')
        route = m['route']
        for pas, w in enumerate((78, 65, 51)):
            col = tuple(t['road'][pas])
            for i in range(len(route) - 1):
                dr.line([route[i], route[i + 1]], fill=col, width=w)
                dr.ellipse([route[i][0] - w / 2, route[i][1] - w / 2, route[i][0] + w / 2, route[i][1] + w / 2], fill=col)
            e = route[-1]; dr.ellipse([e[0] - w / 2, e[1] - w / 2, e[0] + w / 2, e[1] + w / 2], fill=col)
        for p in m['pads']:
            dr.ellipse([p[0] - 37, p[1] - 37, p[0] + 37, p[1] + 37], outline=(213, 175, 101, 220), width=2, fill=(213, 175, 101, 40))
        items = [(k, x, y) for k, x, y in m['decor']]
        items.sort(key=lambda it: it[2])
        for k, x, y in items:
            f = sprite_png(names[k])
            if f:
                im = Image.open(f).convert('RGBA')
                if k == TREE and t.get('tree') and tuple(t['tree']) != (255, 255, 255):
                    r, gg, b, a = im.split(); tr = t['tree']
                    im = Image.merge('RGBA', (r.point(lambda v: v * tr[0] // 255), gg.point(lambda v: v * tr[1] // 255), b.point(lambda v: v * tr[2] // 255), a))
                base.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)
        for name, pos in (('spr_portal', m['portal']), ('spr_core', m['core'])):
            f = sprite_png(name)
            if f:
                im = Image.open(f).convert('RGBA'); base.paste(im, (int(pos[0] - im.width / 2), int(pos[1] - im.height / 2)), im)
        # HUD zones
        dr = ImageDraw.Draw(base, 'RGBA')
        dr.rectangle([0, 0, W, 77], fill=(10, 18, 25, 200)); dr.rectangle([0, 696, W, H], fill=(10, 18, 25, 200))
        base.save(out / f'map{mid}_{m["key"]}.png')


# --------------------------------------------------------------------------------------------- GML emission
def gml_color(c): return f'make_color_rgb({c[0]},{c[1]},{c[2]})'


def emit(maps):
    L = ['/// GENERATED by tools/story_maps.py - edit the tool, not this file.',
         '/// Map 0 is the room-authored forest map; maps 1-4 are applied over the room by wp_map_apply().',
         'function wp_map_count() { return 5; }', '',
         'function wp_map_name(_id) {']
    L.append('    switch(_id) {')
    L.append('        case 0: return wp_tr("The Ward Road","Дорога Оберегу");')
    for mid, m in maps.items():
        L.append(f'        case {mid}: return wp_tr("{m["name_en"]}","{m["name_uk"]}");')
    L += ['    }', '    return "?";', '}', '', '/// Layout of a generated map: route nodes, pad positions, decor [kind,x,y], core and portal.', 'function wp_map_data(_id) {', '    switch(_id) {']
    for mid, m in maps.items():
        r = ','.join(f'[{x},{y}]' for x, y in m['route'])
        p = ','.join(f'[{x},{y}]' for x, y in m['pads'])
        d = ','.join(f'[{k},{x},{y}]' for k, x, y in m['decor'])
        L.append(f'        case {mid}: return {{route:[{r}],pads:[{p}],decor:[{d}],core:[{m["core"][0]},{m["core"][1]}],portal:[{m["portal"][0]},{m["portal"][1]}]}};')
    L += ['    }', '    return undefined;', '}', '', '/// Visual theme of a map: ground sprite, road palette, fog, motes and weather (0 none, 1 snow, 2 embers, 3 spores, 4 wisps).', 'function wp_map_theme(_id) {', '    switch(_id) {']
    for mid, m in maps.items():
        t = m['theme']
        L.append(f'        case {mid}: return {{ground:{t["ground"]},blend:{gml_color(t["blend"])},road:[{",".join(gml_color(c) for c in t["road"])}],stone:[{",".join(gml_color(c) for c in t["stone"])}],'
                 f'fog:[{",".join(gml_color(c) for c in t["fog"])}],fog_a:[{t["fog_a"][0]},{t["fog_a"][1]}],mote:[{",".join(gml_color(c) for c in t["mote"])}],weather:{t["weather"]},tree:{gml_color(t["tree"])}}};')
    L += ['    }', '    // Map 0: exactly the 1.3 look.',
          '    return {ground:spr_ground,blend:make_color_rgb(155,175,175),road:[make_color_rgb(16,26,29),make_color_rgb(53,63,63),make_color_rgb(73,79,75)],stone:[make_color_rgb(59,67,65),make_color_rgb(85,91,83)],',
          '            fog:[make_color_rgb(150,195,195),make_color_rgb(120,170,180)],fog_a:[.10,.07],mote:[global.col.gold,global.col.teal],weather:0,tree:c_white};', '}', '']
    return '\n'.join(L)


def write_script(text):
    d = ROOT / 'scripts' / 'scr_maps'; d.mkdir(parents=True, exist_ok=True)
    (d / 'scr_maps.gml').write_text(text, encoding='utf-8', newline='\n')
    tmpl = json.loads(re.sub(r',\s*([}\]])', r'\1', (ROOT / 'scripts' / 'scr_layout' / 'scr_layout.yy').read_text(encoding='utf-8-sig')))
    tmpl['%Name'] = tmpl['name'] = 'scr_maps'
    (d / 'scr_maps.yy').write_text(json.dumps(tmpl, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    register_script('scr_maps')


def register_script(name):
    path = ROOT / 'Wall Protocol.yyp'; text = path.read_text(encoding='utf-8')
    if f'"name":"{name}"' in text:
        return
    line = f'    {{"id":{{"name":"{name}","path":"scripts/{name}/{name}.yy",}},}},\n'
    existing = sorted(re.findall(r'^    \{"id":\{"name":"(scr_\w+)"', text, re.M))
    later = [s for s in existing if s > name]
    if later:
        anchor = f'    {{"id":{{"name":"{later[0]}"'; text = text.replace(anchor, line + anchor, 1)
    else:
        m = re.search(rf'^    \{{"id":\{{"name":"{existing[-1]}".*\n', text, re.M); text = text[:m.end()] + line + text[m.end():]
    path.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    maps = build()
    problems = check(maps)
    for p in problems:
        print('PROBLEM:', p)
    if '--report' in sys.argv or problems:
        report(maps)
    if '--preview' in sys.argv:
        preview(maps)
    if problems:
        sys.exit(1)
    if '--write' in sys.argv:
        write_script(emit(maps)); print('wrote scripts/scr_maps/scr_maps.gml')
