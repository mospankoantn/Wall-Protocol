"""One-time polish migration. Keeps all existing instance names and placements."""
from pathlib import Path
import json,re,copy
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads(re.sub(r',\s*([}\]])',r'\1',p.read_text(encoding='utf-8-sig')))
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
project=read(root/'Wall Protocol.yyp')
names=['obj_tree','obj_rocks','obj_brazier','obj_wall','obj_grave']
sprites=['spr_tree','spr_rocks','spr_brazier','spr_wall','spr_grave']
for i,(name,spr) in enumerate(zip(names,sprites)):
    data=read(root/'objects/obj_decor/obj_decor.yy')
    data.update({'%Name':name,'name':name,'spriteId':{'name':spr,'path':f'sprites/{spr}/{spr}.yy'},'properties':[],'parentObjectId':{'name':'obj_decor','path':'objects/obj_decor/obj_decor.yy'}})
    data['eventList']=[{'$GMEvent':'v1','%Name':'','collisionObjectId':None,'eventNum':0,'eventType':0,'isDnD':False,'name':'','resourceType':'GMEvent','resourceVersion':'2.0'}]
    write(root/f'objects/{name}/{name}.yy',data)
    (root/f'objects/{name}/Create_0.gml').write_text(f'decor_kind={i};event_inherited();\n',encoding='utf-8',newline='\n')
    if not any(r['id']['name']==name for r in project['resources']):project['resources'].append({'id':{'name':name,'path':f'objects/{name}/{name}.yy'}})
for room in ['rm_game','Room1']:
    p=root/f'rooms/{room}/{room}.yy';data=read(p)
    for layer in data['layers']:
        for inst in layer.get('instances',[]):
            obj=inst['objectId']['name']
            if obj=='obj_decor':
                kind=next((int(v['value']) for v in inst['properties'] if v['propertyId']['name']=='decor_kind'),0)
                name=names[kind];inst['objectId']={'name':name,'path':f'objects/{name}/{name}.yy'};inst['properties']=[]
            if obj=='obj_portal':inst['x']=70
            if obj=='obj_path_node' and any(v['propertyId']['name']=='node_order' and v['value']=='0' for v in inst['properties']):inst['x']=70
    write(p,data)
write(root/'Wall Protocol.yyp',project)
main=read(root/'options/main/options_main.yy');main['option_author']='Eclipse Wire';write(root/'options/main/options_main.yy',main)
print('Editor decoration sprites now match the runtime scene.')
