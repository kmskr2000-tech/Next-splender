import json,sys,os
from PIL import Image, ImageDraw
T=sys.argv[1]; out=sys.argv[2]
cards=json.load(open(T+"/docs/design/"+(sys.argv[3] if len(sys.argv)>3 else "roster.json")+""))["cards"]
cols=10; n=len(cards); rows=(n+cols-1)//cols
s=Image.new("RGBA",(cols*96,rows*96),(248,248,240,255))
for i,c in enumerate(cards):
    p=f"{T}/assets/creatures/{c['id']}.png"
    if os.path.exists(p): s.alpha_composite(Image.open(p).convert("RGBA"),((i%cols)*96,(i//cols)*96))
s.resize((s.width*3//2,s.height*3//2),Image.NEAREST).save(out)
