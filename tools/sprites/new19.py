import json,sys
from PIL import Image, ImageDraw, ImageFont
T=sys.argv[1]; out=sys.argv[2]; sc=int(sys.argv[3]) if len(sys.argv)>3 else 3
IDS="t1-022 t2-020 t1-016 t2-014 t1-013 t2-013 t1-024 t2-022 t1-008 t2-008 t3-008 t1-034 t3-014 t3-015 rare-002 rare-004 legend-001 legend-004 t1-035".split()
cards={c['id']:c for c in json.load(open(T+"/docs/design/roster-korea.json"))["cards"]}
import glob
fs=glob.glob("/usr/share/fonts/**/*CJK*",recursive=True)+glob.glob("/usr/share/fonts/**/*Nanum*",recursive=True)
font=ImageFont.truetype(fs[0],14) if fs else ImageFont.load_default()
cols=5; W=96*sc; rows=(len(IDS)+cols-1)//cols
s=Image.new("RGBA",(cols*W,rows*(W+20)),(248,248,240,255)); d=ImageDraw.Draw(s)
for i,k in enumerate(IDS):
    x,y=(i%cols)*W,(i//cols)*(W+20)
    im=Image.open(f"{T}/assets/creatures/{k}.png").convert("RGBA").resize((W,W),Image.NEAREST)
    s.alpha_composite(im,(x,y)); d.text((x+4,y+W+2),k+" "+cards[k]["name"],fill=(20,20,20,255),font=font)
s.convert("RGB").save(out)
