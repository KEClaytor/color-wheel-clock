# 12-Pixel, 3-Button "Clock"
# 2019-01-01 - Kevin Claytor

import time
import board
import neopixel
import analogio
import digitalio

# One pixel connected internally!
# dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# Soft-pot pin
TOUCH_MIN_V = 1.8
TOUCH_MAX_V = 3.2
analogin = analogio.AnalogIn(board.A3)

# Red Button
button_r = digitalio.DigitalInOut(board.D2)
button_r.switch_to_input(pull=digitalio.Pull.UP)
# White Button
button_w = digitalio.DigitalInOut(board.D1)
button_w.switch_to_input(pull=digitalio.Pull.UP)
# Green Button
button_g = digitalio.DigitalInOut(board.D0)
button_g.switch_to_input(pull=digitalio.Pull.UP)

# Pixel colors
OFF = (0, 0, 0)

PINK = (241, 0, 249)
PURPLE = (113, 5, 255)
YELLOW = (255, 150, 0)

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

RED = (255, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (214, 111, 2)

CYAN = (0, 255, 255)

# NeoPixel strip (of 16 LEDs) connected on D4
NUMPIXELS = 12
BRIGHTNESS = 0.2
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(board.D4, NUMPIXELS, brightness=BRIGHTNESS, auto_write=False)
# Initalize pixels OFF
for i in range(NUMPIXELS):
    pixels[i] = OFF
pixels.show()


def wheel(pos):
    """ Color wheel from 0-255.

    Input a value 0 to 255 to get a color value.
    The colours are a transition r - g - b - back to r.
    """
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)

    if ORDER == neopixel.RGB:
        color = (r, g, b)
    elif ORDER == neopixel.GRB:
        color = (g, r, b)
    else:
        color = (r, g, b, 0)

    return color


def rgb_to_grb(color_tuple):
    """ Convert RGB tuple to GRB tuple.
    """
    r, g, b = color_tuple
    return (g, r, b)


def getVoltage(pin):
    """ Return voltage on an analog pin.
    """
    return (pin.value * 3.3) / 65536


def translate(value, leftMin, leftMax, rightMin, rightMax):
    """ Map value from [leftMin, leftMax] to [rightMin, rightMax].
    """
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def get_button_state():
    """ Read and return a tuple of which buttons are pressed.

    returns:
        (Red Pressed, White Pressed, Green Pressed)
    """
    buttons = [button_r, button_w, button_g]
    state = tuple(not b.value for b in buttons)
    return state


def set_three_colors(CA, CB, CC, offset=0):
    """ Set NeoPixel ring to three colors.
    """
    color_pattern = [CA]*4 + [CB]*4 + [CC]*4
    for ii, c in enumerate(color_pattern):
        idx = (ii + offset) % NUMPIXELS
        pixels[idx] = rgb_to_grb(c)
    pixels.show()


def voltage_to_int(voltage, int_max):
    """ Translate the circular touch pad to an integer range.

    NOTE: If the voltage is below TOUCH_MIN_V, this returns None
    """
    if voltage < TOUCH_MIN_V:
        return None
    else:
        mapped = translate(voltage, TOUCH_MIN_V, TOUCH_MAX_V, 0, int_max-1)
        mapped = (int(mapped) + int_max//2) % int_max
        return mapped


idx = 0
while True:
    """ Main loop - listen and respond to button state.

    MODES:
    NO BUTTONS PRESSED
        Lights off
    RED BUTTON
        Three color, rotate with touch
    WHITE BUTTON
        Three color, rotate with touch
        Also controls brightness
    GREEN BUTTON
        Three color, rotate with touch
    RED + GREEN
        Active LED follows touch
        LED slowly rotates without touch
    RED + WHITE
        Rainbow around circle, rotate with touch
    WHITE + GREEN
        Color picker (wheel chooses color)
    RED + WHITE + GREEN
        Fade through rainbow (non-interactive)
    """

    idx += 1
    buttons = get_button_state()
    voltage = getVoltage(analogin)
    offset = voltage_to_int(voltage, NUMPIXELS)
    print((buttons, voltage, offset))

    if buttons == (False, False, False):
        print("Lights off")
        set_three_colors(OFF, OFF, OFF)

    elif buttons == (True, False, False):
        print("Red button pressed")
        if not offset:
            offset = idx // 5
        set_three_colors(PINK, PURPLE, YELLOW, offset)

    elif buttons == (False, True, False):
        print("White button pressed")
        if offset:
            brightness = float(voltage_to_int(voltage, 100)) / 100
            pixels.brightness = brightness
            print("Brightness: ", pixels.brightness)
        else:
            offset = idx // 5
        set_three_colors(RED, BLUE, GREEN, offset)

    elif buttons == (False, False, True):
        print("Green button pressed")
        if not offset:
            offset = idx // 5
        set_three_colors(ORANGE, RED, WHITE, offset)

    elif buttons == (True, False, True):
        print("Red+Green = Follow mode")
        if not offset:
            offset = idx // 5
        for ii in range(NUMPIXELS):
            pixels[ii] = OFF
        index = (offset + 1) % NUMPIXELS
        pixels[index] = rgb_to_grb(PINK)
        pixels.show()

    elif buttons == (True, True, False):
        print("Red+White = Rainbow wheel")
        if not offset:
            offset = idx // 5
        for ii in range(NUMPIXELS):
            rc_index = (ii + offset) * 256 // NUMPIXELS
            pixels[ii] = wheel(rc_index & 255)
        pixels.show()

    elif buttons == (False, True, True):
        print("White+Green = Rainbow picker")
        if offset:
            offset = voltage_to_int(voltage, 256)
        else:
            offset = idx // 5
        for ii in range(NUMPIXELS):
            pixels[ii] = wheel(offset & 255)
        pixels.show()

    elif buttons == (True, True, True):
        print("Red+White+Green = Rainbow fade")
        for i in range(NUMPIXELS):
            pixels[i] = wheel(idx & 255)
        pixels.show()

    time.sleep(0.1)
