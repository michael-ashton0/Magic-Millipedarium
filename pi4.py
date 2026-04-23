from gpiozero import LED, Button
import serial
from time import sleep

VOLUME = 20
NARRATION_TIME_BEFORE_UV = 41
TIME_UV_ON = 30
TIME_IN_DARK = 30

green_led = LED(16)
red_led = LED(18)
uv_light = LED(22)

button = Button(36, pull_up=True)

uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

def send_dfplayer_command(command, param=0):
    """
    Send a 10-byte DFPlayer command packet.
    """
    packet = bytearray(10)
    packet[0] = 0x7E
    packet[1] = 0xFF
    packet[2] = 0x06
    packet[3] = command
    packet[4] = 0x00  # no feedback
    packet[5] = (param >> 8) & 0xFF
    packet[6] = param & 0xFF

    checksum = 0 - (packet[1] + packet[2] + packet[3] + packet[4] + packet[5] + packet[6])
    checksum &= 0xFFFF

    packet[7] = (checksum >> 8) & 0xFF
    packet[8] = checksum & 0xFF
    packet[9] = 0xEF

    uart.write(packet)
    sleep(0.2)

def dfplayer_set_volume(volume):
    """
    Volume range usually 0-30.
    """
    volume = max(0, min(30, volume))
    send_dfplayer_command(0x06, volume)

def dfplayer_play_track(track_number):
    """
    Play track by number, e.g. 1 -> 0001.mp3
    """
    send_dfplayer_command(0x03, track_number)

def dfplayer_stop():
    send_dfplayer_command(0x16, 0)

def dfplayer_reset():
    send_dfplayer_command(0x0C, 0)
    sleep(1)

def dfplayer_loop():
    send_dfplayer_command(0x19)

# State helpers
def set_idle_state():
    green_led.on()
    red_led.off()
    uv_light.off()

def set_narr_state():
    green_led.off()
    red_led.on()
    uv_light.off()

def set_uv_state():
    green_led.off()
    red_led.off()
    uv_light.on()

def set_dark_state():
    green_led.off()
    red_led.off()
    uv_light.off()

def wait_for_button_press():
    while not button.is_pressed:
        sleep(0.01)

def wait_for_button_release():
    while button.is_pressed:
        sleep(0.01)


def main():
    dfplayer_reset()
    dfplayer_set_volume(VOLUME)

    while True:
        set_idle_state()
        
        dfplayer_play_track(1)
        dfplayer_loop()

        wait_for_button_press()
        sleep(0.03)

        if button.is_pressed:
            wait_for_button_release()
            set_narr_state()
            dfplayer_play_track(2)
            
            sleep(NARRATION_TIME_BEFORE_UV)
            
            set_uv_state()
            sleep(TIME_UV_ON)
            
            set_dark_state()
            sleep(TIME_IN_DARK)
            
            dfplayer_stop()
            sleep(0.2)

            dfplayer_reset()

main()