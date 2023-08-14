# Imports
import matplotlib.pyplot as plt
import pyvisa
import time
import arduino_utils
import tkinter as tk
from kiethlay_functions import *
from tkinter import ttk 


root = tk.Tk()
root.title("IV Measurement Setup")
options = ["COM3", "COM5"]
keithley_port_label = tk.Label(root, text="Keithlay Port")
keithley_port_label.grid(row=1, column=0, columnspan=2)
keithley_port = ttk.Combobox(root, values=options)
keithley_port.grid(row=1, column=2, columnspan=2)
keithley_port.set("Pick a PORT")

arduino_port_lebel = tk.Label(root, text="Arduino Port")
arduino_port_lebel.grid(row=2, column=0, columnspan=2)
arduino_port = ttk.Combobox(root, values=options)
arduino_port.grid(row=2, column=2, columnspan=2)
arduino_port.set("Pick a PORT")


def setup():
    keithley_port_no = keithley_port.get()
    arduino_port_no = arduino_port.get()
    global keithley_obj
    keithley_obj = Keithley6514(keithley_port_no, arduino_port_no)
    result = f"Inputs: {keithley_port_no}, {arduino_port_no}. Setup Complete."
    label.config(text=result)


# Main loop code execution function
def volt_measurement():

    volt = keithley_obj.measure_volt()
    result = f"{volt} in V"
    output_volt.config(text=result)


# Main loop code execution function
def current_measurement():

    current = keithley_obj.measure_current()
    result = f"{current} in A"
    output_current.config(text=result)


# Main loop code execution function
def charge_measurement():

    charge = keithley_obj.measure_charge()
    result = f"{charge} in C"
    output_charge.config(text=result)


# Main loop code execution function
def resistance_measurement():

    resistance = keithley_obj.measure_resistance()
    result = f"{resistance} in Ohms"
    output_resistance.config(text=result)


def auto_IV_loop_measurement():
    temperature_val = temperature.get()
    sample_name = sample.get()
    loop_number = loop_no.get()
    minimum_voltage_val = int(voltage_minima.get())
    maximum_voltage_val = int(voltage_maxima.get())
    step_val = float(voltage_step.get())
    filename = sample_name + "-"+ temperature_val + "-" + str(time.time())
    filename, temperature_val, time_taken = keithley_obj.auto_IV_loop_measurement(
        filename,
        temperature_val,
        voltage_minimum= minimum_voltage_val,
        voltage_maxima=maximum_voltage_val,
        step_size = step_val,
        loop=int(loop_number),
    )
    result = f"Total time taken for the measurement {time_taken} minutes."
    output_autoIV.config(text=result)
    IV_plot_file(str(filename), temperature_val)


button = tk.Button(root, text="Machine setup", command=setup)
button.grid(row=4, column=0, columnspan=4)
label = tk.Label(root, text="")
label.grid(row=3, column=0, columnspan=4)

# Button for voltage measurement
button = tk.Button(root, text="Measure Voltage", command=volt_measurement)
button.grid(row=5, column=0, columnspan=2)
output_volt = tk.Label(root, text="")
output_volt.grid(row=5, column=2, columnspan=2)

# Button for current measurement
button = tk.Button(root, text="Measure Current", command=current_measurement)
button.grid(row=7, column=0, columnspan=2)
output_current = tk.Label(root, text="")
output_current.grid(row=7, column=3, columnspan=2)

# Button for charge measurement
button = tk.Button(root, text="Measure Charge", command=charge_measurement)
button.grid(row=9, column=0, columnspan=2)
output_charge = tk.Label(root, text="")
output_charge.grid(row=9, column=2, columnspan=2)

# Button for resistance measurement
button = tk.Button(root, text="Measure Resistance", command=resistance_measurement)
button.grid(row=11, column=0, columnspan=2)
output_resistance = tk.Label(root, text="")
output_resistance.grid(row=11, column=2, columnspan=2)

# auto-IV measurement 
measurement_label = tk.Label(root, text="Auto IV measurement")
measurement_label.grid(row=13, column=0, columnspan=4, rowspan= 2)

# temperature input
temperature_label = tk.Label(root, text="Temperature in K")
temperature_label.grid(row=15, column=0, columnspan=2)
temperature = tk.Entry(root)
temperature.grid(row=15, column=2, columnspan=2)
# sample name input
sample_label = tk.Label(root, text="Sample Name")
sample_label.grid(row=17, column=0, columnspan=2)
sample = tk.Entry(root)
sample.grid(row=17, column=2, columnspan=2)
# Loop no input
loop_no_label = tk.Label(root, text="Loop number")
loop_no_label.grid(row=19, column=0, columnspan=2)
loop_no = tk.Entry(root)
loop_no.grid(row=19, column=2, columnspan=2)

# VOltage minimum input
voltage_minima_label = tk.Label(root, text="Minimum Voltage (upto -5 V)")
voltage_minima_label.grid(row=21, column=0, columnspan=2)
voltage_minima = tk.Entry(root)
voltage_minima.grid(row=21, column=2, columnspan=2)

# Voltage maxima input
voltage_maxima_label = tk.Label(root, text="Maximum voltage (upto 5V)")
voltage_maxima_label.grid(row=23, column=0, columnspan=2)
voltage_maxima = tk.Entry(root)
voltage_maxima.grid(row=23, column=2, columnspan=2)

# Voltage step value input
voltage_step_label = tk.Label(root, text="Voltage step (Keep more than 0.2 V)")
voltage_step_label.grid(row=25, column=0, columnspan=2)
voltage_step = tk.Entry(root)
voltage_step.grid(row=25, column=2, columnspan=2)

# Button for loop iv measurement
button = tk.Button(root, text="Start measurement", command=auto_IV_loop_measurement)
button.grid(row=27, column=0, columnspan=4)
output_autoIV = tk.Label(root, text="")
output_autoIV.grid(row=29, column=0, columnspan=4)
copyright = tk.Label(root, text="Copyright @Paramesh, 2023")
copyright.grid(row=31, column=1, columnspan=2)
root.mainloop()
