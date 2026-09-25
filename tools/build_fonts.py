"""Compile complete Latin/Ukrainian bitmap font atlases for portable CLI builds."""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
for name,pixels,ttf in [('fnt_ui',18,'arial.ttf'),('fnt_heading',32,'georgiab.ttf'),('fnt_title',70,'georgiab.ttf')]:
    path=root/'fonts'/name/(name+'.yy')
    data=json.loads(path.read_text(encoding='utf-8'))
    font=ImageFont.truetype('C:/Windows/Fonts/'+ttf,pixels)
    ascent,descent=font.getmetrics();line=ascent+descent+2
    codes=list(range(32,127))+list(range(1024,1280))+list(range(8211,8218))+[8226,9647]
    atlas=Image.new('RGBA',(1024,2048));draw=ImageDraw.Draw(atlas)
    glyphs={};x=y=2
    for code in codes:
        char=chr(code);left,top,right,bottom=font.getbbox(char,anchor='ls')
        width=max(1,math.ceil(right-left));advance=round(font.getlength(char))
        if x+width+2>1024:x=2;y+=line+2
        draw.text((x-left,y+ascent),char,font=font,fill=(255,255,255,255),anchor='ls')
        glyphs[str(code)]={'character':code,'h':line,'offset':left,'shift':advance,'w':width,'x':x,'y':y}
        x+=width+3
    finalheight=2**math.ceil(math.log2(y+line+2))
    atlas.crop((0,0,1024,finalheight)).save(path.with_suffix('.png'))
    data.update(glyphs=glyphs,kerningPairs=[],ascender=ascent,ascenderOffset=0,lineHeight=line,size=pixels*.75,regenerateBitmap=False,canGenerateBitmap=True,applyKerning=0,styleName='Bold' if 'b.' in ttf else 'Regular')
    data['ranges']=[{'lower':32,'upper':126},{'lower':1024,'upper':1279},{'lower':8211,'upper':8217},{'lower':8226,'upper':8226},{'lower':9647,'upper':9647}]
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(name,len(glyphs),'glyphs',1024,finalheight)
