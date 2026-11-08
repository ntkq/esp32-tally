from machine import Pin, SoftI2C
import ssd1306
import time
import gc
import network
import urequests
import micropython
from secrets import WIFI_CREDS, URL

i2c = SoftI2C(scl=Pin(23), sda=Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# rotate display 180
oled.write_cmd(0xA0)
oled.write_cmd(0xC0)

BTN_SUBH = Pin(18, Pin.IN, Pin.PULL_UP)  # white
BTN_HAMD = Pin(19, Pin.IN, Pin.PULL_UP)  # blue
BTN_AKBAR = Pin(21, Pin.IN, Pin.PULL_UP)  # red

LED = Pin(2, Pin.OUT)
LED.value(0)

last_irq = {"subh": 0, "hamd": 0, "akbar": 0}
DEBOUNCE = 50

counts = {"subh": 0, "hamd": 0, "akbar": 0}
completion = {"complete": False}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def update_screen(message=None):
    oled.fill(0)
    if message:
        oled.text(message, 0, 20)
    else:
        oled.text(f"subhanallah: {counts['subh']}", 0, 0)
        oled.text(f"alhamdulilah: {counts['hamd']}", 0, 20)
        oled.text(f"allahu akbar: {counts['akbar']}", 0, 40)
    oled.show()


def reset_tasbih():
    print("Resetting counters...")
    counts["subh"] = 0
    counts["hamd"] = 0
    counts["akbar"] = 0
    LED.value(0)

    update_screen("resetting...")
    time.sleep(0.5)
    update_screen()


def check_finished():
    if counts["subh"] >= 33 and counts["hamd"] >= 33 and counts["akbar"] >= 33:
        completion["complete"] = True
        LED.value(1)
        api_send()
        counts["subh"] = 0
        counts["hamd"] = 0
        counts["akbar"] = 0
        completion["complete"] = False
        update_screen()
        time.sleep(0.5)
        LED.value(0)


def api_send():
    print("going to send to api")
    update_screen("uploading")
    payload = {"complete": completion["complete"]}
    if wlan.isconnected():
        response = None
        try:
            response = urequests.post(URL, json=payload, timeout=5)
            print(f"uploaded data -> {response.status_code}")
            update_screen("uploaded")
        except Exception as ex:
            print("api upload error:", ex)
            update_screen("cant upload")
        finally:
            if response:
                response.close()
            gc.collect()
            time.sleep(1)
            update_screen()
    else:
        print("tried api send but disconnected")
        update_screen("not connected")
        time.sleep(1)
        update_screen()


def press(button):
    now = time.ticks_ms()
    if button == BTN_SUBH:
        btn_irq = "subh"
    elif button == BTN_HAMD:
        btn_irq = "hamd"
    else:
        btn_irq = "akbar"

    if time.ticks_diff(now, last_irq[btn_irq]) < DEBOUNCE:
        return
    last_irq[btn_irq] = now
    micropython.schedule(on_press, button)


def on_press(button):
    subh_state = BTN_SUBH.value()
    hamd_state = BTN_HAMD.value()
    akbar_state = BTN_AKBAR.value()

    if subh_state == 0:
        if hamd_state == 0:
            api_send()
        elif akbar_state == 0:
            reset_tasbih()
        else:
            counts["subh"] += 1
            print("subh:", counts["subh"])
            update_screen()

    elif hamd_state == 0:
        counts["hamd"] += 1
        print("hamd:", counts["hamd"])
        update_screen()

    elif akbar_state == 0:
        counts["akbar"] += 1
        print("akbar:", counts["akbar"])
        update_screen()

    check_finished()


def main():
    BTN_SUBH.irq(trigger=Pin.IRQ_FALLING, handler=press)
    BTN_HAMD.irq(trigger=Pin.IRQ_FALLING, handler=press)
    BTN_AKBAR.irq(trigger=Pin.IRQ_FALLING, handler=press)


wlan.connect(WIFI_CREDS[0], WIFI_CREDS[1])
wifi_timeout = 10
while not wlan.isconnected() and wifi_timeout > 0:
    time.sleep(1)
    wifi_timeout -= 1

if wlan.isconnected():
    print("wifi connected")
    update_screen("connected")
    time.sleep(1)
else:
    print("wifi failed")
    update_screen("wifi failed")
    time.sleep(1)

try:
    update_screen()
    print("Tasbih started")
    main()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("cancelled")
    oled.fill(0)
    oled.show()
