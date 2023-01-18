import time
import board
import digitalio
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import displayio
import adafruit_displayio_ssd1306
import adafruit_ssd1306
import busio

#hardware/output setup begin
displayio.release_displays()

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)

display_bus = displayio.I2CDisplay(i2c, device_address = 0x3C)
display_text = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
display.fill(0)
display.show()

keyPins = [board.GP20, board.GP21, board.GP10, board.GP11]
buttonPins = [board.GP28, board.GP2]
ledPin = board.GP27
numLeds = 4

cc = ConsumerControl(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

keys = [digitalio.DigitalInOut(pin) for pin in keyPins]                                                                                                            
keys.append(digitalio.DigitalInOut(buttonPins[0]))
#executive decision to make the left button in the key list bc it makes more sense hopefully
button = digitalio.DigitalInOut(buttonPins[1])

for key in keys:
    key.direction = digitalio.Direction.INPUT
    key.pull = digitalio.Pull.UP
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

pixels = neopixel.NeoPixel(ledPin, numLeds, brightness=1, auto_write=False)
cool_colors = [(255,0,0), (255,255,255)]
for i in range(numLeds):
    pixels[i] = cool_colors[1]

pixels.show()

#setup end

led_should_be_on = True
led_off = False
brightness = 1

#updates is list of 2 index tuple (int index, bool state) passed to most functions

def basic_on_off(updates, colors):
    for update in updates:
        i = update[0] #index
        if i != 4:
            if update[1]: #if pressed
                pixels[i] = colors[0]
            else: #if released
                pixels[i] = colors[1]

def single_color(updates, color):
    basic_on_off(updates, [color, (0,0,0)])

def color(updates) -> None:
    
    if led_should_be_on:
        pixels.fill((1,0,1))
        pass
    elif not led_off:
        pixels.fill((0,0,0))
        led_off = True
    return

def basic_profile(actions, updates):
    for update in updates:
        action = actions[update[0]]
        if isinstance(action, int):
            if update[1]:
                keyboard.press(action)
            else:
                keyboard.release(action)
        elif isinstance(action, list):
            if update[1]:
                keyboard.press(*action)
            else:
                keyboard.release(*action)
        elif isinstance(action, str):
                if update[1]:
                    layout.write(action)

def menu(updates) -> None:
    actions = [Keycode.SHIFT, Keycode.F2, Keycode.ESCAPE, Keycode.ENTER, 'mode=m keys=4']
    basic_profile(actions, updates)
    
def osu(updates) -> None:
    actions = [Keycode.S, Keycode.D, [Keycode.F, Keycode.SHIFT], Keycode.TAB, Keycode.SPACE]
    basic_profile(actions, updates)

def mania(updates) -> None:
    actions = [Keycode.D, Keycode.F, Keycode.J, Keycode.K, Keycode.GRAVE_ACCENT]
    basic_profile(actions, updates)

def multimedia(updates) -> None:
    actions = [ConsumerControlCode.SCAN_PREVIOUS_TRACK, ConsumerControlCode.SCAN_NEXT_TRACK, ConsumerControlCode.PLAY_PAUSE, Keycode.PAUSE, [Keycode.CONTROL, Keycode.SHIFT, Keycode.ALT, Keycode.M]]
    #didnt want to include the consumer code stuff in basic_profile because both those and keycodes are just ints and i didnt know how to differentiate them well
    for update in updates:
        action = actions[update[0]]
        if update[0] != 3 and update[0] != 4:
            if update[1]:
                cc.send(action)
        elif isinstance(action, int):
            if update[1]:
                keyboard.press(action)
            else:
                keyboard.release(action)
        elif isinstance(action, list):
            if update[1]:
                keyboard.press(*action)
            else:
                keyboard.release(*action)

FAKE_MODES = 1 #modes that shouldnt be toggleable and should go at the end of the list
modes = [(osu, 'osu!'), (mania, 'osu!Mania'), (multimedia, 'Multimedia'), (menu, 'Song Browser')]
mode = 0
realMode = mode #mode index ignoring if youre on song browser
print(modes[mode][1])

keyStates = [0 for _ in range(len(keys))]
lastKeyStates = list(keyStates)
buttonState = 0
lastButtonState = buttonState
rgb_updated = False

buttonPressed = False
modeToggled = False

while True:
    #find current button states
    for i in range(len(keys)):
        keyStates[i] = not keys[i].value
    buttonState = not button.value

    if buttonState != lastButtonState:
        if buttonState:
            buttonPressed = True
        else:
            buttonPressed = False
            if not modeToggled:
                if mode != -1:
                    mode = -1
                else:
                    mode = realMode
                print()
                print(modes[mode][1])
            modeToggled = False  
                
    #updates is list of 2 index tuple (int index, bool state) passed to most functions
    updates=[]

    for i in range(len(keys)):
        if keyStates[i] != lastKeyStates[i]:
            rgb_updated = True
            if keyStates[i]:
                updates.append((i, True))
            else:
                updates.append((i, False))
    
    if buttonPressed:
        if keyStates[-1] != lastKeyStates[-1] and keyStates[-1]:
            mode = (mode+1)%(len(modes) - FAKE_MODES)
            realMode = mode
            print()
            print(modes[mode][1])
            updates.pop(-1)
            modeToggled = True

    basic_on_off(updates, cool_colors)
    #single_color(updates, (255,0,100))
    modes[mode][0](updates)

    lastKeyStates = list(keyStates)
    lastButtonState = buttonState

    if rgb_updated: pixels.show()
    time.sleep(.01)