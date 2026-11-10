"""Gera pixel art original e sons originais; requer Pillow apenas para recriar imagens.
Os arquivos PNG e WAV já acompanham o ZIP: executar o jogo não requer Pillow.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import random, math, wave, struct
BASE=Path(__file__).resolve().parent/'assets';BASE.mkdir(exist_ok=True)
random.seed(43)
W,H=256,132

def scene(nome,tema):
    im=Image.new('RGB',(W,H),(16,18,29)); d=ImageDraw.Draw(im)
    # Wood ceiling, walls and perspective floor
    d.rectangle((0,0,255,22),fill=(24,23,34))
    d.polygon([(0,22),(255,22),(255,94),(0,94)],fill=tema)
    d.polygon([(0,95),(255,95),(255,131),(0,131)],fill=(42,34,40))
    for y in range(98,132,9):d.line((0,y,255,y),fill=(67,49,47),width=1)
    for x in range(0,256,22):d.line((x,97,x+12,132),fill=(69,48,45),width=1)
    for x in range(0,256,32):d.rectangle((x,16,x+3,98),fill=(38,33,44))
    for x in range(0,256,16):
        d.line((x,3,x,18),fill=(45,41,49))
    # lamps
    for x in [28,226]:
        d.rectangle((x-2,29,x+2,44),fill=(100,76,57))
        d.ellipse((x-6,24,x+6,36),fill=(164,112,68))
        d.ellipse((x-3,27,x+3,32),fill=(250,181,92))
    if nome=='hall':
        # ornate portrait
        d.rectangle((22,27,82,82),fill=(136,93,53),outline=(213,163,82),width=3)
        d.rectangle((27,32,77,77),fill=(49,58,63))
        for x in [41,58]:
            d.ellipse((x,40,x+10,53),fill=(174,142,114));d.rectangle((x-2,53,x+13,72),fill=(48,43,63))
        d.rectangle((18,86,82,112),fill=(83,49,41),outline=(146,102,64),width=2)
        for x in [30,65]:d.ellipse((x,98,x+3,101),fill=(221,167,87))
        d.rectangle((130,35,177,113),fill=(65,42,45),outline=(139,98,68),width=4)
        d.rectangle((138,42,168,108),fill=(32,26,39))
        d.ellipse((159,75,163,79),fill=(219,171,90))
        d.polygon([(193,92),(216,44),(239,92)],fill=(55,62,74))
    elif nome=='biblioteca':
        for x in [12,68,183]:
            d.rectangle((x,26,x+55,101),fill=(67,45,39),outline=(128,88,61),width=3)
            for y in [45,68,91]:
                d.line((x+3,y,x+52,y),fill=(150,99,60),width=3)
                for bx in range(x+6,x+51,6):
                    d.rectangle((bx,y-16,bx+4,y-3),fill=random.choice([(102,56,54),(73,86,83),(129,105,65),(55,75,92)]))
        d.ellipse((88,60,129,102),fill=(93,103,104),outline=(205,164,89),width=2)
        d.line((110,59,110,104),fill=(190,152,83),width=2)
        d.rectangle((139,72,184,113),fill=(56,58,67),outline=(166,138,88),width=3)
        d.rectangle((148,81,173,105),fill=(25,30,37))
    elif nome=='escritorio':
        d.rectangle((22,62,98,103),fill=(85,52,43),outline=(151,99,63),width=3)
        d.polygon([(28,60),(91,60),(101,75),(16,75)],fill=(112,76,55))
        d.polygon([(34,50),(78,50),(84,66),(27,66)],fill=(192,170,126))
        d.line((35,54,71,54),fill=(94,78,69),width=2)
        d.ellipse((98,20,143,65),fill=(159,124,78),outline=(210,172,91),width=4)
        d.ellipse((107,29,134,56),fill=(47,51,57))
        d.line((121,42,121,32),fill=(235,213,171),width=2)
        d.line((121,42,132,49),fill=(235,213,171),width=2)
        d.rectangle((153,44,203,115),fill=(79,55,46),outline=(168,110,69),width=4)
        for y in [62,83,105]:d.line((158,y,197,y),fill=(130,88,62),width=2)
        d.rectangle((212,42,253,118),fill=(28,27,37),outline=(109,87,66),width=4)
    elif nome=='porao':
        d.rectangle((0,20,255,99),fill=(38,43,49))
        for y in range(24,96,13):
            for x in range((y%26)-20,256,31):d.rectangle((x,y,x+29,y+11),outline=(62,65,68))
        d.rectangle((17,69,75,103),fill=(61,53,52),outline=(108,94,75),width=3)
        d.ellipse((82,66,111,97),outline=(158,116,77),width=4)
        d.rectangle((119,65,132,94),fill=(151,130,94))
        d.polygon([(121,66),(126,51),(131,66)],fill=(239,164,69))
        d.rectangle((142,49,191,106),fill=(50,62,65),outline=(143,125,91),width=3)
        for y in [64,79,94]:d.line((148,y,184,y),fill=(116,132,130),width=2)
        d.rectangle((202,27,253,119),fill=(29,30,36),outline=(136,128,110),width=3)
        for x in range(211,251,9):d.line((x,30,x,116),fill=(116,125,121),width=3)
    elif nome=='camara':
        d.ellipse((14,21,88,92),fill=(57,52,67),outline=(133,93,91),width=4)
        d.polygon([(39,80),(55,40),(73,80)],fill=(136,78,73))
        d.rectangle((93,74,160,114),fill=(85,76,75),outline=(159,123,96),width=4)
        d.polygon([(92,73),(127,54),(161,73)],fill=(112,98,87))
        d.rectangle((182,20,249,119),fill=(28,26,34),outline=(190,148,87),width=4)
        d.polygon([(196,107),(216,44),(237,107)],fill=(56,56,65))
        d.ellipse((210,69,223,82),fill=(238,177,86))
    # dust and pixel highlights
    for _ in range(120):
        x=random.randrange(256);y=random.randrange(20,119)
        if random.random()<.55:d.point((x,y),fill=(83,73,74))
    big=im.resize((1024,528),Image.Resampling.NEAREST)
    big.save(BASE/(nome+'.png'))

for n,c in [('hall',(54,43,54)),('biblioteca',(44,50,54)),('escritorio',(52,42,49)),('porao',(37,43,47)),('camara',(45,39,52))]:scene(n,c)
# Cover: exterior manor with moon and windows
im=Image.new('RGB',(256,175),(15,17,30));d=ImageDraw.Draw(im)
for _ in range(130):
    x=random.randrange(256);y=random.randrange(95)
    d.point((x,y),fill=random.choice([(61,66,87),(91,91,111),(46,52,72)]))
d.ellipse((175,13,214,52),fill=(216,200,160))
d.polygon([(0,150),(55,110),(104,128),(155,98),(230,123),(256,110),(256,175),(0,175)],fill=(25,30,38))
d.polygon([(34,84),(131,30),(229,84)],fill=(39,37,47))
d.rectangle((48,82,215,170),fill=(49,45,54))
d.rectangle((109,53,157,171),fill=(59,51,59))
for x in [67,94,174,196]:
    for y in [93,127]:
        d.rectangle((x,y,x+13,y+22),fill=(180,129,73),outline=(31,31,42),width=2)
        d.line((x+6,y,x+6,y+22),fill=(34,34,42),width=2)
d.rectangle((122,119,144,173),fill=(23,25,32),outline=(120,93,68),width=3)
for x in range(0,256,9):
    d.line((x,160,x+5,175),fill=(32,44,43))
im.resize((1024,700),Image.Resampling.NEAREST).save(BASE/'capa.png')
# Synthesized original audio (not copyrighted samples)
for name,notes in [('acerto',[(660,.12),(880,.2)]),('erro',[(190,.16),(130,.22)]),('porta',[(90,.22),(120,.20),(80,.25)])]:
    sr=22050; samples=[]
    for freq,dur in notes:
        n=int(sr*dur)
        for i in range(n):
            env=(1-i/n)**1.6
            s=int(9500*env*(math.sin(2*math.pi*freq*i/sr)+.2*math.sin(2*math.pi*freq*2*i/sr)))
            samples.append(max(-32768,min(32767,s)))
    with wave.open(str(BASE/(name+'.wav')),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes(struct.pack('<'+'h'*len(samples),*samples))
print('Assets generated:',[p.name for p in BASE.iterdir()])
