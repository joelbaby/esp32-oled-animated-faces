#!/usr/bin/env python3
"""Verify a decoration-only revision against pre-revision raster fingerprints."""
from pathlib import Path
import argparse, hashlib, importlib.util, json
from PIL import Image, ImageChops, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'build/decoration-checks.json')
a=p.parse_args()
spec=importlib.util.spec_from_file_location('decoration_generator',ROOT/'tools/generate_assets.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
baseline=json.loads((ROOT/'tests/decoration-baseline.json').read_text())
rc2=json.loads((ROOT/'tests/decoration-rc2-baseline.json').read_text())
assert hashlib.sha256(g.UPSTREAM.read_bytes()).hexdigest()==baseline['original_upstream_generator_sha256']
assert list(g.original.EXPRESSIONS)==list(baseline['expressions'])
assert g.original.FRAME_DURATION_MS==baseline['frame_duration_ms']==80

def components(image):
    unseen={(x,y) for y in range(image.height) for x in range(image.width) if image.getpixel((x,y))}
    areas=[]
    while unseen:
        pending=[unseen.pop()];area=0
        while pending:
            x,y=pending.pop();area+=1
            neighbors={(x+dx,y+dy) for dx in [-1,0,1] for dy in [-1,0,1]}
            found=unseen & neighbors;unseen-=found;pending.extend(found)
        areas.append(area)
    return sorted(areas)

report={'eyes_only_frames_exact':0,'untouched_full_frames_exact':0,'no_clipping_frames':0,
        'codec_roundtrips':0,'decoration_eye_padding_pixels':g.DECORATION_EYE_PADDING,
        'frame_duration_ms':80,'untouched_rc2_full_frames_exact':0,'expressions':{}}
for name,(_,count) in g.original.EXPRESSIONS.items():
    old=baseline['expressions'][name];assert count==old['frames']
    eye_union=Image.new('1',(128,48),0);decorations=[];full_hash=hashlib.sha256()
    for index in range(count):
        eyes,_=g.render_eyes(name,index)
        assert hashlib.sha256(eyes.tobytes()).hexdigest()==old['eyes_sha256'][index],(name,index,'eyes changed')
        report['eyes_only_frames_exact']+=1
        eye_union=ImageChops.lighter(eye_union,eyes)
        frame,guard=g.render(name,index);data=frame.tobytes();full_hash.update(data)
        assert len(data)==768 and g.un_rle(g.rle(data))==data
        report['codec_roundtrips']+=1
        outside=guard.copy();ImageDraw.Draw(outside).rectangle((g.MARGIN,g.MARGIN,g.MARGIN+127,g.MARGIN+47),fill=0)
        assert not outside.getbbox(),(name,index,'clipped')
        report['no_clipping_frames']+=1
        if name in g.REVISED_DECORATIONS:
            decoration=g.pixel_decorations(name,index/count);decorations.append(decoration)
            assert ImageChops.logical_and(frame,eyes).tobytes()==eyes.tobytes()
    if name!='embarrassed':
        assert full_hash.hexdigest()==rc2['expressions'][name]['full_rasters_sha256'],(name,'approved rc2 frame changed')
        report['untouched_rc2_full_frames_exact']+=count
    else:
        assert full_hash.hexdigest()!=rc2['expressions'][name]['full_rasters_sha256'],(name,'embarrassed revision missing')
    if name not in g.REVISED_DECORATIONS:
        assert full_hash.hexdigest()==old['full_rasters_sha256'],(name,'non-target changed')
        report['untouched_full_frames_exact']+=count
    else:
        assert full_hash.hexdigest()!=old['full_rasters_sha256'],(name,'revision missing')
        forbidden=eye_union.convert('L').filter(ImageFilter.MaxFilter(2*g.DECORATION_EYE_PADDING+1)).convert('1')
        visible=[];component_areas=[]
        for index,decoration in enumerate(decorations):
            assert not ImageChops.logical_and(decoration,forbidden).getbbox(),(name,index,'decoration crowds eye envelope')
            areas=components(decoration)
            if areas:
                visible.append(index);component_areas+=areas
                expected=6 if name=='surprised' else 2 if name=='confused' else 4 if name=='angry' else 7 if name=='embarrassed' else None
                if expected:assert len(areas)==expected,(name,index,areas,'fragmented glyph')
                assert min(areas)>=4,(name,index,areas,'isolated speck')
        assert visible==list(range(visible[0],visible[-1]+1)),(name,'visibility flicker')
        report['expressions'][name]={'frames':count,'visible_frames':visible,'minimum_connected_component_pixels':min(component_areas),'eye_envelope_bbox':eye_union.getbbox(),'full_rasters_sha256':full_hash.hexdigest(),'clearance_all_frames':True}
assert report['eyes_only_frames_exact']==report['no_clipping_frames']==report['codec_roundtrips']==884
assert report['untouched_full_frames_exact']==680
assert report['untouched_rc2_full_frames_exact']==840
report['status']='PASS; visual review pending, no firmware build/flash/freeze'
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
print('PASS: all884 eye-only frames exact; all840 full frames of other20 match rc2 including approved4; original680 frames of remaining16 exact; all204 revised decoration masks clear moving-eye envelopes by2px; no clipping/specks; codec roundtrips exact')
