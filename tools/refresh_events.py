"""Sync event lists only; never rewrites room placements or sprite resources."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
types={'Create':0,'Step':3,'Draw':8,'Other':7,'CleanUp':12}
for path in (root/'objects').glob('*/*.yy'):
    data=json.loads(re.sub(r',\s*([}\]])',r'\1',path.read_text(encoding='utf-8-sig')))
    data['eventList']=[]
    for event in sorted(path.parent.glob('*.gml')):
        kind,number=event.stem.split('_')
        data['eventList'].append({'$GMEvent':'v1','%Name':'','collisionObjectId':None,'eventNum':int(number),'eventType':types[kind],'isDnD':False,'name':'','resourceType':'GMEvent','resourceVersion':'2.0'})
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Event lists synchronized.')
