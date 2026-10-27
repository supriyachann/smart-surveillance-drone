"""Create a captioned design/software walkthrough, not a live flight recording.
Requires Pillow and FFmpeg. No real footage, voices or model outputs are used.
"""
import subprocess
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'artifacts'; TMP.mkdir(exist_ok=True)
OUT=ROOT/'output/video'; OUT.mkdir(parents=True,exist_ok=True)
font_path=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
if not font_path.exists(): font_path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
f=lambda n:ImageFont.truetype(str(font_path),n)
slides=[
('Why mobile monitoring?', 'Large sites can leave gaps between fixed cameras and manual patrols. This project explores how aerial sensing could support authorized operators. The current deliverable is a local software prototype and a proposed aircraft integration design. No drone has been connected or flown.', ['Coverage gaps','Human review','Authorized monitoring']),
('Separate flight and observation', 'The proposed Pixhawk controls stabilization and configured flight failsafes. A Raspberry Pi would process camera frames. These hardware choices still require validation. The implemented software does not send aircraft commands or automatically pursue people or vehicles.', ['Pixhawk: proposed flight layer','Raspberry Pi: proposed companion','Operator retains control']),
('The implemented software path', 'An optional YOLO adapter reads a local video or webcam and converts supported detections to JSON events. The Python service validates them and keeps the latest 200 in memory. The dashboard polls the service. Actual model inference requires optional packages and trusted local weights and has not been run in the build environment.', ['Video / webcam adapter','Validated local event service','Browser review queue']),
('Try the sample session', 'Open static/index.html directly in a browser. No server or internet connection is needed for the offline preview. Select Load sample events. The queue contains two synthetic events: a person and a car. These fixtures exercise the interface; they are not AI predictions or evidence of detection accuracy.', ['Load sample events','Synthetic person event','Synthetic car event']),
('Inspect an event', 'Choose Inspect beside an event. The dashboard displays its class, confidence, timestamp and source alias. Its normalized bounding box is projected onto an illustration. This is not the original camera frame. With a real detector, annotated camera frames appear separately in the optional OpenCV preview window.', ['Inspect the event','Read class and confidence','Check source and capture time']),
('Review the queue', 'Choose Mark reviewed after inspecting an event. Select Needs review to see pending items. Re-loading the sample session skips duplicate IDs. The detector uses a per-class cooldown, so this prototype is not object tracking. A person or vehicle label is a cue for review and does not establish intent or danger.', ['Mark reviewed','Filter pending events','Keep a human in the loop']),
('Export and validate', 'Select Export events to download a JSON session with review state and synthetic labels. Offline events reset on page reload. Server events reset on process restart. Thirteen Python tests and a minimal-DOM workflow check passed. Live-server testing and rendered browser QA were blocked by the build environment and remain to be run on a normal host.', ['Export JSON','Preserve synthetic labels','Record real validation evidence']),
('Next: measured field validation', 'Install the optional detector packages and supply trusted weights. Evaluate on authorized, labeled footage; measure precision, recall, false alerts and latency. Validate flight integration in a simulator before controlled hardware tests. Record an actual demonstration for any live-demo requirement. The college declaration needs the real required signatures and stamp.', ['Test actual inference','Validate flight separately','Complete institutional declaration']),
]
scene=Image.open(ROOT/'data/synthetic-scene.png').resize((580,326))
for i,(title,body,steps) in enumerate(slides):
    im=Image.new('RGB',(1280,720),'#f7f9f6'); d=ImageDraw.Draw(im)
    d.rectangle((0,0,1280,72),fill='#173e34')
    d.text((32,21),'Smart Surveillance Drone',font=f(25),fill='white')
    d.text((1110,23),f'{i+1} / 8',font=f(23),fill='white')
    d.text((32,100),title,font=f(36),fill='#173e34')
    y=173
    for line in textwrap.wrap(body,44):
        d.text((32,y),line,font=f(23),fill='#31584a');y+=32
    im.paste(scene,(668,175))
    y=525
    for step in steps:
        d.text((680,y),'• '+step,font=f(22),fill='#31584a');y+=35
    d.rectangle((0,665,1280,720),fill='#fff1cc')
    d.text((32,680),'Captioned software/design walkthrough - synthetic illustration, not a live flight demo',font=f(21),fill='#644e1d')
    im.save(TMP/f'walkthrough-{i:02}.png')
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','1/30','-i',str(TMP/'walkthrough-%02d.png'),'-vf','fps=12,format=yuv420p','-t','240','-c:v','libx264','-preset','fast','-crf','24','-movflags','+faststart',str(OUT/'project-walkthrough.mp4')],check=True)
print('Created 4-minute 1280x720 captioned walkthrough (no audio; no real flight recording).')
