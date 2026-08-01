from machine import Pin, SoftI2C
import ssd1306
import time

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

BTN_SUBH = Pin(18, Pin.IN, Pin.PULL_UP)
BTN_HAMD = Pin(19, Pin.IN, Pin.PULL_UP)
BTN_AKBAR = Pin(23, Pin.IN, Pin.PULL_UP)

LED = Pin(2, Pin.OUT)
LED.value(0)

counts = {"subh": 0, "hamd": 0, "akbar": 0}
last_state = {"subh": 1, "hamd": 1, "akbar": 1}

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
    time.sleep(0.75)
    update_screen()

def check_finished():
    if counts["subh"] >= 33 and counts["hamd"] >= 33 and counts["akbar"] >= 34:
        LED.value(1)

update_screen()
print("Tasbih started")

while True:
    c_subh = BTN_SUBH.value()
    c_hamd = BTN_HAMD.value()
    c_akbar = BTN_AKBAR.value()

    if c_subh == 0 and c_akbar == 0:
        reset_tasbih()
        last_state["subh"] = 1
        last_state["akbar"] = 1
        time.sleep(0.5) 
        continue

    display_needs_update = False

    if c_subh == 0 and last_state["subh"] == 1:
        counts["subh"] += 1
        print(f"subhanallah: {counts['subh']}")
        display_needs_update = True

    if c_hamd == 0 and last_state["hamd"] == 1:
        counts["hamd"] += 1
        print(f"alhamdulilah: {counts['hamd']}")
        display_needs_update = True

    if c_akbar == 0 and last_state["akbar"] == 1:
        counts["akbar"] += 1
        print(f"allahu akbar: {counts['akbar']}")
        display_needs_update = True

    if display_needs_update:
        update_screen()
        check_finished()

    last_state["subh"] = c_subh
    last_state["hamd"] = c_hamd
    last_state["akbar"] = c_akbar

    time.sleep(0.05)
