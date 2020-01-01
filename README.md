# Interacive NeoPixel Color Wheel ("Clock")

Neopixel "clock" face with three button function selects.

Here's the demo video:

<iframe width="560" height="315" src="https://www.youtube.com/embed/8xB9JruYcvE" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Electronics

#### Full Wiring Diagram

#### Digital IO

#### Analog IO

#### NeoPixels

## Code

The code is CircuitPython, drop the main.py into the Trinket M0 folder on the PC, and include the neopixel library.

#### Digital IO

The digital pins are Pull UP as mentioned above.
This means that they are natrually high (`button.value == True`).

```python
import digitalio

button_r = digitalio.DigitalInOut(board.D2)
button_r.switch_to_input(pull=digitalio.Pull.UP)
```

So when the button is pressed we actually test for: `not button.value`.
This is wrapped into a read function that returns which button is pressed:

```python
def get_button_state():
    """ Read and return a tuple of which buttons are pressed.

    returns:
        (Red Pressed, White Pressed, Green Pressed)
    """
    buttons = [button_r, button_w, button_g]
    state = tuple(not b.value for b in buttons)
    return state
```

#### Analog IO

The soft-potentiometer is read through an AnalogIO pin as described above in the Electronics section.

```python
import analogio

TOUCH_MIN_V = 1.8
TOUCH_MAX_V = 3.2
analogin = analogio.AnalogIn(board.A3)
```

The AnalogIn reads an ADC value, which is converted to voltage (`getVoltage()`).
This voltage varies from 1.8 to 3.2 V, this is mapped to an integer range (`voltage_to_int()` using `translate()`).
A voltage less than 1.8 V indicates that there is no touch.

```python
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
```

And can be use for offsets;

```python
voltage = getVoltage(analogin)
offset = voltage_to_int(voltage, NUMPIXELS)
```

or changing brightness;

```python
voltage = getVoltage(analogin)
brightness = float(voltage_to_int(voltage, 100)) / 100
```

or changing position along the color wheel;

```python
voltage = getVoltage(analogin)
offset = voltage_to_int(voltage, NUMPIXELS)
rc_index = (ii + offset) * 256 // NUMPIXELS
```

#### NeoPixels

NeoPixel control is pretty straight forward and follows the examples in the CircuitPython library.

```python
import neopixel

NUMPIXELS = 12
BRIGHTNESS = 0.2
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(board.D4, NUMPIXELS, brightness=BRIGHTNESS, auto_write=False)
# Initalize pixels OFF
for i in range(len(pixels)):
    pixels[i] = OFF
pixels.show()
```

Here's a snippet that sets the three color display and follows the touch (indicated by `offset`) around:

```python
def set_three_colors(CA, CB, CC, offset=0):
    """ Set NeoPixel ring to three colors.
    """
    color_pattern = [CA]*4 + [CB]*4 + [CC]*4
    for ii, c in enumerate(color_pattern):
        idx = (ii + offset) % NUMPIXELS
        pixels[idx] = rgb_to_grb(c)
    pixels.show()
```
