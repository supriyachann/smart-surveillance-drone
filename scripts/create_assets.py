"""Optional authoring helper. Needs Pillow, reportlab, PyMuPDF and FFmpeg."""
import subprocess
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
TMP = ROOT / 'artifacts'
for p in [OUT/'pdf', OUT/'video', TMP]:
    p.mkdir(parents=True,exist_ok=True)
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
if not Path(FONT).exists():
    FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font = lambda size: ImageFont.truetype(FONT,size)


def scene(t=0):
    im=Image.new('RGB',(1280,720),'#edf2ed'); d=ImageDraw.Draw(im)
    for x in range(0,1280,60): d.line((x,0,x,720), fill='#d6e2da')
    for y in range(0,720,60): d.line((0,y,1280,y), fill='#d6e2da')
    d.line((-50,550,1330,210),fill='#c4d4cb',width=125)
    for box,name in [((90,145,350,300),'Building A'),((820,425,1160,620),'Building B')]:
        d.rectangle(box,fill='#d4e1d9',outline='#749888',width=3)
        d.text((box[0]+25,box[1]+55),name,font=font(24),fill='#31584a')
    x=440+int(t*12)
    d.ellipse((x+10,280,x+35,305),fill='#57776c')
    d.line((x+22,307,x+22,355),fill='#57776c',width=12)
    d.line((x+22,350,x+3,385),fill='#57776c',width=8)
    d.line((x+22,350,x+40,385),fill='#57776c',width=8)
    d.rectangle((x-10,265,x+55,400),outline='#156a53',width=3)
    d.text((x-10,235),'Synthetic person',font=font(18),fill='#156a53')
    d.rounded_rectangle((760,235,920,315),radius=15,fill='#628493')
    d.rectangle((745,220,935,330),outline='#156a53',width=3)
    d.text((745,185),'Synthetic vehicle',font=font(18),fill='#156a53')
    d.rectangle((0,0,1280,90),fill='#173e34')
    d.text((30,19),'Synthetic monitoring scene',font=font(32),fill='white')
    d.rectangle((0,655,1280,720),fill='#fff1cc')
    d.text((30,673),'Illustration only - no real footage, AI predictions or aircraft telemetry',font=font(23),fill='#644e1d')
    return im

scene().save(ROOT/'data/synthetic-scene.png')
process=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate','15','-i','-','-an','-c:v','libx264','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'data/synthetic-scene.mp4')],stdin=subprocess.PIPE)
for frame in range(150): process.stdin.write(scene(frame/15).tobytes())
process.stdin.close()
if process.wait(): raise RuntimeError('Sample clip encoding failed')

pdf=OUT/'pdf/design-document.pdf'
c=canvas.Canvas(str(pdf),pagesize=(900,650))
c.setTitle('Smart Surveillance Drone - Software and integration design')
c.setAuthor('Smart Surveillance Drone contributors')

def text(x,y,value,size=14,color='#26483d'):
    c.setFillColor(HexColor(color)); c.setFont('Helvetica',size); c.drawString(x,y,value)

def page(title,subtitle,num):
    c.setFillColor(HexColor('#f7f9f6')); c.rect(0,0,900,650,fill=1,stroke=0)
    text(40,601,'Smart Surveillance Drone',15)
    text(40,546,title,30)
    text(40,514,subtitle,13,'#536b61')
    c.setStrokeColor(HexColor('#cddbd4'));c.line(40,490,860,490)
    text(40,25,'Software prototype | Hardware integration pending | No flight claims',10)
    text(835,25,str(num),10)

def lines(x,y,value,width=96,size=14,gap=24):
    for line in textwrap.wrap(value,width):
        text(x,y,line,size); y-=gap
    return y

def box(x,y,w,h,title,detail):
    c.setFillColor(HexColor('#e6efe9'));c.setStrokeColor(HexColor('#99b4a5'));c.roundRect(x,y,w,h,8,fill=1,stroke=1)
    text(x+15,y+h-27,title,15)
    lines(x+15,y+h-50,detail,max(18,int(w/7.5)),11,17)

def arrow(x1,y1,x2,y2):
    c.setStrokeColor(HexColor('#176a55'));c.setLineWidth(2);c.line(x1,y1,x2,y2)
    p=c.beginPath();p.moveTo(x2,y2);p.lineTo(x2-8,y2+5);p.lineTo(x2-8,y2-5);p.close()
    c.setFillColor(HexColor('#176a55'));c.drawPath(p,fill=1,stroke=0)

page('A monitoring desk for human review','Current software scope and honest evaluation boundaries',1)
y=lines(40,451,'The prototype lets an operator inspect person and vehicle events, mark alerts reviewed, filter the queue and export a session. A local Python service accepts validated events from an optional YOLO adapter.',93)
y-=20
box(40,260,390,100,'Implemented software','Offline sample session, local HTTP service, event review and JSON export.')
box(465,260,395,100,'Optional inference path','Local video/webcam adapter. Requires packages and trusted weights; actual inference not yet run.')
lines(40,220,'Aircraft control, GPS missions, MQTT and browser video streaming are proposed future integration. No aircraft was connected. Synthetic sample imagery is illustrative and must never be used as detection evidence.',94)
text(40,102,'Validation: 13 Python tests and the offline UI workflow harness pass.',15)
text(40,75,'Live networking and rendered browser QA were blocked by the build sandbox.',13)
c.showPage()
page('Software architecture','Implemented local event path; aircraft system remains independent',2)
box(40,342,220,105,'Input source','Synthetic fixtures OR authorized local video / webcam')
box(335,342,225,105,'Event service','Validate schema, deduplicate IDs, retain up to 200 events')
box(635,342,225,105,'Monitoring desk','Inspect, filter, mark reviewed and export JSON')
arrow(265,395,325,395);arrow(565,395,625,395)
text(42,310,'Real video passes through the optional YOLO adapter before event ingestion.',13)
box(40,135,390,115,'Proposed aircraft layer','Pixhawk: stabilization and configured failsafes. Raspberry Pi: companion processing. Hardware unverified.')
box(465,135,395,115,'Separation of responsibilities','No flight-control endpoint exists in the prototype. Detections require human review; no automatic pursuit.')
text(40,85,'Actual interface: loopback HTTP JSON. MQTT and remote video are not implemented.',13)
c.showPage()
page('Detection and event flow','Validation, bounded storage and review states',3)
steps=[('1. Read an authorized frame','Optional YOLO adapter; timestamp is frame-read time.'),('2. Filter supported classes','Confidence threshold and per-class cooldown.'),('3. Validate the JSON event','Types, UTC time, confidence, normalized box and source ID.'),('4. Deduplicate and retain','Latest 200 events in memory; reset on server restart.'),('5. Review and export','Operator inspects the event and marks it reviewed.')]
y=420
for title,detail in steps:
    box(40,y-38,820,65,title,detail); y-=82
c.showPage()
page('Dashboard wireframe','Illustrative inspection scene with a separate review queue',4)
c.drawImage(str(ROOT/'data/synthetic-scene.png'),40,180,width=535,height=301)
box(595,300,265,180,'Review queue','Person: synthetic sample. Inspect its normalized box. Mark reviewed. Filter pending events. Export JSON.')
box(595,180,265,100,'Flight telemetry','Not connected. Battery and GPS unavailable.')
lines(40,135,'The browser scene is an illustration. Original camera frames appear only in the optional OpenCV preview window. The UI must not imply that the illustration is a live video stream.',100,13,21)
c.showPage();c.save()
# Render every final page for inspection.
doc=fitz.open(pdf)
for index,p in enumerate(doc):
    p.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(TMP/f'design-page-{index+1}.png')
print(f'Created {pdf.name}: {len(doc)} pages; synthetic image/video generated.')
