#!/usr/bin/env python3
"""Render pinned original Otto geometry into a 128x48 monochrome face region.

Eyes retain uniform shape scale; their centers are reflowed to a wide layout.
Original decorative primitives retain uniform local shape scale while their
anchors are reflowed vertically. Selected readability revisions use whole-
pixel glyphs outside the moving eyes. All work is offline; no Pillow/GIF in firmware.
"""
from pathlib import Path
import importlib.util,sys,math,json,hashlib,argparse
from PIL import Image,ImageDraw,ImageChops,ImageFont
ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/'third_party/otto/generate_emojis.py'
assert hashlib.sha256(UPSTREAM.read_bytes()).hexdigest() == '40dd14781fda254184b7f7d139b2abc803bf9efb09f7555ee0f6b174a0ddad58', 'Unrecognized upstream generator'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('otto_original',UPSTREAM)
original=importlib.util.module_from_spec(spec);sys.modules[spec.name]=original;spec.loader.exec_module(original)
W,H=128,48
EYE_SCALE=.34
DECOR_SCALE=.25
SS=4
MARGIN=16
class DecorationPainter:
    def __init__(self,dx=0,dy=0):
        self.canvas=Image.new('L',((W+2*MARGIN)*SS,(H+2*MARGIN)*SS),0);self.dx=dx;self.dy=dy
    def anchor(self,x,y):return (64+(x+self.dx-120)*.40+MARGIN,24+(y+self.dy-120)*.15+MARGIN)
    def polygon(self,points,*,fill=255,target=None):
        xs,ys=zip(*points);cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
        ax,ay=self.anchor(cx,cy)
        pts=[((ax+(x-cx)*DECOR_SCALE)*SS,(ay+(y-cy)*DECOR_SCALE)*SS) for x,y in points]
        ImageDraw.Draw(target or self.canvas).polygon(pts,fill=fill)
    def ellipse(self,x,y,w,h,*,fill=255,target=None):
        if w<=0 or h<=0:return
        ax,ay=self.anchor(x,y);rw=w*DECOR_SCALE/2;rh=h*DECOR_SCALE/2
        ImageDraw.Draw(target or self.canvas).ellipse(((ax-rw)*SS,(ay-rh)*SS,(ax+rw)*SS,(ay+rh)*SS),fill=fill)
    def stroke(self,points,width,*,fill=255,target=None):
        if width<=.2:return
        xs,ys=zip(*points);cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2;ax,ay=self.anchor(cx,cy)
        pts=[((ax+(x-cx)*DECOR_SCALE)*SS,(ay+(y-cy)*DECOR_SCALE)*SS) for x,y in points]
        draw=ImageDraw.Draw(target or self.canvas);line_width=max(1,round(width*DECOR_SCALE*SS))
        if len(pts)>1:draw.line(pts,fill=fill,width=line_width,joint='curve')
        r=line_width/2
        for x,y in pts:draw.ellipse((x-r,y-r,x+r,y+r),fill=fill)

REVISED_DECORATIONS = frozenset({"surprised", "confused", "delicious", "angry", "embarrassed"})
DECORATION_EYE_PADDING = 2

def eye_guard(face):
    """The original OLED eye-render path, unchanged; decorations are separate."""
    guard=Image.new('L',((W+2*MARGIN)*SS,(H+2*MARGIN)*SS),0)
    # Render each eye with unmodified original geometry/drawing, then uniformly
    # scale its layer and reposition its original anchor into the OLED layout.
    size=round(original.SIZE*original.SCALE*EYE_SCALE)
    for eye,side,source_x,target_x in [(face.left,1,original.LEFT_X,40),(face.right,-1,original.RIGHT_X,88)]:
        p=original.Painter(face.dx,face.dy);original.draw_eye(p,eye,side)
        layer=p.canvas.resize((size,size),Image.Resampling.LANCZOS)
        origin=(round((target_x-source_x*EYE_SCALE+MARGIN)*SS),round((24-original.EYE_Y*EYE_SCALE+MARGIN)*SS))
        mask=Image.new('L',guard.size,0);mask.paste(layer,origin);guard=ImageChops.lighter(guard,mask)
    return guard

def binary_guard(guard):
    small=guard.resize((W+2*MARGIN,H+2*MARGIN),Image.Resampling.BOX)
    return small.point(lambda x:255 if x>=96 else 0).convert('1',dither=Image.Dither.NONE)

def render_eyes(name,index):
    fn,count=original.EXPRESSIONS[name]
    binary=binary_guard(eye_guard(fn(index/count)))
    return binary.crop((MARGIN,MARGIN,MARGIN+W,MARGIN+H)),binary

def pixel_decorations(name,t):
    """Readable whole-pixel glyphs in free space outside the moving eye envelope.

    Keep the original envelope/repetition rhythm; quantize birth/death and motion
    instead of scaling strokes through subpixel sizes. No clipping/masking against
    a moving eye: the exhaustive test checks a fixed two-pixel envelope clearance.
    """
    image=Image.new('1',(W,H),0)
    draw=ImageDraw.Draw(image)
    attack={"surprised":.14,"confused":.18,"delicious":.18,"angry":.16,"embarrassed":.18}[name]
    amount=original.envelope(t,attack,ease=original.pop if name=="surprised" else original.smooth)
    if amount<.20:return image
    if name=="surprised":
        # Three detached rays on each OUTER side, not eyelashes on the lid.
        rays=[[(22,8),(18,4)],[(21,14),(15,13)],[(22,20),(17,24)]]
        for ray in rays:
            draw.line(ray,fill=1,width=2)
            draw.line([(127-x,y) for x,y in ray],fill=1,width=2)
    elif name=="confused":
        # A stable 2px hook and 2x2 dot with three empty rows between them.
        dx=round(original.wave(t,2)*amount)
        hook=[(110+dx,8),(110+dx,6),(112+dx,4),(115+dx,4),
              (117+dx,6),(117+dx,8),(114+dx,11),(114+dx,13)]
        draw.line(hook,fill=1,width=2,joint='curve')
        draw.rectangle((113+dx,17,114+dx,18),fill=1)
    elif name=="delicious":
        # Preserve the original twice-per-loop hang/fall rhythm. The drop remains
        # a recognizable 7x8px silhouette instead of a thresholded single pixel.
        u=original.cycle(t,2)
        fall=max(0,(u-.6)/.4)
        y=34+round(5*fall*fall)
        x=65
        if u<.6:draw.line([(x,30),(x,y+2)],fill=1,width=2)
        drop=[(x,y),(x-1,y+2),(x-3,y+4),(x-3,y+6),(x-2,y+7),
              (x+2,y+7),(x+3,y+6),(x+3,y+4),(x+1,y+2)]
        draw.polygon(drop,fill=1)
        if amount>=.7:
            # The original upper-right sparkle, made detached and pixel-stable.
            draw.line([(111,7),(111,11)],fill=1,width=1)
            draw.line([(109,9),(113,9)],fill=1,width=1)
    elif name=="embarrassed":
        # Three readable diagonal blush marks below EACH moving-eye envelope.
        # Keep the original four-cycle, phase-offset blush pulse, quantized to
        # 3/4px lengths so no line dissolves into an isolated pixel.
        for cheek in (0,48):
            for i,x in enumerate((29,35,41)):
                length=4 if original.wave(t,4,i/3)>=0 else 3
                # Row-defined 2px bands avoid the cross-shaped tips produced
                # by a short diagonal line primitive at this tiny resolution.
                for row in range(length+1):
                    shift=round(2*(length-row)/length)
                    draw.rectangle((x+cheek+shift,40+row,
                                    x+cheek+shift+1,40+row),fill=1)
        # A detached 7x9 sweat drop; original once-per-loop slow fall becomes
        # three whole-pixel steps rather than a tiny subpixel triangle.
        x=113;y=7+round(3*original.cycle(t,1))
        draw.polygon([(x,y),(x-1,y+2),(x-3,y+5),(x-3,y+7),(x-2,y+8),
                      (x+2,y+8),(x+3,y+7),(x+3,y+5),(x+1,y+2)],fill=1)
    elif name=="angry":
        # Four separate manga-vein corners; 2px strokes cannot fragment. Retain
        # the original three throbs per loop using two integer radii.
        radius=6 if abs(original.wave(t,3))>=.5 else 5
        cx,cy=114,10
        for sx in (-1,1):
            for sy in (-1,1):
                corner=[(cx+sx*radius,cy+sy*2),
                        (cx+sx*3,cy+sy*3),(cx+sx*2,cy+sy*radius)]
                draw.line(corner,fill=1,width=2,joint='curve')
    return image

def render(name,index):
    fn,count=original.EXPRESSIONS[name];face=fn(index/count)
    guard=eye_guard(face)
    if name in REVISED_DECORATIONS:
        binary=binary_guard(guard)
        decorations=Image.new('1',binary.size,0)
        decorations.paste(pixel_decorations(name,index/count),(MARGIN,MARGIN))
        binary=ImageChops.lighter(binary,decorations)
    else:
        # Preserve the original composite path exactly for the other 16.
        extra=DecorationPainter(face.dx,face.dy)
        for draw in face.extras:draw(extra)
        binary=binary_guard(ImageChops.lighter(guard,extra.canvas))
    image=binary.crop((MARGIN,MARGIN,MARGIN+W,MARGIN+H))
    return image,binary

def pack(image):return image.tobytes()
def rle(data):
    # Byte PackBits: high bit run, low7bits length-1; literals otherwise.
    out=bytearray();i=0
    while i<len(data):
        run=1
        while i+run<len(data) and data[i+run]==data[i] and run<128:run+=1
        if run>=3:out.extend((0x80|(run-1),data[i]));i+=run;continue
        start=i;i+=run
        while i<len(data) and i-start<128:
            run=1
            while i+run<len(data) and data[i+run]==data[i] and run<3:run+=1
            if run>=3:break
            i+=min(run,128-(i-start))
        out.append(i-start-1);out.extend(data[start:i])
    return bytes(out)
def un_rle(data):
    out=bytearray();i=0
    while i<len(data):
        c=data[i];i+=1;n=(c&127)+1
        if c&128:out.extend([data[i]]*n);i+=1
        else:out.extend(data[i:i+n]);i+=n
    return bytes(out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--output',type=Path,default=ROOT/'build/generated');args=ap.parse_args();out=args.output;preview=out/'previews';preview.mkdir(parents=True,exist_ok=True)
    metadata=[];unique={};frames=[];total=0;clipped=[]
    font=ImageFont.load_default();sheet=Image.new('RGB',(5*270,5*132),(31,37,42));label=ImageDraw.Draw(sheet)
    for row,(name,(fn,count)) in enumerate(original.EXPRESSIONS.items()):
        images=[];encoded=[];bounds=[];extras_visible=0
        for i in range(count):
            im,guard=render(name,i);images.append(im);data=pack(im);blob=rle(data);assert un_rle(blob)==data and len(data)==768
            if data not in unique:unique[data]=len(unique);frames.append(blob)
            encoded.append(unique[data]);bounds.append(im.getbbox())
            outside=guard.copy();ImageDraw.Draw(outside).rectangle((MARGIN,MARGIN,MARGIN+W-1,MARGIN+H-1),fill=0)
            if outside.getbbox():clipped.append({'name':name,'frame':i,'bbox':outside.getbbox()})
        total+=count
        # Middle hold frame, away from loop-neutral boundaries and exact blinks.
        hold=round(count*.35);im=images[hold]
        if not args.check:im.resize((W*4,H*4),Image.Resampling.NEAREST).save(preview/f'{name}.png')
        if not args.check:images[0].resize((W*3,H*3),Image.Resampling.NEAREST).save(preview/f'{name}.gif',save_all=True,append_images=[x.resize((W*3,H*3),Image.Resampling.NEAREST) for x in images[1:]],duration=80,loop=0,optimize=False)
        col=row%5;line=row//5;x=col*270+7;y=line*132+7;label.text((x,y),name,font=font,fill='white');sheet.paste(im.convert('RGB').resize((256,96),Image.Resampling.NEAREST),(x,y+18))
        metadata.append({'name':name,'frames':count,'frame_ids':encoded,'lit_bounds_union':(min(b[0] for b in bounds if b),min(b[1] for b in bounds if b),max(b[2] for b in bounds if b),max(b[3] for b in bounds if b))})
    if not args.check:sheet.crop((0,0,1350,5*132)).save(preview/'otto-expression-sheet.png')
    payload=b''.join(frames)
    if not args.check:(out/'otto-frames.rle').write_bytes(payload)
    offsets=[0]
    for blob in frames:offsets.append(offsets[-1]+len(blob))
    report={'upstream_commit':'4a666924e8e4e2bb55fb9d3167211bb936224abf','generator_sha256':hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),'width':W,'height':H,'frame_duration_ms':80,'source_frames':total,'unique_frames':len(frames),'raw_bytes':total*768,'compressed_payload_bytes':len(payload),'frame_offset_bytes':len(offsets)*4,'expression_index_bytes':total*2,'worst_compressed_frame_bytes':max(map(len,frames)),'clipped_frames':clipped,'frames':metadata,'offsets':offsets}
    assert not clipped,'Generated lit pixels exceed128x48'
    if args.check:
        expected=ROOT/'include/third_party/otto/otto_assets.inc'
        assert expected.read_text()==asset_include(report,payload),'Generated Otto assets differ'
        print('Otto original generator: all884 frames fit; exact firmware assets reproduced')
        return
    (out/'generation.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'otto_assets.inc').write_text(asset_include(report,payload))
    print(json.dumps({k:v for k,v in report.items() if k not in ['frames','offsets','clipped_frames']},indent=2));print('Clipped frames:',len(clipped))
def asset_include(report,payload):
    def array(name,kind,values,perline):
        lines=[f"inline constexpr {kind} {name}[] = {{"]
        for i in range(0,len(values),perline):lines.append("    "+",".join(str(x) for x in values[i:i+perline])+",")
        return "\n".join(lines+["};"])
    flat=[x for expr in report['frames'] for x in expr['frame_ids']]
    lines=["// Generated by scripts/upstream/otto/generate_oled.py; do not edit.",
           "// Original Otto MIT source and provenance are alongside this file.",
           "#pragma once", "#include <cstdint>", "namespace otto_assets {",
           "inline constexpr uint32_t FrameDurationMs=80;",
           "inline constexpr unsigned Width=128,Height=48,FrameBytes=768;",
           "struct Expression {const char* name;uint16_t first,count;};",
           array("Pixels","uint8_t",list(payload),32),array("Offsets","uint32_t",report['offsets'],12),
           array("FrameIds","uint16_t",flat,20),"inline constexpr Expression Expressions[] = {"]
    first=0
    for expr in report['frames']:
        lines.append(f'    {{"{expr["name"]}",{first},{expr["frames"]}}},');first+=expr['frames']
    lines += ["};", "inline constexpr unsigned ExpressionCount=sizeof(Expressions)/sizeof(Expressions[0]);",
              "inline constexpr unsigned UniqueFrames=sizeof(Offsets)/sizeof(Offsets[0])-1;", "} // namespace otto_assets",""]
    return "\n".join(lines)
if __name__=='__main__':main()
