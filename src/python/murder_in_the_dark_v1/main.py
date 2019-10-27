import sys
import random
import time
import board
import busio
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_ht16k33 import segments

# Initialize the I2C bus:
i2c = busio.I2C(board.SCL, board.SDA)

####################################################################################
# Button init
####################################################################################
# Initialize the MCP23017 chip on the bonnet
mcp = MCP23017(i2c)

# Optionally change the address of the device if you set any of the A0, A1, A2
# pins.  Specify the new address with a keyword parameter:
#mcp = MCP23017(i2c, address=0x21)  # MCP23017 w/ A0 set

# Make a list of all the port A pins (a.k.a 0-7)
port_a_pins = []
for pin in range(0, 16):
    port_a_pins.append(mcp.get_pin(pin))

## Make a list of all the port B pins (a.k.a 8-15)
#port_b_pins = []
#for pin in range(8, 16):
#    port_b_pins.append(mcp.get_pin(pin))

# Set all the port A pins to output
for pin in port_a_pins:
    pin.direction = Direction.INPUT
    pin.pull = Pull.UP

## Set all the port B pins to input, with pullups!
#for pin in port_b_pins:
#    pin.direction = Direction.INPUT
#    pin.pull = Pull.UP

# Turn on all port A pins for 1/10 of a second
#while True:
#    for pin in port_a_pins:
#        pin.value = True    # turn LED on!
#        time.sleep(0.1)     # wait 0.1 seconds
#        pin.value = False   # turn LED off



####################################################################################
# LED segment init
####################################################################################
# This creates a 7 segment 4 character display:
display = segments.Seg7x4(i2c)
# Clear the display.
display.fill(0)

def get_code(exclude):
    code = random.randint(1,9)
    while code == exclude:
        code = random.randint(1,9)
    return code

code1, code2, code3, code4 = range(4)
def reset_code():
    global code1, code2, code3, code4
    # what's the code? different every reboot
    code1 = get_code(0)
    code2 = get_code(code1)
    code3 = get_code(code2)
    code4 = get_code(code3)
    print(f'new code is {code1}{code2}{code3}{code4}')
# initial code
reset_code()

bomb_armed_ts = None # when was the bomb last armed?  None if not armed
triggers_pushed_ts = None # when were the triggers last pushed? None if not pushed
display_code = False

# which button is pushed?
is_on = [False]*len(port_a_pins)

entered_code = [] # list of buttons that have been pushed. Cleared with triggers

def update_display():
    # display code (triggers are down)
    if triggers_pushed_ts is not None:
        if time.time() - triggers_pushed_ts > 2:
            display.print(f'{code1}{code2}{code3}{code4}')
        else: 
            display.print('8888')
    # countdown
    elif bomb_armed_ts is not None:
        # 05.2f  means 5 total characters, prefixed with zeros, two dec precision
        #print(f'display {60-(time.time()-bomb_armed_ts):05.2f}')
        display.print(f'{60-(time.time()-bomb_armed_ts):05.2f}')
    # nuthin
    else:
        display.fill(0)

    
def update_button_state():
    # update button state
    for num, button in enumerate(port_a_pins):
        if not button.value:
            # turn on matching port A pin
            if not is_on[num]:
                #print("Button #", num, "pressed!")
                #port_a_pins[num].value = True    # turn LED on!
                is_on[num] = True
        else:
            if is_on[num]:
                #print("Button #", num, "released!")
                #port_a_pins[num].value = False    # turn LED off
                is_on[num] = False

while True:
    update_button_state()
    # detect triggers
    if is_on[15] and is_on[14]:
        entered_code = [] # reset the code
        #print(f'triggers are being pushed for the first time')
        if triggers_pushed_ts is None:
            triggers_pushed_ts = time.time()
    else:
        triggers_pushed_ts = None
    # detect code buttons
    for but in range(10):
        if is_on[but]:
            code_input = but+1
            print(f'entered code button: {code_input}. Code buffer now == {entered_code}')
            if len(entered_code)==0 or code_input != entered_code[-1]:
                entered_code.append(code_input)
    # arm/disarm the bomb
    if f'{code1}{code2}{code3}{code4}' == ''.join(str(c) for c in entered_code):
        if bomb_armed_ts is None:
            print('armed the bomb')
            bomb_armed_ts = time.time()
            entered_code = []
            reset_code()
        else:
            print('disarmed the bomb! yay for you! Take a moment to celebrate yourself')
            bomb_armed_ts = None
            entered_code = []
            display.fill(0)
            reset_code()
    # code failure. Try again
    if len(entered_code)>4:
        entered_code = []
    # explode
    if bomb_armed_ts is not None and time.time() - bomb_armed_ts > 60:
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('BOMB ESPLODED! All your base are belong to us.')
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        display.print('dead')
        sys.exit(1)
    update_display()




