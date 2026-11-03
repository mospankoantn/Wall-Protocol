"""One-time migration of rm_menu.yy for version 1.4 (main menu gains "Story mode" and "Load game").

Moves the authored main-page buttons to the new column and the "credits" button to the right-hand side.
Only buttons that still sit at their 1.0-1.3 default position are moved, so layouts you edited yourself are left alone.
Idempotent: running it again changes nothing.
"""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'rooms' / 'rm_menu' / 'rm_menu.yy'
# action: (old x, old y, new x, new y, new button_w or None, new nav_order)
MOVES = {
    'continue': (80, 338, 80, 382, None, 1),
    'new':      (80, 398, 80, 434, None, 2),
    'options':  (80, 458, 80, 538, None, 4),
    'guide':    (80, 518, 80, 590, None, 5),
    'credits':  (80, 578, 1030, 582, 280, 7),
    'quit':     (80, 638, 80, 642, None, 6),
}


def set_prop(block, name, value):
    pat = re.compile(r'("propertyId":\{"name":"%s",[^}]*\},"resourceType":"GMOverriddenProperty","resourceVersion":"2.0","value":")([^"]*)(")' % name)
    assert pat.search(block), name
    return pat.sub(lambda m: m.group(1) + str(value) + m.group(3), block, count=1)


def main():
    text = PATH.read_text(encoding='utf-8')
    changed = 0

    def fix(m):
        nonlocal changed
        block = m.group(0)
        if '"obj_button"' not in block or '\\"main\\"' not in block:
            return block
        act = re.search(r'"propertyId":\{"name":"action",[^}]*\},"resourceType":"GMOverriddenProperty","resourceVersion":"2.0","value":"\\"(\w+)\\""', block)
        if not act or act.group(1) not in MOVES:
            if act and act.group(1) == 'sandbox':
                new = set_prop(block, 'nav_order', 8)
                if new != block:
                    changed += 1
                return new
            return block
        ox, oy, nx, ny, nw, nav = MOVES[act.group(1)]
        x = float(re.search(r'"x":([\d.]+),', block).group(1)); y = float(re.search(r'"y":([\d.]+),', block).group(1))
        if (x, y) == (nx, ny):
            return block
        if (x, y) != (ox, oy):
            print('skipped (edited by hand):', act.group(1), x, y)
            return block
        block = re.sub(r'"x":[\d.]+,', f'"x":{nx}.0,', block, count=1)
        block = re.sub(r'"y":[\d.]+,', f'"y":{ny}.0,', block, count=1)
        if nw is not None:
            block = set_prop(block, 'button_w', nw)
        block = set_prop(block, 'nav_order', nav)
        changed += 1
        return block

    new = re.sub(r'\{"\$GMRInstance":"v4".*?"y":[\d.]+,\},', fix, text, flags=re.S)
    if new != text:
        PATH.write_text(new, encoding='utf-8', newline='\n')
    print('buttons updated:', changed)


if __name__ == '__main__':
    main()
