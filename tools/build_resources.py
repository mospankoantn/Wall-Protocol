"""Authoring-time resource importer. GML lives in the actual objects/scripts folders.
Run once to construct the new project; do not run after editing room layouts in the IDE.
Original source is preserved in build/before-rework.zip.
"""
from pathlib import Path
import json, re, uuid, copy, shutil, math, wave, struct
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    # GameMaker's existing JSON uses trailing commas; output is strict JSON.
    return json.loads(re.sub(r',\s*([}\]])', r'\1', Path(path).read_text(encoding='utf-8-sig')))
def write(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
def uid(): return str(uuid.uuid4())
def ref(kind, name): return {'name':name,'path':f'{kind}/{name}/{name}.yy'}
def base(kind, name, version=''):
    return {'$'+kind:version,'%Name':name,'name':name,'resourceType':kind,'resourceVersion':'2.0'}
project = read(ROOT/'Wall Protocol.yyp')
object_template = read(ROOT/'objects/obj_game/obj_game.yy')
room_template = read(ROOT/'rooms/Room1/Room1.yy')
sprite_template = read(ROOT/'sprites/spr_button/spr_button.yy')
sound_template = read(ROOT/'sounds/snd_click/snd_click.yy')
resources = [r for r in project['resources'] if r['id']['name']=='fnt_ua']
folders = ['Systems','Interface','World','Towers','Enemies','Art','Audio','Rooms','Scripts','Font']
project['Folders'] = []
for name in folders:
    folder=base('GMFolder', name)
    folder['folderPath']=f'folders/{name}.yy'
    project['Folders'].append(folder)
    write(f'folders/{name}.yy',folder)
def register(kind,name,folder,data):
    data['parent']={'name':folder,'path':f'folders/{folder}.yy'}
    write(f'{kind}/{name}/{name}.yy', data)
    resources.append({'id':ref(kind,name)})
def sprite(name,frames,origin=None):
    data=copy.deepcopy(sprite_template)
    data['%Name']=data['name']=name
    w,h=frames[0].size
    data.update(width=w,height=h,bbox_left=0,bbox_right=w-1,bbox_top=0,bbox_bottom=h-1,origin=4 if origin is None else 9)
    layer=uid()
    data['layers'][0].update({'%Name':layer,'name':layer})
    seq=data['sequence']; seq['%Name']=seq['name']=name
    seq['length']=len(frames);seq['playbackSpeed']=5
    seq['xorigin'],seq['yorigin']=origin or (w//2,h//2)
    keyframes=[];data['frames']=[]
    directory=ROOT/'sprites'/name;directory.mkdir(parents=True,exist_ok=True)
    for index,im in enumerate(frames):
        frame=uid();data['frames'].append(base('GMSpriteFrame',frame,'v1'))
        im.save(directory/f'{frame}.png')
        (directory/'layers'/frame).mkdir(parents=True,exist_ok=True)
        im.save(directory/'layers'/frame/f'{layer}.png')
        keyframes.append({'$Keyframe<SpriteFrameKeyframe>':'','Channels':{'0':{'$SpriteFrameKeyframe':'','Id':{'name':frame,'path':f'sprites/{name}/{name}.yy'},'resourceType':'SpriteFrameKeyframe','resourceVersion':'2.0'}},'Disabled':False,'id':uid(),'IsCreationKey':False,'Key':float(index),'Length':1.0,'resourceType':'Keyframe<SpriteFrameKeyframe>','resourceVersion':'2.0','Stretch':False})
    seq['tracks'][0]['keyframes']['Keyframes']=keyframes
    register('sprites',name,'Art',data)

atlas=Image.open(ROOT/'art/defense_atlas.png').convert('RGBA')
def cell(col,row,size): return atlas.crop((col*256,row*256,(col+1)*256,(row+1)*256)).resize((size,size),Image.Resampling.LANCZOS)
for name,col,row,size in [('spr_archer',0,0,96),('spr_rune',1,0,96),('spr_frost',2,0,96),('spr_core',3,0,144),('spr_portal',4,0,144),('spr_pad',5,0,76),('spr_tree',4,1,136),('spr_rocks',5,1,100),('spr_brazier',4,2,72),('spr_wall',5,2,120),('spr_emblem',0,3,256),('spr_arrow',1,3,28),('spr_orb',2,3,32),('spr_shard',3,3,28),('spr_aether',4,3,64),('spr_grave',5,3,64)]:
    sprite(name,[cell(col,row,size)])
for name,col,size in [('spr_skeleton',0,58),('spr_brute',1,76),('spr_runner',2,58),('spr_boss',3,106)]:
    sprite(name,[cell(col,1,size),cell(col,2,size)])
sprite('spr_menu_art',[Image.open(ROOT/'art/menu_keyart.png').convert('RGBA')],(0,0))
sprite('spr_studio',[Image.open(ROOT/'Eclipse_Wire_logo.png').convert('RGBA')],(0,0))
# Editor-visible handles and UI plates are intentionally simple native-style graphics.
marker=Image.new('RGBA',(28,28));d=ImageDraw.Draw(marker);d.ellipse((2,2,25,25),fill=(40,90,99,210),outline=(128,222,220,255),width=2);d.line((7,14,21,14),fill='white',width=2);d.line((14,7,14,21),fill='white',width=2)
sprite('spr_node',[marker])
plate=Image.new('RGBA',(360,48));d=ImageDraw.Draw(plate);d.rounded_rectangle((1,1,358,46),radius=4,fill=(17,30,37,245),outline=(112,129,121,255),width=1)
sprite('spr_button',[plate],(0,0))
icon=cell(0,3,256)
icon_path=ROOT/'options/windows/icons/icon.ico';icon_path.parent.mkdir(parents=True,exist_ok=True)
icon.save(icon_path,sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
icon.save(ROOT/'art/game_icon.png')

rate=44100;rng=np.random.default_rng(72)
def sound(name,values,music=False):
    values=np.clip(values,-0.95,0.95)
    folder=ROOT/'sounds'/name;folder.mkdir(parents=True,exist_ok=True)
    with wave.open(str(folder/f'{name}.wav'),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes((values*32767).astype('<i2').tobytes())
    data=copy.deepcopy(sound_template)
    data.update({'%Name':name,'name':name,'soundFile':f'{name}.wav','duration':len(values)/rate,'preload':not music,'compression':1 if music else 0})
    register('sounds',name,'Audio',data)
def tone(duration,freq,end=None,noise=0):
    t=np.arange(int(rate*duration))/rate
    end=freq if end is None else end
    phase=2*np.pi*(freq*t+(end-freq)*t*t/(2*duration))
    return (np.sin(phase)*0.35+rng.uniform(-1,1,len(t))*noise)*np.minimum(t*100,1)*np.exp(-t*5/duration)
sound('snd_click',tone(.12,680,960))
sound('snd_build',tone(.65,220,740)+tone(.65,330,990)*.5)
sound('snd_arrow',tone(.16,1300,210,.2))
sound('snd_rune',tone(.45,240,55,.16))
sound('snd_frost',tone(.36,1900,720,.08))
sound('snd_hit',tone(.16,150,75,.18))
sound('snd_breach',tone(.8,110,38,.16))
sound('snd_wave',tone(1,220,440)+tone(1,330,660)*.4)
sound('snd_victory',sum(tone(2,f)*.55 for f in [293.66,369.99,440,587.33]))
duration=32;t=np.arange(rate*duration)/rate;music=np.zeros(len(t))
for chord_i,chord in enumerate([[146.832,174.614,220],[130.813,174.614,220],[130.813,164.814,195.998],[110,146.832,164.814]]):
    start=chord_i*8*rate;tt=np.arange(8*rate)/rate
    env=np.sin(np.pi*tt/8)**.65
    segment=sum(np.sin(2*np.pi*f*tt+.03*np.sin(tt*.5))*0.026+np.sin(2*np.pi*f*2.002*tt)*.008 for f in chord)*env
    music[start:start+len(tt)]+=segment
    for note_i in range(8):
        note=tone(1.6,chord[note_i%3]*4)*.11
        pos=start+note_i*rate
        count=min(len(note),len(music)-pos)
        music[pos:pos+count]+=note[:count]
sound('snd_ambience',music,True)

event_types={'Create':0,'Step':3,'Draw':8,'Other':7,'CleanUp':12}
def obj(name,folder='Systems',spr=None,parent=None,persistent=False,properties=None):
    data=copy.deepcopy(object_template)
    data['%Name']=data['name']=name
    data['spriteId']=ref('sprites',spr) if spr else None
    data['parentObjectId']=ref('objects',parent) if parent else None
    data['persistent']=persistent
    data['properties']=properties or []
    data['eventList']=[]
    for path in sorted((ROOT/'objects'/name).glob('*.gml')):
        et,num=path.stem.split('_')
        data['eventList'].append({'$GMEvent':'v1','%Name':'','collisionObjectId':None,'eventNum':int(num),'eventType':event_types[et],'isDnD':False,'name':'','resourceType':'GMEvent','resourceVersion':'2.0'})
    register('objects',name,folder,data)
def prop(name,value,typ=0):
    return {**base('GMObjectProperty',name,'v1'),'filters':[],'listItems':[],'multiselect':False,'rangeEnabled':False,'rangeMax':10.0,'rangeMin':0.0,'value':str(value),'varType':typ}
objects=[('obj_app','Systems',None,None,True),('obj_game','Systems'),('obj_wave','Systems'),('obj_audio','Systems',None,None,True),('obj_splash','Interface'),('obj_menu','Interface'),('obj_text','Interface'),('obj_hud','Interface'),('obj_board','World'),('obj_core','World','spr_core'),('obj_portal','World','spr_portal'),('obj_effect','World'),('obj_projectile','World','spr_arrow'),('obj_test','Systems')]
for args in objects: obj(*args)
obj('obj_button','Interface','spr_button',properties=[prop('action','"new"',2),prop('page','"main"',2),prop('button_w',360),prop('button_h',48),prop('nav_order',0)])
obj('obj_path_node','World','spr_node',properties=[prop('node_order',0)])
obj('obj_build_pad','World','spr_pad',properties=[prop('pad_key','"pad"',2)])
obj('obj_decor','World','spr_tree',properties=[prop('decor_kind',0)])
obj('obj_tower','Towers',properties=[prop('tower_kind',0),prop('level',1)])
for name,spr,kind in [('obj_tower_archer','spr_archer',0),('obj_tower_rune','spr_rune',1),('obj_tower_frost','spr_frost',2)]:
    obj(name,'Towers',spr,'obj_tower')
obj('obj_enemy','Enemies',properties=[prop('enemy_kind',0)])
for name,spr,kind in [('obj_skeleton','spr_skeleton',0),('obj_brute','spr_brute',1),('obj_runner','spr_runner',2),('obj_boss','spr_boss',3)]:
    obj(name,'Enemies',spr,'obj_enemy')
for path in sorted((ROOT/'scripts').glob('*/*.gml')):
    name=path.stem
    register('scripts',name,'Scripts',{**base('GMScript',name,'v1'),'isCompatibility':False,'isDnD':False})
# Additional fonts are rebuilt by the compiler from installed Arial/Georgia.
for name,size,font,bold in [('fnt_ui',16,'Arial',False),('fnt_heading',30,'Georgia',True),('fnt_title',56,'Georgia',True)]:
    data=read(ROOT/'fonts/fnt_ua/fnt_ua.yy')
    data.update({'%Name':name,'name':name,'size':size,'fontName':font,'bold':bold,'glyphs':{},'ranges':[{'lower':32,'upper':126},{'lower':1024,'upper':1279},{'lower':8211,'upper':8217}]})
    register('fonts',name,'Font',data)

instance_template=room_template['layers'][0]['instances'][0]
button_layouts={}
def instance(room,name,x,y,values=None):
    data=copy.deepcopy(instance_template); inst='inst_'+uuid.uuid4().hex[:8].upper()
    data.update({'%Name':inst,'name':inst,'objectId':ref('objects',name),'x':x,'y':y,'imageSpeed':0,'properties':[]})
    for key,value in (values or {}).items():
        data['properties'].append({'$GMOverriddenProperty':'v1','%Name':'','name':'','objectId':ref('objects',name),'propertyId':{'name':key,'path':f'objects/{name}/{name}.yy'},'resourceType':'GMOverriddenProperty','resourceVersion':'2.0','value':json.dumps(value,ensure_ascii=False) if isinstance(value,str) else str(value)})
    return data
def room(name,layout):
    data=copy.deepcopy(room_template)
    data['%Name']=data['name']=name;data['creationCodeFile']='RoomCreationCode.gml'
    instances=[instance(name,*i) for i in layout]
    data['layers'][0]['instances']=instances
    data['layers'][1]['colour']=4280162063
    data['layers'][1]['depth']=10000
    button_layouts[name]=[i for i in layout if i[0]=='obj_button']
    data['instanceCreationOrder']=[{'name':i['name'],'path':f'rooms/{name}/{name}.yy'} for i in instances]
    register('rooms',name,'Rooms',data)
    (ROOT/'rooms'/name/'RoomCreationCode.gml').write_text('wp_room_setup();\n',encoding='utf-8',newline='\n')
def button(x,y,action,page='main',w=360,order=0):return ('obj_button',x,y,{'action':action,'page':page,'button_w':w,'nav_order':order})
common=[('obj_app',24,24),('obj_audio',64,24)]
options=[button(503,300,'music','options',360,0),button(503,360,'sfx','options',360,1),button(503,420,'fullscreen','options',360,2),button(503,480,'language','options',360,3),button(503,540,'effects','options',360,4),button(503,622,'back','options',360,5)]
language=[button(503,355,'english','language',360,0),button(503,417,'ukrainian','language',360,1)]
room('rm_boot',common+[('obj_splash',683,384)]+language)
menu_buttons=[button(80,338,'continue','main',360,0),button(80,398,'new','main',360,1),button(80,458,'options','main',360,2),button(80,518,'guide','main',360,3),button(80,578,'credits','main',360,4),button(80,638,'quit','main',360,5)]
confirm=[button(503,408,'confirm_new','confirm_new',360,0),button(503,470,'cancel','confirm_new',360,1)]
room('rm_menu',common+[('obj_menu',0,0)]+menu_buttons+options+language+confirm)
room('rm_text',common+[('obj_text',100,150),button(100,642,'back','text',300,0),button(930,642,'text_next','text',300,1)])
route=[(38,385),(145,385),(145,210),(350,210),(350,525),(560,525),(560,300),(775,300),(775,475),(965,475)]
pads=[(84,266),(248,320),(250,116),(454,159),(460,406),(469,635),(660,413),(670,203),(870,203),(885,365),(891,611),(711,619)]
world=common+[('obj_game',1000,24),('obj_wave',1040,24),('obj_board',0,0),('obj_hud',1060,0),('obj_core',966,475),('obj_portal',40,385)]
world += [('obj_path_node',x,y,{'node_order':i}) for i,(x,y) in enumerate(route)]
world += [('obj_build_pad',x,y,{'pad_key':f'pad_{i:02}'}) for i,(x,y) in enumerate(pads)]
for x,y,k in [(65,110,0),(167,93,0),(360,100,1),(553,110,0),(601,150,0),(752,120,0),(958,156,0),(1002,261,0),(84,555,0),(170,607,0),(280,669,0),(554,687,0),(1000,641,0),(52,696,0),(970,350,2),(1000,542,2),(975,420,3),(975,595,3),(243,454,1),(669,517,1),(393,650,4)]: world.append(('obj_decor',x,y,{'decor_kind':k}))
game_buttons=[button(1084,168,'wave','game',258,0),button(1084,227,'speed','game',124,1),button(1218,227,'pause','game',124,2),button(1084,398,'build0','game',258,3),button(1084,458,'build1','game',258,4),button(1084,518,'build2','game',258,5),button(1084,584,'upgrade','game',258,6),button(1084,641,'sell','game',258,7)]
pause=[button(503,290,'resume','pause',360,0),button(503,350,'save','pause',360,1),button(503,410,'load','pause',360,2),button(503,470,'options','pause',360,3),button(503,530,'guide','pause',360,4),button(503,590,'menu','pause',360,5)]
result=[button(503,460,'retry','result',360,0),button(503,522,'menu','result',360,1)]
room('rm_game',world+game_buttons+pause+options+language+result)
# Preserve the original resource as an editable practice room with the same systems.
room('Room1',world+game_buttons+pause+options+language+result)
layout_code=['// Generated fallback defaults. Room-authored positions always win.','function wp_ensure_buttons() {','    var _layout=[];','    switch(room) {']
for room_name,buttons in button_layouts.items():
    rows=[]
    for _,bx,by,values in buttons:
        rows.append('{x:'+str(bx)+',y:'+str(by)+',action:'+json.dumps(values['action'])+',page:'+json.dumps(values['page'])+',button_w:'+str(values['button_w'])+',nav_order:'+str(values['nav_order'])+'}')
    layout_code.append('        case '+room_name+': _layout=['+','.join(rows)+']; break;')
layout_code += ['    }','    for(var _i=0;_i<array_length(_layout);++_i) {','        var _b=_layout[_i],_found=false;','        with(obj_button) if(action==_b.action&&page==_b.page)_found=true;','        if(!_found)wp_spawn(obj_button,_b.x,_b.y,_b);','    }','}']
layout_dir=ROOT/'scripts/scr_layout';layout_dir.mkdir(parents=True,exist_ok=True)
(layout_dir/'scr_layout.gml').write_text('\n'.join(layout_code)+'\n',encoding='utf-8',newline='\n')
if not any(r['id']['name']=='scr_layout' for r in resources):
    register('scripts','scr_layout','Scripts',{**base('GMScript','scr_layout','v1'),'isCompatibility':False,'isDnD':False})
project['resources']=resources
project['RoomOrderNodes']=[{'roomId':ref('rooms',n)} for n in ['rm_boot','rm_menu','rm_text','rm_game','Room1']]
write('Wall Protocol.yyp',project)
write('Wall Protocol.resource_order',{'FolderOrderSettings':[{'name':n,'order':i,'path':f'folders/{n}.yy'} for i,n in enumerate(folders)],'ResourceOrderSettings':[]})
options=read(ROOT/'options/windows/options_windows.yy')
options.update(option_windows_company_info='Eclipse Wire',option_windows_copyright_info='Eclipse Wire',option_windows_description_info='Wall Protocol - The Last Ward',option_windows_resize_window=True,option_windows_version='1.1.0.0',option_windows_icon='${options_dir}/windows/icons/icon.ico')
write('options/windows/options_windows.yy',options)
print(f'Authored {len(resources)} resources and 5 rooms. Original backup: build/before-rework.zip')
