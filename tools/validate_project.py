"""Validate GameMaker JSON5 metadata, links, room order, media and text encoding."""
from pathlib import Path
import sys,json,wave,struct,math
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
import json5
from PIL import Image
root=Path(__file__).resolve().parents[1]
errors=[];checks=0
def check(ok,message):
    global checks
    checks+=1
    if not ok:errors.append(message)
def read(path):
    try:return json5.loads(path.read_text(encoding='utf-8-sig'),allow_duplicate_keys=False)
    except Exception as e:errors.append(f'{path.relative_to(root)}: {e}');return {}
project=read(root/'Wall Protocol.yyp')
resources={r['id']['name']:r['id']['path'] for r in project['resources']}
check(len(resources)==len(project['resources']),'Duplicate resource names')
data={}
for name,path in resources.items():
    p=root/path;check(p.is_file(),f'Missing resource: {path}')
    if p.is_file():
        item=read(p);data[name]=item
        check(item.get('name')==name and item.get('%Name')==name,f'Name mismatch: {name}')
        check(item.get('resourceVersion')=='2.0',f'Unexpected resourceVersion: {name}')
        parent=item.get('parent',{}).get('path','')
        check((root/parent).exists(),f'Missing parent: {name} -> {parent}')
for f in project['Folders']:check((root/f['folderPath']).exists(),f"Missing folder {f['folderPath']}")
for p in (root/'options').rglob('*.yy'):read(p)
windows=read(root/'options/windows/options_windows.yy')
check(windows['option_windows_icon']=='${options_dir}/windows/icons/icon.ico','Windows icon must use project options_dir, not the GameMaker defaults')
types={'Create':0,'Step':3,'Draw':8,'Other':7,'CleanUp':12}
for name,item in data.items():
    folder=(root/resources[name]).parent
    if item.get('resourceType')=='GMObject':
        parent=item.get('parentObjectId');spr=item.get('spriteId')
        if parent:check(parent['name'] in resources,f'Missing object parent {name}')
        if spr:check(spr['name'] in resources,f'Missing sprite {name}')
        expected={(e['eventType'],e['eventNum']) for e in item['eventList']}
        actual={(types[p.stem.split('_')[0]],int(p.stem.split('_')[1])) for p in folder.glob('*.gml')}
        check(actual==expected,f'Unregistered/missing event in {name}')
    if item.get('resourceType')=='GMScript':check((folder/(name+'.gml')).exists(),f'Missing script {name}')
    if item.get('resourceType')=='GMRoom':
        instances=[i for layer in item['layers'] for i in layer.get('instances',[])]
        names=[i['name'] for i in instances];order=[i['name'] for i in item['instanceCreationOrder']]
        check(len(set(names))==len(names),f'Duplicate room instance {name}')
        check(set(names)==set(order) and len(names)==len(order),f'Broken instance creation order {name}')
        check(instances[0]['objectId']['name']=='obj_app',f'App must be first in {name}')
        for inst in instances:
            obj=inst['objectId']['name'];check(obj in resources,f'Missing room object {obj}')
            for prop in inst['properties']:
                check((root/prop['propertyId']['path']).is_file(),f'Missing property source {obj}')
                owner=read(root/prop['propertyId']['path'])
                check(any(p['name']==prop['propertyId']['name'] for p in owner['properties']),f'Invalid room override {obj}.{prop["propertyId"]["name"]}')
        check((folder/item['creationCodeFile']).is_file(),f'Missing creation code {name}')
    if item.get('resourceType')=='GMSprite':
        expected=[f['name'] for f in item['frames']]
        keyframes=item['sequence']['tracks'][0]['keyframes']['Keyframes']
        check(len(expected)==len(keyframes),f'Frame/sequence mismatch {name}')
        for i,frame in enumerate(expected):
            check(keyframes[i]['Channels']['0']['Id']['name']==frame,f'Sequence frame mismatch {name}')
            paths=[folder/(frame+'.png')]+[folder/'layers'/frame/(layer['name']+'.png') for layer in item['layers']]
            for path in paths:
                check(path.exists(),f'Missing PNG {path}')
                if path.exists():
                    im=Image.open(path);check(im.size==(item['width'],item['height']),f'PNG size mismatch {name}')
                    check(im.mode=='RGBA',f'Expected RGBA {name}')
                    check(im.getchannel('A').getextrema()[1]>0,f'Empty sprite {name}')
    if item.get('resourceType')=='GMFont':
        check((folder/(name+'.png')).exists(),f'Missing font bitmap {name}')
        if name!='fnt_ua':
            for char in 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя':
                check(str(ord(char)) in item['glyphs'],f'Missing Ukrainian glyph {name}: {char}')
    if item.get('resourceType')=='GMSound':
        path=folder/item['soundFile'];check(path.exists(),f'Missing sound {name}')
        if path.exists():
            with wave.open(str(path),'rb') as f:
                want=2 if name in ('snd_ambience','snd_battle') else 1   # music loops are stereo, effects are mono
                check(f.getframerate()==44100 and f.getsampwidth()==2 and f.getnchannels()==want,f'Audio format {name}')
                check(item.get('duration',0)>0 and abs(item['duration']-f.getnframes()/44100)<.01,f'Sound duration {name}')
                raw=f.readframes(f.getnframes());values=struct.unpack('<'+'h'*(len(raw)//2),raw)
                peak=max(abs(v) for v in values)
                check(100<peak<32767,f'Empty/clipped sound {name}')
icon=Image.open(root/'options/windows/icons/icon.ico')
check(len(icon.ico.sizes())>=6,'Icon must contain multiple resolutions')
for p in root.rglob('*'):
    if not p.is_file() or any(n in p.parts for n in ['build','vendor','__pycache__']):continue
    if p.suffix not in ['.gml','.yy','.yyp','.md','.py','.ps1','.resource_order']:continue
    raw=p.read_bytes()
    try:raw.decode('utf-8');check(True,'')
    except UnicodeDecodeError:check(False,f'Not UTF-8: {p}')
    check(b'\r' not in raw,f'Non-LF text: {p.relative_to(root)}')
report={'passed':not errors,'checks':checks,'resources':len(resources),'objects':sum(v.get('resourceType')=='GMObject' for v in data.values()),'rooms':sum(v.get('resourceType')=='GMRoom' for v in data.values()),'errors':errors}
(root/'build/metadata-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
