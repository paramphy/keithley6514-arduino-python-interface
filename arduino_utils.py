# import libraries
import time
import keyboard
import pyfirmata
import numpy as np


class arduino:
    # init method or constructor
    def __init__(self, port):
        self.port = port
        self.board = pyfirmata.Arduino(self.port)
        self.pwm_2 = self.board.get_pin("d:9:p")

    def arduino_set_voltage(self, value):

        value = value * 255 / 5.0
        self.pwm_2.write(value / 255.0)


def main():
    arduinoobj = arduino("COM3")
    voltage_range = np.linspace(0, 5, 101)
    print("Startig the voltage sweep")
    while True:
        for i in voltage_range:
            arduinoobj.arduino_set_voltage(i)
            print("Voltage", i)
            time.sleep(5)
        for i in voltage_range[::-1]:
            arduinoobj.arduino_set_voltage(i)
            print("Voltage", i)
            time.sleep(5)


if __name__ == "__main__":
    main()
