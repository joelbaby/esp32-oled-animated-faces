#!/usr/bin/env python3
"""Render an illustrative status bar above the actual compressed happy animation."""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'include/third_party/otto/otto_assets.inc').read_text()
def values(name):
 return list(map(int,re.findall(r'\d+',re.search(r'\b'+name+r'\[\] = \{(.*?)\};',text,re.S).group(1))))
payload,offsets,ids=values('Pixels'),values('Offsets'),values('FrameIds')
first,count=map(int,re.search(r'\{"happy",(\d+),(\d+)\}',text).groups())
status=Image.new('1',(128,16));d=ImageDraw.Draw(status)
for x,h in [(4,3),(8,5),(12,7)]:d.rectangle((x,11-h,x+1,11),fill=1)
d.text((43,2),'READY',font=ImageFont.load_default(),fill=1)
d.rectangle((108,4,122,11),outline=1);d.rectangle((123,6,124,9),fill=1);d.rectangle((110,6,118,9),fill=1)
base=Image.new('RGB',(1000,400),'#14191e');d=ImageDraw.Draw(base)
font=ImageFont.load_default(size=20);small=ImageFont.load_default(size=17);title=ImageFont.load_default(size=28)
d.text((24,18),'Room for your status bar',font=title,fill='white')
d.text((24,57),'128 x 64 OLED layout | shown at 4x scale',font=small,fill='#b9c8d1')
x,y=24,98
d.rectangle((x-2,y-2,x+513,y+257),outline='#657a88',width=2)
d.line((550,y,550,y+63),fill='#7ed9c0',width=2);d.line((550,y,561,y),fill='#7ed9c0',width=2);d.line((550,y+63,561,y+63),fill='#7ed9c0',width=2)
d.text((578,y+7),'16 px - status area',font=font,fill='#7ed9c0');d.text((578,y+34),'Rows 0-15 | stays untouched',font=small,fill='#c5d0d8')
d.line((550,y+64,550,y+255),fill='#9bc8ff',width=2);d.line((550,y+64,561,y+64),fill='#9bc8ff',width=2);d.line((550,y+255,561,y+255),fill='#9bc8ff',width=2)
d.text((578,y+124),'48 px - animated face',font=font,fill='#9bc8ff');d.text((578,y+153),'Rows 16-63 | actual assets',font=small,fill='#c5d0d8')
d.text((24,372),'Illustrative status icons; not a hardware capture. Otto expressions by txp666.',font=small,fill='#b9c8d1')
frames=[]
for index in range(count):
 frame_id=ids[first+index];data=payload[offsets[frame_id]:offsets[frame_id+1]];out=bytearray();i=0
 while i<len(data):
  command=data[i];i+=1;n=(command&127)+1
  if command&128:out.extend([data[i]]*n);i+=1
  else:out.extend(data[i:i+n]);i+=n
 assert len(out)==768
 face=Image.frombytes('1',(128,48),bytes(out));screen=Image.new('1',(128,64));screen.paste(status,(0,0));screen.paste(face,(0,16))
 assert screen.crop((0,0,128,16)).tobytes()==status.tobytes()
 assert screen.crop((0,16,128,64)).tobytes()==bytes(out)
 image=base.copy();image.paste(screen.resize((512,256),Image.Resampling.NEAREST),(x,y));frames.append(image.quantize(colors=64))
dest=ROOT/'docs/images';dest.mkdir(parents=True,exist_ok=True)
frames[0].save(dest/'status-bar-layout.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=False)
frames[15].save(dest/'status-bar-layout.png')
with Image.open(dest/'status-bar-layout.gif') as im:
 total_ms=0
 for k in range(im.n_frames):
  im.seek(k);assert im.info['duration']%80==0;total_ms+=im.info['duration']
 assert total_ms==count*80
print(f'PASS: {count} actual frames; status pixels fixed; lower48 exact; GIF timing80ms')
