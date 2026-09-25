"""Slice the atlas using actual sprite rectangles instead of the approximate grid.
Keeps existing sprite/frame IDs intact. No image repainting or alpha keying.
"""
from pathlib import Path
import json,re,copy,uuid
from PIL import Image
root=Path(__file__).resolve().parents[1]
def read(path):return json.loads(re.sub(r',\s*([}\]])',r'\1',path.read_text(encoding='utf-8-sig')))
atlas=Image.open(root/'art/defense_atlas.png').convert('RGBA')
boxes={
 'spr_archer':[(14,27,245,274)],'spr_rune':[(281,6,498,273)],'spr_frost':[(542,4,722,275)],
 'spr_core':[(804,4,1001,273)],'spr_portal':[(1035,1,1267,276)],'spr_pad':[(1297,89,1535,275)],
 'spr_skeleton':[(13,294,224,530),(16,544,223,777)],
 'spr_brute':[(253,283,515,531),(250,539,516,781)],
 'spr_runner':[(535,297,747,532),(535,546,748,779)],
 'spr_boss':[(768,272,1048,533),(749,533,1019,783)],
 'spr_tree':[(1062,270,1275,531)],'spr_rocks':[(1290,301,1534,532)],
 'spr_brazier':[(1081,537,1253,779)],'spr_wall':[(1300,540,1534,780)],
 'spr_emblem':[(17,779,237,1016)],'spr_arrow':[(273,793,507,1003)],
 'spr_orb':[(536,786,751,1017)],'spr_shard':[(799,784,989,1017)],
 'spr_aether':[(1062,790,1247,1018)],'spr_grave':[(1300,794,1518,1023)]}
for name,frames in boxes.items():
    folder=root/'sprites'/name;data=read(folder/(name+'.yy'));w,h=data['width'],data['height']
    for frame,box in zip(data['frames'],frames):
        tile=atlas.crop(box);tile.thumbnail((w-4,h-4),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(w,h));canvas.paste(tile,((w-tile.width)//2,(h-tile.height)//2))
        canvas.save(folder/(frame['name']+'.png'))
        canvas.save(folder/'layers'/frame['name']/(data['layers'][0]['name']+'.png'))
    if name=='spr_emblem':
        canvas.save(root/'options/windows/icons/icon.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
        canvas.save(root/'art/game_icon.png')
# Ground texture: a complete native resource, cloned from the verified sprite schema.
source=root/'art/forest_ground.png'
if source.exists():
    name='spr_ground';folder=root/'sprites'/name;folder.mkdir(parents=True,exist_ok=True)
    if (folder/(name+'.yy')).exists():data=read(folder/(name+'.yy'))
    else:
        data=read(root/'sprites/spr_menu_art/spr_menu_art.yy')
        data['name']=data['%Name']=name;data['width']=data['height']=512
        data['bbox_right']=data['bbox_bottom']=511
        seq=data['sequence'];seq['name']=seq['%Name']=name
        frame=str(uuid.uuid4());layer=str(uuid.uuid4())
        data['frames'][0]['name']=data['frames'][0]['%Name']=frame
        data['layers'][0]['name']=data['layers'][0]['%Name']=layer
        seq['tracks'][0]['keyframes']['Keyframes'][0]['Channels']['0']['Id']={'name':frame,'path':f'sprites/{name}/{name}.yy'}
    frame=data['frames'][0]['name'];layer=data['layers'][0]['name']
    (folder/'layers'/frame).mkdir(parents=True,exist_ok=True)
    im=Image.open(source).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
    im.save(folder/(frame+'.png'));im.save(folder/'layers'/frame/(layer+'.png'))
    (folder/(name+'.yy')).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    project=read(root/'Wall Protocol.yyp')
    if not any(r['id']['name']==name for r in project['resources']):project['resources'].append({'id':{'name':name,'path':f'sprites/{name}/{name}.yy'}})
    (root/'Wall Protocol.yyp').write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Imported clean sprite rectangles and ground texture.')
