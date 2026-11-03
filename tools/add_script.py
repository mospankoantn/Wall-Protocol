"""Creates (or refreshes) a GameMaker script resource from a .gml file and registers it in the .yyp.

    python tools/add_script.py scr_story            # uses scripts/scr_story/scr_story.gml
Idempotent.  The .yy is copied from an existing script, so the format always matches the project.
"""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]


def add_script(name):
    d = ROOT / 'scripts' / name
    if not (d / f'{name}.gml').exists():
        raise SystemExit(f'missing {d / (name + ".gml")}')
    tmpl = json.loads(re.sub(r',\s*([}\]])', r'\1', (ROOT / 'scripts/scr_layout/scr_layout.yy').read_text(encoding='utf-8-sig')))
    tmpl['%Name'] = tmpl['name'] = name
    (d / f'{name}.yy').write_text(json.dumps(tmpl, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    path = ROOT / 'Wall Protocol.yyp'; text = path.read_text(encoding='utf-8')
    if f'"name":"{name}"' in text:
        return
    line = f'    {{"id":{{"name":"{name}","path":"scripts/{name}/{name}.yy",}},}},\n'
    existing = sorted(re.findall(r'^    \{"id":\{"name":"(scr_\w+)"', text, re.M)); later = [s for s in existing if s > name]
    if later:
        anchor = f'    {{"id":{{"name":"{later[0]}"'; text = text.replace(anchor, line + anchor, 1)
    else:
        m = re.search(rf'^    \{{"id":\{{"name":"{existing[-1]}".*\n', text, re.M); text = text[:m.end()] + line + text[m.end():]
    path.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    for n in sys.argv[1:]:
        add_script(n); print('registered', n)
