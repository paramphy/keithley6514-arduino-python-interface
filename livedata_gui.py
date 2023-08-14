# Imports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyvisa
import time
import arduino_utils
import tkinter as tk
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Figure initialization
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
plt.title("I-t charecteristics")
plt.ylabel("Current in A")
plt.xlabel("Time")

# Live plot class
class live_plot:

    # Class initialization
    def __init__(
        self, temperature, bias, sample, arduino_port="COM3", keithlay_port="COM5"
    ):
        self.current = []
        self.t = []
        # Initialize communication Keithlay6514
        self.rm = pyvisa.ResourceManager()
        self.rm.list_resources()
        self.keithley = self.rm.open_resource(keithlay_port)
        self.keithley.read_termination = "\r"
        print(self.keithley.query("*IDN?"))
        self.filename = "It-temp- " + bias + "-" + temperature + "-" + sample + ".txt"
        self.board = arduino_utils.arduino(arduino_port)
        self.board.arduino_set_voltage((float(bias) + 5.0) / 2.0)
        self.initial_time = time.time()

    # Animation function
    def animate(self, i, t, current):
        # Read current from Keithlay6514
        try:
            current_new = self.keithley.query_ascii_values("MEAS:CURR?")
            self.current.append(current_new[0])
            self.t.append(time.time() - self.initial_time)
            with open(self.filename, "a") as f:
                f.write(
                    str(time.time() - self.initial_time)
                    + "\t"
                    + str(current_new[0])
                    + "\n"
                )
            # time.sleep(0.01)

        except:
            print("error")
            pass

        ax.clear()
        ax.plot(t, current)
        return (t, current)

    # Main function
    def main(self):

        print("The measurement is starting....")
        self.ani = animation.FuncAnimation(
            fig, self.animate, fargs=(self.t, self.current), interval=25, blit=False
        )

        plt.show()
        return self.ani


# Main loop code execution function
def execute_code():

    temperature = entry1.get()
    bias = entry2.get()
    sample_name = entry3.get()
    measurement_obj = live_plot(temperature, bias, sample_name)
    result = f"Inputs: {temperature}, {bias}, {sample_name}"
    label.config(text=result)
    anim = measurement_obj.main()


if __name__ == "__main__":

    root = tk.Tk()
    root.title("Live data GUI")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(
        row=0,
        column=0,
        columnspan=2,
    )
    label1 = tk.Label(root, text="Input temperature ")
    label1.grid(row=1, column=0)
    entry1 = tk.Entry(root)
    entry1.grid(row=1, column=1)

    label2 = tk.Label(root, text="Input bias ")
    label2.grid(row=2, column=0)
    entry2 = tk.Entry(root)
    entry2.grid(row=2, column=1)

    label3 = tk.Label(root, text="Input Sample name ")
    label3.grid(row=3, column=0)
    entry3 = tk.Entry(root)
    entry3.grid(row=3, column=1)

    button = tk.Button(root, text="Start measurement", command=execute_code)
    button.grid(row=4, column=0, columnspan=2)

    label = tk.Label(root, text="")
    label.grid(row=5, column=0, columnspan=2)
    copyright = tk.Label(root, text="Copyright @Paramesh, 2023")
    copyright.grid(row=6, column=1, columnspan=2)
    root.mainloop()
