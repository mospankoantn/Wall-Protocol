"""Rough balance estimate for survival and the story chapters (no GameMaker needed).

A small Python port of the battle rules (enemy stats, tower/projectile maths, wave timing, income) driven by a simple
scripted player: it builds on the pads that cover the most road, then upgrades every tower once per wave.
For each scenario it reports the result with all pads and the SMALLEST number of towers that still wins - a difficulty
measure that can be compared across maps.  It is an estimate: real play differs (targeting choices, selling, timing).

    python tools/balance_sim.py [--detail]
"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import story_maps as SM

TOWERS = [dict(cost=90, dmg=20, rng=175, rate=.55), dict(cost=135, dmg=34, rng=165, rate=1.05), dict(cost=110, dmg=11, rng=155, rate=.72)]
FLIGHT = [620, 390, 500]
RATE_UP = [.12, .08, .10]
KINDS = [0, 0, 0, 2, 1, 1, 0, 1, 2, 0, 0, 0, 0, 1]      # tower kind per pad rank (same mix as the integration test)
SPEED = [56, 38, 84, 30]; REWARD = [10, 19, 15, 100]; BREACH = [1, 2, 1, 6]

# rules mirror scr_story.gml (keep in sync)
SURVIVAL = dict(map=0, total=8, gold=280, hpmult=1, offset=0, flavor=0, boss=[8])
CHAPTERS = [dict(map=0, total=5, gold=300, hpmult=.85, offset=0, flavor=0, boss=[]),
            dict(map=1, total=6, gold=420, hpmult=.85, offset=1, flavor=1, boss=[]),
            dict(map=2, total=7, gold=320, hpmult=1.2, offset=1, flavor=2, boss=[]),
            dict(map=3, total=8, gold=340, hpmult=1.15, offset=1, flavor=3, boss=[8]),
            dict(map=4, total=10, gold=380, hpmult=1.8, offset=2, flavor=4, boss=[5, 10])]


def wave_list(w, r):
    e = w + r['offset']; out = []
    for i in range(6 + e * 2):
        k = 0
        if e >= 2 and i % 4 == 2: k = 2
        if e >= 4 and i % 5 == 4: k = 1
        f = r['flavor']
        if f == 1 and e >= 3 and i % 4 == 1: k = 1
        if f == 2 and e >= 2 and i % 3 == 0: k = 2
        if f == 3 and i % 4 == 1: k = 1 if e >= 3 else 2
        if f == 4 and i % 3 == 2: k = 1 if i % 2 == 0 else 2
        out.append(k)
    if w in r['boss']: out.append(3)
    return out


def hp_of(k, w, r):
    e = w + r['offset']
    return round([70 + e * 13, 180 + e * 32, 88 + e * 17, 950 + e * 80][k] * r['hpmult'])


class E:
    __slots__ = 'k hp x y seg prog slow slowf'.split()


def simulate(rules, route, pads, n_towers=None, upgrades=True, dt=1 / 20):
    pts = SM.samples(route)
    order = sorted(range(len(pads)), key=lambda i: -SM.exposure(pads[i], pts))
    if n_towers is not None: order = order[:n_towers]
    gold = rules['gold']; hp = 20; towers = {}      # pad index -> [kind, level, cooldown, invested]
    segs = [(route[i], route[i + 1], math.dist(route[i], route[i + 1])) for i in range(len(route) - 1)]
    for wave in range(1, rules['total'] + 1):
        for rank, pi in enumerate(order):                                 # build pass
            if pi not in towers and gold >= TOWERS[KINDS[rank % len(KINDS)]]['cost']:
                kd = KINDS[rank % len(KINDS)]; gold -= TOWERS[kd]['cost']; towers[pi] = [kd, 1, 0.0, TOWERS[kd]['cost']]
        if upgrades:
            for pi in order:                                              # upgrade pass
                if pi in towers and towers[pi][1] < 3:
                    kd, lv = towers[pi][0], towers[pi][1]; c = round(TOWERS[kd]['cost'] * (.65 + .35 * lv))
                    if gold >= c: gold -= c; towers[pi][1] += 1; towers[pi][3] += c; towers[pi][2] = 0
        queue = wave_list(wave, rules); spawned = 0; timer = .6; enemies = []; shots = []
        while True:
            timer -= dt
            if spawned < len(queue) and timer <= 0:
                e = E(); e.k = queue[spawned]; e.hp = hp_of(e.k, wave, rules); e.x, e.y = route[0]; e.seg = 0; e.prog = 0.0; e.slow = 0.0; e.slowf = 1.0
                enemies.append(e); spawned += 1; timer = max(.35, .9 - wave * .04)
            if spawned >= len(queue) and not enemies and not shots: break
            for e in enemies:                                             # move
                e.slow = max(0, e.slow - dt)
                if e.slow == 0: e.slowf = 1.0
                mv = SPEED[e.k] * e.slowf * dt
                while mv > 0 and e.seg < len(segs):
                    a, b, ln = segs[e.seg]; d = math.dist((e.x, e.y), b)
                    if d <= mv: e.x, e.y = b; e.prog += d; mv -= d; e.seg += 1
                    else: ang = math.atan2(b[1] - e.y, b[0] - e.x); e.x += math.cos(ang) * mv; e.y += math.sin(ang) * mv; e.prog += mv; mv = 0
            for e in [e for e in enemies if e.seg >= len(segs)]:
                hp -= BREACH[e.k]; enemies.remove(e)
                if hp <= 0: return dict(win=False, hp=0, wave=wave)
            for pi, t in towers.items():                                  # towers fire
                kd, lv = t[0], t[1]; t[2] = max(-.5, t[2] - dt)
                if t[2] <= 0:
                    rng = TOWERS[kd]['rng'] + (lv - 1) * 10; px, py = pads[pi]
                    cands = [e for e in enemies if math.dist((px, py), (e.x, e.y)) <= rng and e.hp > 0]
                    if cands:
                        tg = max(cands, key=lambda e: e.prog)
                        shots.append([px, py - 27, kd, tg, 1 + (lv - 1) * .58, lv]); t[2] = TOWERS[kd]['rate'] / (1 + (lv - 1) * RATE_UP[kd])
            for s in list(shots):                                         # projectiles
                tg = s[3]
                if tg.hp <= 0 or tg not in enemies: shots.remove(s); continue
                step = FLIGHT[s[2]] * dt; tx, ty = tg.x, tg.y - 14
                if math.dist((s[0], s[1]), (tx, ty)) <= step + 6:
                    dmg = TOWERS[s[2]]['dmg'] * s[4]; victims = [tg]
                    if s[2] == 1:
                        radius = 58 + (s[5] - 1) * 7; victims = [e for e in enemies if math.dist((e.x, e.y), (tg.x, tg.y)) <= radius]
                    if s[2] == 2: tg.slowf = max(.42, .6 - (s[5] - 1) * .07); tg.slow = 1.7 + (s[5] - 1) * .35
                    for v in victims:
                        v.hp -= dmg
                        if v.hp <= 0 and v in enemies: gold += REWARD[v.k]; enemies.remove(v)
                    shots.remove(s)
                else:
                    ang = math.atan2(ty - s[1], tx - s[0]); s[0] += math.cos(ang) * step; s[1] += math.sin(ang) * step
        if wave < rules['total']: gold += 45 + wave * 10
    return dict(win=True, hp=hp, wave=rules['total'])


def margin(rules, route, pads):
    """How many times the enemies' HP could be multiplied (on top of the rules) before the scripted player loses."""
    lo, hi = 1.0, 40.0
    if not simulate(rules, route, pads)['win']: return 0.0
    for _ in range(12):
        mid = (lo + hi) / 2
        if simulate(dict(rules, hpmult=rules['hpmult'] * mid), route, pads)['win']: lo = mid
        else: hi = mid
    return lo


def min_towers(rules, route, pads):
    for n in range(1, len(pads) + 1):
        if simulate(rules, route, pads, n)['win']: return n
    return None


def scenarios():
    maps = SM.build()
    yield 'survival (forest, 8 waves)', SURVIVAL, SM.MAP0['route'], SM.MAP0['pads']
    for i, r in enumerate(CHAPTERS):
        if r['map'] == 0: route, pads = SM.MAP0['route'], SM.MAP0['pads']
        else: route, pads = maps[r['map']]['route'], maps[r['map']]['pads']
        yield f'chapter {i + 1} (map {r["map"]}, {r["total"]} waves)', r, route, pads


if __name__ == '__main__':
    print(f'{"scenario":34s} {"all pads":>12s} {"no upgrades":>12s} {"min towers":>11s} {"HP margin":>10s}')
    for name, r, route, pads in scenarios():
        a = simulate(r, route, pads); b = simulate(r, route, pads, upgrades=False); n = min_towers(r, route, pads); m = margin(r, route, pads)
        fmt = lambda x: ('win HP %2d' % x['hp']) if x['win'] else ('lost w%d' % x['wave'])
        print(f'{name:34s} {fmt(a):>14s} {fmt(b):>14s} {str(n) + " of " + str(len(pads)):>11s} {"x%.1f" % m:>10s}')
