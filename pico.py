from machine import Pin, UART
import time

VOLUME = 20
NARRATION_TIME_BEFORE_UV = 41
TIME_UV_ON = 30
TIME_IN_DARK = 30

# Pin setup, GP14, GP15, GP16
green_led = Pin(14, Pin.OUT)
red_led = Pin(15, Pin.OUT)
uv_light = Pin(17, Pin.OUT)

button = Pin(16, Pin.IN, Pin.PULL_UP)

# GP0, GP1
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# DFPlayer commands (allegedly)

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
    time.sleep_ms(200)

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
    time.sleep_ms(1000)

def dfplayer_loop():
    send_dfplayer_command(0x19)

# State helpers
def set_idle_state():
    green_led.value(1)
    red_led.value(0)
    uv_light.value(0)

def set_narr_state():
    green_led.value(0)
    red_led.value(1)
    uv_light.value(0)

def set_uv_state():
    green_led.value(0)
    red_led.value(0)
    uv_light.value(1)

def set_dark_state():
    green_led.value(0)
    red_led.value(0)
    uv_light.value(0)

def wait_for_button_press():
    while button.value() == 1:
        time.sleep_ms(10)

def wait_for_button_release():
    while button.value() == 0:
        time.sleep_ms(10)


def main():
    dfplayer_reset()
    dfplayer_set_volume(VOLUME)

    while True:
        set_idle_state()
        
        dfplayer_play_track(1)
        dfplayer_loop()

        wait_for_button_press()
        time.sleep_ms(30)

        if button.value() == 0:
            wait_for_button_release()
            
            set_narr_state()
            dfplayer_play_track(2)
            time.sleep(NARRATION_TIME_BEFORE_UV)
            
            set_uv_state()
            time.sleep(TIME_UV_ON)
            
            set_dark_state()
            time.sleep(TIME_IN_DARK)
            
            dfplayer_stop()
            time.sleep_ms(200)

            dfplayer_reset()

main()