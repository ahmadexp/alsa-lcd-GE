import sys
import time
import board
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

    while True:
        event = client.event_input()
        env = filter_events(event)
        if env is None:
            continue
        client.drop_input()
        e, n, v = env
        test_draw(oled, canvas, e, n, v)
        oled.image(canvas)
        oled.show()


if __name__ == "__main__":
    sys.exit(main())
