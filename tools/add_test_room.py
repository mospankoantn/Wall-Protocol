"""One-time rm_test migration, preserving existing rooms. Do not rerun after editing rm_test."""
import copy
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/vendor'))
import json5

def read(path):
    return json5.loads((ROOT / path).read_text(encoding='utf-8'))

def write(path, data):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

if (ROOT / 'rooms/rm_test/rm_test.yy').exists():
    raise SystemExit('rm_test already exists. Edit it in Room Editor; migration cancelled.')

base = read('rooms/rm_game/rm_game.yy')
source_instances = next(l['instances'] for l in base['layers'] if 'instances' in l)
inst_template = source_instances[0]
prop_template = next(i['properties'][0] for i in source_instances if i['properties'])

def ref(name, kind='objects'):
    return {'name': name, 'path': f'{kind}/{name}/{name}.yy'}

def instance(obj, x=0, y=0, properties=None, owner=None):
    result = copy.deepcopy(inst_template)
    result['name'] = result['%Name'] = 'inst_' + uuid.uuid4().hex[:8].upper()
    result.update(objectId=ref(obj), x=x, y=y, properties=[])
    for key, value in (properties or {}).items():
        prop = copy.deepcopy(prop_template)
        prop['objectId'] = ref(owner or obj)
        prop['propertyId'] = {'name': key, 'path': ref(owner or obj)['path']}
        prop['value'] = json.dumps(value, ensure_ascii=False)
        result['properties'].append(prop)
    return result

obj = read('objects/obj_game/obj_game.yy')
obj['name'] = obj['%Name'] = 'obj_sandbox'
obj['eventList'] = []
template = read('objects/obj_button/obj_button.yy')['properties'][2]
for key, val in [('starting_aether', 5000), ('test_wave', 4), ('invulnerable', 1)]:
    prop = copy.deepcopy(template)
    prop['name'] = prop['%Name'] = key
    prop['value'] = str(val)
    obj['properties'].append(prop)
write('objects/obj_sandbox/obj_sandbox.yy', obj)

script = read('scripts/scr_world/scr_world.yy')
script['name'] = script['%Name'] = 'scr_sandbox'
write('scripts/scr_sandbox/scr_sandbox.yy', script)

room = copy.deepcopy(base)
room['name'] = room['%Name'] = 'rm_test'
instances = [instance(n, 24 + i*48, 24) for i, n in enumerate(
    ['obj_app', 'obj_audio', 'obj_game', 'obj_sandbox', 'obj_wave', 'obj_board', 'obj_hud'])]
route = [(85, 410), (165, 410), (165, 175), (590, 175), (590, 420), (950, 420)]
for i, (x, y) in enumerate(route):
    instances.append(instance('obj_path_node', x, y, {'node_order': i}))
pads = [(285, 270), (430, 340), (750, 355), (445, 110), (830, 200), (420, 460)]
for i, (x, y) in enumerate(pads):
    instances.append(instance('obj_build_pad', x, y, {'pad_key': f'lab_{i:02}'}))
for i, kind in enumerate(['archer', 'rune', 'frost']):
    instances.append(instance('obj_tower_' + kind, *pads[i], {'level': i+1}, 'obj_tower'))
for name, (x, y) in zip(['obj_skeleton', 'obj_brute', 'obj_runner', 'obj_boss'],
                         [(100, 410), (165, 330), (400, 175), (590, 300)]):
    instances.append(instance(name, x, y))
instances.extend([instance('obj_portal', *route[0]), instance('obj_core', *route[-1])])

# Copy only UI instances from the live game. Pause has its own lab-safe actions.
layout = []
for source in source_instances:
    if source['objectId']['name'] != 'obj_button':
        continue
    props = {p['propertyId']['name']: json.loads(p['value']) for p in source['properties']}
    if props['page'] == 'pause':
        continue
    item = {'x': source['x'], 'y': source['y'], **props}
    layout.append(item)
for i, action in enumerate(['resume', 'options', 'lab_reset', 'menu']):
    layout.append(dict(x=503, y=320+i*70, action=action, page='pause', button_w=360, nav_order=i))
actions = ['lab_spawn0', 'lab_spawn1', 'lab_spawn2', 'lab_spawn3', 'lab_swarm',
           'lab_clear', 'lab_gold', 'lab_heal', 'lab_god', 'lab_cycle',
           'lab_victory', 'lab_defeat', 'lab_reset', 'lab_menu']
for i, action in enumerate(actions):
    layout.append(dict(x=24+(i%5)*204, y=544+(i//5)*46, action=action,
                       page='game', button_w=192, button_h=40, nav_order=8+i))
for item in layout:
    props = {k: v for k, v in item.items() if k not in ('x', 'y')}
    instances.append(instance('obj_button', item['x'], item['y'], props))

next(l for l in room['layers'] if 'instances' in l)['instances'] = instances
room['instanceCreationOrder'] = [{'name': i['name'], 'path': 'rooms/rm_test/rm_test.yy'} for i in instances]
write('rooms/rm_test/rm_test.yy', room)
(ROOT/'rooms/rm_test/RoomCreationCode.gml').write_text('wp_room_setup();\n', encoding='utf-8', newline='\n')

script_file = ROOT/'scripts/scr_sandbox/scr_sandbox.gml'
with script_file.open('a', encoding='utf-8', newline='\n') as f:
    f.write('\n// Fallback only: existing room-authored buttons always win.\n')
    f.write('function wp_sandbox_buttons() {\n    return [\n')
    f.write(',\n'.join('        '+json.dumps(b, ensure_ascii=False, separators=(',', ':')) for b in layout))
    f.write('\n    ];\n}\n')

menu = read('rooms/rm_menu/rm_menu.yy')
button = instance('obj_button', 1030, 638, dict(action='sandbox', page='main', button_w=280, nav_order=6))
next(l for l in menu['layers'] if 'instances' in l)['instances'].append(button)
menu['instanceCreationOrder'].append({'name': button['name'], 'path': 'rooms/rm_menu/rm_menu.yy'})
write('rooms/rm_menu/rm_menu.yy', menu)

project = read('Wall Protocol.yyp')
for name, kind in [('obj_sandbox','objects'), ('scr_sandbox','scripts'), ('rm_test','rooms')]:
    project['resources'].append({'id': ref(name, kind)})
project['RoomOrderNodes'].append({'roomId': ref('rm_test', 'rooms')})
write('Wall Protocol.yyp', project)
print(f'Added rm_test with {len(instances)} authored instances. Existing room layouts retained.')
