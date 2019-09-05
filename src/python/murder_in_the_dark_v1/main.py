import busio
import board
import time

from adafruit_mcp230xx.mcp23017 import MCP23017

# init the i2c bus
i2c = busio.I2C(board.SCL, board.SDA)

# create an instance of mcp
mcp = MCP23017(i2c)

pin12 = mcp.get_pin(12)
# set pin 12 high
pin12.switch_to_output(value=True)
time.sleep(1)
pin12.switch_to_output(value=False)
