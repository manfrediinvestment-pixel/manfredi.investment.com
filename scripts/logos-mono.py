# Genera assets/logos/mono/*.png: cada logo de assets/logos en blanco con fondo
# transparente, recortado a su contorno (para las tapas de Informes).
# Uso: python scripts/logos-mono.py assets/logos assets/logos/mono hoja.png
import sys, os
from PIL import Image, ImageChops
src, out, sheet = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
def dist(img, color, thr=18, span=150):
    ref = Image.new('RGB', img.size, color)
    d = ImageChops.difference(img, ref); r,g,b = d.split()
    a = ImageChops.lighter(ImageChops.lighter(r,g),b)
    return a.point(lambda v: 0 if v < thr else min(255, int((v-thr)*255/span)))
def stretch(a):
    h = a.histogram(); tot = sum(h[1:]) or 1; acc=0; p=255
    for v in range(255,0,-1):
        acc += h[v]
        if acc > tot*0.05: p=v; break
    return a if p >= 230 else a.point(lambda v: min(255,int(v*255/max(p,1))))
tiles=[]; boxed=[]
for f in sorted(os.listdir(src)):
    if not f.endswith('.png'): continue
    im = Image.open(os.path.join(src,f)).convert('RGBA')
    comp = Image.alpha_composite(Image.new('RGBA', im.size, (255,255,255,255)), im).convert('RGB')
    a = dist(comp, (255,255,255)); bb = a.getbbox()
    if not bb: continue
    c2 = comp.crop(bb); a2 = a.crop(bb); w,h = a2.size
    m = max(2, min(w,h)//25)
    corners = [(m,m),(w-1-m,m),(m,h-1-m),(w-1-m,h-1-m)]
    if f not in ('msft.png','nflx.png','intc.png','sap.png') and sum(a2.getpixel(p) > 200 for p in corners) >= 3:   # logo dentro de un recuadro de color
        col = c2.getpixel(corners[0]); boxed.append(f)
        a2 = dist(c2, col, thr=40, span=120)
        # descartar el borde del recuadro
        inset = max(3, min(w,h)//14)
        mask = Image.new('L', a2.size, 0); mask.paste(255, (inset,inset,w-inset,h-inset))
        a2 = ImageChops.multiply(a2, mask)
        bb2 = a2.getbbox()
        if bb2: a2 = a2.crop(bb2)
    a2 = stretch(a2)
    c = Image.new('RGBA', a2.size, (255,255,255,0)); c.putalpha(a2)
    k = 320 / max(c.size)
    c = c.resize((max(1,round(c.size[0]*k)), max(1,round(c.size[1]*k))), Image.LANCZOS)
    c.save(os.path.join(out,f), optimize=True); tiles.append(c)
cols=10; rows=(len(tiles)+cols-1)//cols
sh=Image.new('RGB',(cols*110,rows*110),(11,22,48))
for i,c in enumerate(tiles):
    t=c.copy(); t.thumbnail((90,90)); sh.paste(t,((i%cols)*110+10,(i//cols)*110+10),t)
sh.save(sheet); print(boxed)
