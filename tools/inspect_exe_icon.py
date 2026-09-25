"""Read PE icon resources without running the executable or using a desktop API."""
from pathlib import Path
import struct,io,json
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[1]
raw=(root/'build/package/Wall Protocol.exe').read_bytes()
pe=struct.unpack_from('<I',raw,0x3c)[0]
sections=struct.unpack_from('<H',raw,pe+6)[0]
optional_size=struct.unpack_from('<H',raw,pe+20)[0]
opt=pe+24;magic=struct.unpack_from('<H',raw,opt)[0]
directory=opt+(112 if magic==0x20b else 96)
rva,size=struct.unpack_from('<II',raw,directory+16)
section_table=opt+optional_size
def offset(addr):
    for i in range(sections):
        item=section_table+i*40
        vs,va,rs,ptr=struct.unpack_from('<IIII',raw,item+8)
        if va<=addr<va+max(vs,rs):return ptr+addr-va
    raise ValueError(addr)
base=offset(rva)
def entries(at):
    named,count=struct.unpack_from('<HH',raw,at+12)
    return [struct.unpack_from('<II',raw,at+16+i*8) for i in range(named+count)]
def resource_types():
    found={}
    for typ,to in entries(base):
        for name,no in entries(base+(to&0x7fffffff)):
            for lang,lo in entries(base+(no&0x7fffffff)):
                va,size=struct.unpack_from('<II',raw,base+lo)
                found[(typ,name,lang)]=raw[offset(va):offset(va)+size]
    return found
resources=resource_types()
icons={key[1]:val for key,val in resources.items() if key[0]==3}
groups=[val for key,val in resources.items() if key[0]==14]
reports=[]
for gi,group in enumerate(groups):
    count=struct.unpack_from('<H',group,4)[0];header=bytearray(group[:6]);images=[];position=6+16*count
    for i in range(count):
        info=group[6+i*14:6+(i+1)*14]
        icon_id=struct.unpack_from('<H',info,12)[0];payload=icons[icon_id]
        header.extend(info[:8]+struct.pack('<II',len(payload),position));images.append(payload);position+=len(payload)
    ico=bytes(header)+b''.join(images)
    p=root/f'build/verification/compiled-icon-{gi}.ico';p.write_bytes(ico)
    im=Image.open(io.BytesIO(ico)).convert('RGBA');im.save(p.with_suffix('.png'))
    reference=Image.open(root/'options/windows/icons/icon.ico').convert('RGBA').resize(im.size,Image.Resampling.LANCZOS)
    diff=ImageChops.difference(im,reference)
    error=sum(sum(channel) for channel in zip(*diff.getdata()))/(im.width*im.height*4)
    reports.append({'group':gi,'entries':count,'size':im.size,'mean_pixel_error':error,'custom_icon':error<3})
print(json.dumps(reports,indent=2))
(root/'build/verification/icon-check.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
