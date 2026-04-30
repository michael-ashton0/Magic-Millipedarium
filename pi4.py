from gpiozero import LED, Button
import serial
from time import sleep

VOLUME                  = 20
NARRATION_BEFORE_UV 	= 41
TIME_UV_ON 		        = 30
TIME_IN_DARK 		    = 30

green_led = LED(23)
red_led = LED(24)
uv_light = LED(26)

button = Button(16, pull_up=True)

uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)


def send_dfplayer_command(command, param=0):
    packet = bytearray(10)
    packet[0] = 0x7E
    packet[1] = 0xFF
    packet[2] = 0x06
    packet[3] = command
    packet[4] = 0x00
    packet[5] = (param >> 8) & 0xFF
    packet[6] = param & 0xFF

    checksum = 0 - sum(packet[1:7])
    checksum &= 0xFFFF

    packet[7] = (checksum >> 8) & 0xFF
    packet[8] = checksum & 0xFF
    packet[9] = 0xEF

    uart.write(packet)
    sleep(0.2)


def dfplayer_reset():
    send_dfplayer_command(0x0C, 0)
    sleep(1)


def dfplayer_set_volume(volume):
    volume = max(0, min(30, volume))
    send_dfplayer_command(0x06, volume)


def dfplayer_play_track(track_number):
    send_dfplayer_command(0x03, track_number)


def dfplayer_stop():
    send_dfplayer_command(0x16, 0)


def dfplayer_loop_all():
    send_dfplayer_command(0x11, 0)


def dfplayer_loop_track(track_number):
    send_dfplayer_command(0x08, track_number)


# State helpers
def set_idle_state():
    green_led.on()
    red_led.off()
    uv_light.off()
    print("idle")


def set_narr_state():
    green_led.off()
    red_led.on()
    uv_light.off()
    print("narr")


def set_uv_state():
    green_led.off()
    red_led.off()
    uv_light.on()
    print("uv")


def set_dark_state():
    green_led.off()
    red_led.off()
    uv_light.off()
    print("dark")


def wait_for_button_press():
    while not button.is_pressed:
        sleep(0.01)


def wait_for_button_release():
    while button.is_pressed:
        sleep(0.01)


def main():
    dfplayer_reset()
    sleep(1)
    dfplayer_set_volume(VOLUME)
    sleep(1)

    while True:
        set_idle_state()

        dfplayer_play_track(1)
        sleep(1)
        dfplayer_loop_track(1)

        wait_for_button_press()
        sleep(0.03)

        if button.is_pressed:
            wait_for_button_release()

            set_narr_state()
            dfplayer_play_track(2)

            sleep(NARRATION_BEFORE_UV)
            set_uv_state()

            sleep(TIME_UV_ON)
            set_dark_state()

            sleep(TIME_IN_DARK)

            dfplayer_stop()
            sleep(1)

            dfplayer_reset()
            sleep(1)
            dfplayer_set_volume(VOLUME)
            sleep(1)


main()
