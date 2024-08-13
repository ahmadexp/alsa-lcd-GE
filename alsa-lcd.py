import sys
import time
import board
import numpy as np
import adafruit_ssd1306
import pprint as p
from alsa_midi import (
            SequencerClient,
            NoteOnEvent,
            NoteOffEvent
        )
from PIL import Image, ImageDraw, ImageFont

WIDTH = 64
HEIGHT = 48

def test_draw(oled, canvas, event, note, vel):
    #oled.fill(0)
    #oled.show()
    vel = int(vel/4)
    draw = ImageDraw.Draw(canvas)
    BORDER = 5
    draw.rectangle(
    (note-20, vel,
    note-18, 47),
        outline=0,
        fill=event,
    )

    #print(event, note, vel)
    #return draw

def bars(canvas, state, bar,  val):
    draw = ImageDraw.Draw(canvas)
    for i in range(0,7):
        if val[i] == 1:
            if state[i] < bar[i]:
                state[i] = state[i] + 1
                draw.line((i*8 ,state[i], (i*8)+6,state[i]), fill=255, width=1)

        else:
            if state[i] > 0:
                state[i] = state[i] - 1
                draw.line((i*8 , state[i], (i*8)+7,state[i]), fill=0, width=1)


def filter_events(event):
    if isinstance(event, NoteOnEvent) or isinstance(event, NoteOffEvent):
        event_type = str(type(event))
        note = event.note
        vel = event.velocity

        event_type = 0 if "Off" in event_type else 1

        #p.pprint(f"{event_type}, {note}, {vel}")

        return (event_type, note, vel)
    else:
        return None

def main():
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3D)

    oled.fill(0)
    oled.show()

    canvas = Image.new("1", (oled.width, oled.height))

    client = SequencerClient("client")
    port = client.create_port("inout")

    in_ports = client.list_ports(input=True)[0]
    p.pprint(in_ports)

    port.connect_from(in_ports)

    state = np.array([0,0,0,0,0,0,0,0])
    bar = np.array([0,0,0,0,0,0,0,0])
    val = np.array([1,1,1,1,1,1,1,1])
    note_max=1
    note_min=100
    vel_max=1
    vel_min=100
    while True:
        event = client.event_input()
        env = filter_events(event)
        if env is None:
            continue
        client.drop_input()
        e, n, v = env
        if n > note_max:
            note_max = n
        if n < note_min:
            note_min = n
        if v > vel_max:
            vel_max = v
        if v < vel_min:
            vel_min = v
        if(note_max > note_min):
            norm_n = ((n - note_min) * 8 ) / (note_max - note_min)
        else:
            norm_n=0
        if(vel_max > vel_min):
            norm_v = ((v - vel_min) * 48) / (vel_max - vel_min)
        else:
            norm_v=0
        if norm_n > 7:
            norm_n = 7
        if norm_n < 0:
            norm_n = 0
        index = int(norm_n)
        bar[index]=norm_v
        bar[index]=e
        #test_draw(oled, canvas, e, n, v)
        bars(canvas,state,bar,val)
        #draw = ImageDraw.Draw(canvas)
        #draw.line((0,0,10,10),fill=255, width=1)
        oled.image(canvas)
        oled.show()


if __name__ == "__main__":
    sys.exit(main())
