#!/usr/bin/env python3
"""Edit video Đức Thành: lật ngang, logo, chữ chìm, tiêu đề trượt vào, dòng hotline, cảnh kết.
Dùng: python3 edit_video.py SRC OUT --pill "XEM MÁY CHẠY THỰC TẾ" --line1 "MÁY CHIẾT RÓT" --line2 "DUNG DỊCH" [--phone "0989 139 855"] [--no-flip] [--mute] [--music nhac.mp3 --music-vol 0.8]  (--mute + --music = chỉ nhạc; chỉ --music = nhạc + tiếng gốc nhỏ)
"""
import argparse, os, subprocess, json, tempfile
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920
F='/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'; FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
HERE=os.path.dirname(os.path.abspath(__file__))
ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--pill',default='XEM MÁY CHẠY THỰC TẾ'); ap.add_argument('--line1',required=True); ap.add_argument('--line2',default='')
ap.add_argument('--phone',default='0989 139 855'); ap.add_argument('--no-flip',action='store_true'); ap.add_argument('--mute',action='store_true'); ap.add_argument('--music',default=''); ap.add_argument('--music-vol',type=float,default=0.8)
ap.add_argument('--end',type=float,default=2.7); ap.add_argument('--max',type=float,default=170.0,help='cắt tối đa (giây)')
a=ap.parse_args()
tmp=tempfile.mkdtemp()
logo=Image.open(os.path.join(HERE,'logo-duc-thanh.png')).convert('RGBA')
def badge(s):
    l=logo.resize((s,s),Image.LANCZOS); b=Image.new('RGBA',(s+24,s+24),(0,0,0,0))
    m=Image.new('L',b.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,b.size[0]-1,b.size[1]-1],radius=28,fill=235)
    b.paste(Image.new('RGBA',b.size,(255,255,255,255)),(0,0),m); b.alpha_composite(l,(12,12)); return b
def ct(d,y,t,f,fill,st=3):
    w=d.textlength(t,font=f); d.text(((W-w)/2,y),t,font=f,fill=fill,stroke_width=st,stroke_fill=(0,40,90,255))
fnt=lambda p,s: ImageFont.truetype(p,s)
# chữ chìm
wm=Image.new('RGBA',(W*2,H*2),(0,0,0,0)); d=ImageDraw.Draw(wm)
for y in range(0,H*2,330):
    for x in range(-200 if (y//330)%2 else 100,W*2,620): d.text((x,y),'ĐỨC THÀNH',font=fnt(F,64),fill=(255,255,255,34))
wm.rotate(28,resample=Image.BICUBIC).crop((W//2,H//2,W//2+W,H//2+H)).save(f'{tmp}/wm.png')
# lớp cố định: dải màu, logo, hotline (tránh vùng UI của TikTok/Reels)
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(560): d.line([(0,y),(W,y)],fill=(5,30,70,int(170*(1-y/560))))
for y in range(1300,1620):
    al=int(190*min(1,(y-1300)/120)) if y<1420 else int(190*max(0,1-(y-1520)/100)) if y>1520 else 190
    d.line([(0,y),(W,y)],fill=(5,30,70,al))
ov.alpha_composite(badge(140),(W-204,170))
ct(d,1395,'Tư vấn – báo giá: '+a.phone,fnt(F,52),(255,255,255,255)); ct(d,1470,'mayducthanh.vn',fnt(FB,42),(255,214,0,255))
ov.save(f'{tmp}/ov.png')
# tiêu đề
t=Image.new('RGBA',(W,540),(0,0,0,0)); d=ImageDraw.Draw(t); f1=fnt(F,44)
if a.pill:
    w1=d.textlength(a.pill,font=f1); d.rounded_rectangle([60,180,60+w1+48,256],radius=38,fill=(255,204,0,255)); d.text((84,192),a.pill,font=f1,fill=(10,40,90,255))
f2=fnt(F,84 if max(len(a.line1),len(a.line2))<=16 else 64)
d.text((60,280),a.line1,font=f2,fill=(255,255,255,255),stroke_width=5,stroke_fill=(0,40,90,255))
if a.line2: d.text((60,378),a.line2,font=f2,fill=(255,214,0,255),stroke_width=5,stroke_fill=(0,40,90,255))
t.save(f'{tmp}/title.png')
# cảnh kết
e=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(e)
for y in range(H): d.line([(0,y),(W,y)],fill=(8+int(10*y/H),52+int(30*y/H),120+int(50*y/H),255))
bl=badge(380); e.alpha_composite(bl,((W-bl.size[0])//2,330))
ct(d,820,'MÁY ĐÓNG GÓI – CHIẾT RÓT',fnt(F,62),(255,255,255,255),0); ct(d,900,'ĐỨC THÀNH',fnt(F,96),(255,214,0,255),0)
ct(d,1060,'Tư vấn – lắp đặt – bảo hành tận nơi',fnt(FB,46),(220,235,255,255),0)
d.rounded_rectangle([140,1190,W-140,1330],radius=70,fill=(255,204,0,255))
fp=fnt(F,84); w=d.textlength(a.phone,font=fp); d.text(((W-w)/2,1215),a.phone,font=fp,fill=(10,40,90,255))
ct(d,1360,'Hotline / Zalo',fnt(FB,42),(255,255,255,255),0); ct(d,1470,'mayducthanh.vn',fnt(F,58),(255,255,255,255),0)
e.convert('RGB').save(f'{tmp}/end.png')
# thông tin nguồn
pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type','-of','json',a.src]))
D=min(float(pr['format']['duration']),a.max); E=a.end; T=D+E
has_a=any(s['codec_type']=='audio' for s in pr['streams']) and not a.mute
flip='hflip,' if not a.no_flip else ''
fc=(f"[0:v]{flip}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
    f"scale=w='trunc(1080*(1+0.05*t/{D})/2)*2':h='trunc(1920*(1+0.05*t/{D})/2)*2':eval=frame,crop=1080:1920,eq=contrast=1.06:saturation=1.15[v0];"
    "[v0][1:v]overlay=0:0[v1];[v1][2:v]overlay=0:0[v2];"
    "[3:v]format=rgba,fade=in:st=0.15:d=0.4:alpha=1[ti];[v2][ti]overlay=x='-200+200*min(1,(t-0.15)/0.4)':y=0:enable='gte(t,0.15)'[v3];"
    f"[v3]format=yuv420p,trim=duration={D},setpts=PTS-STARTPTS[main];"
    "[4:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p,fade=in:st=0:d=0.4[end];[main][end]concat=n=2:v=1:a=0[vout];")
if a.music:
    mi=5  # chỉ số input nhạc (sau 5 input: video + 4 ảnh)
    mus=f"[{mi}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={T},volume={a.music_vol},afade=in:d=0.5,afade=out:st={max(0,T-1.5)}:d=1.5[mus];"
    if has_a: fc+=mus+f"[0:a]atrim=duration={D},aresample=48000,aformat=channel_layouts=stereo,volume=0.35,apad=whole_dur={T}[orig];[orig][mus]amix=inputs=2:duration=longest:normalize=0[aout]"
    else: fc+=mus.replace('[mus];','[aout]')
else:
    fc+= (f"[0:a]atrim=duration={D},aresample=48000,afade=out:st={max(0,D-0.7)}:d=0.7,apad=whole_dur={T}[aout]" if has_a
      else f"anullsrc=r=48000:cl=stereo,atrim=duration={T}[aout]")
cmd=['ffmpeg','-loglevel','error','-y','-i',a.src]
for p,dur in (('wm',D),('ov',D),('title',D),('end',E)): cmd+=['-loop','1','-t',str(dur),'-i',f'{tmp}/{p}.png']
if a.music: cmd+=['-stream_loop','-1','-i',a.music]
cmd+=['-filter_complex',fc,'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
      '-c:a','aac','-b:a','160k','-movflags','+faststart','-t',str(T),a.out]
subprocess.check_call(cmd); print('OK',a.out,round(T,2),'s')
