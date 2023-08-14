import time
import pyvisa
from matplotlib import pyplot as plt
import numpy as np
import sys
from arduino_utils import *


class Keithley6514:
    def __init__(self, keithley_port="COM5", arduino_port="COM3"):
        # Initialize communication Keithlay6514
        try:
            self.rm = pyvisa.ResourceManager()
            resources = self.rm.list_resources()
            print("Available resources")
            for resource in resources:
                print(resource)
            self.keithley = self.rm.open_resource(keithley_port)
            self.keithley.read_termination = "\r"
            print(self.keithley.query("*IDN?"))
            print(time.asctime(), "Keithley 6514 is properly identified at port", keithley_port)
            self.arduinoobj = arduino(arduino_port)
            print(time.asctime(), "Arduino is properly identified at port", arduino_port)
            print("======================================================================\n")
        except:
            print(time.asctime(), "Error connecting to the port!!!")
            print(time.asctime(), "Recheck the port name or plug in the usb port in different ports.")
            # sys.exit(
            #    1
            # )  # exiing with a non zero value is better for returning from an error

    def measure_volt(self):
        """Voltage measurement function"""
        self.keithley.write("SOUR:VOLT 10")
        self.keithley.write("OUTP 1")
        voltage = self.keithley.query_ascii_values("MEAS:VOLT?")
        print(time.asctime(), "Voltage measurement is done.")
        return voltage[0]

    # Current measurement function
    def measure_current(self):
        """Current measurement function"""
        self.keithley.write("SOUR:CURR 1")
        self.keithley.write("OUTP 1")
        current = self.keithley.query_ascii_values("MEAS:CURR?")
        print(time.asctime(), "Current measurement is done.")
        return current[0]

    # Resistance measurement function
    def measure_resistance(self):
        """Resistance measurement function"""
        self.keithley.write("SOUR:RES 1")
        self.keithley.write("OUTP 1")
        resistance = self.keithley.query_ascii_values("MEAS:RES?")
        print(time.asctime(), "Resistance measurement is done.")
        return resistance[0]

    def measure_charge(self):
        """Charge measurement function"""
        self.keithley.write("SOUR:CHAR 1")
        self.keithley.write("OUTP 1")
        charge = self.keithley.query_ascii_values("MEAS:CHAR?")
        print(time.asctime(), "Charge measurement is done.")
        return charge[0]

    # I-V measurement function
    def IV_measurement(
        self,
        circular=True,
        increment=0.5,
        manual=True,
        sleep_time=0.3,
        machine_sleep_time=0.2,
        range_start=0,
        range_end=5,
    ):
        """Current-Voltage measurement function"""
        if manual == True:
            print("For now the code is set to manual by default")
            print("It is set to measure 0 to 5 and back to 0 by default.")
        dicision = "Y"  # input(
        #    "Do you wish to change the setup. Y to measure 0-5 and N for 0-5-0: "
        # )
        if dicision == "Y" or "y":
            circular = False
        else:
            pass
        temperature = input("Input the measurement temperature in K: ")
        filename = input("Input file name: ")
        filename = (
            filename + "_" + str(temperature) + "K_" + str(int(time.time())) + ".txt"
        )

        print("Please fix the voltage and wait at least 2 seconds  before changing it.")
        print("Measurement is starting...")
        print("======================================================================")
        ini_time = time.time()
        with open(filename, "a") as f:
            f.write("Time" + "\tVoltage" + "\tCurrent" + "\tStandard Deviation\n")
            mult_factor = int(1 / increment)
            for i in range(
                range_start * mult_factor,
                range_end * mult_factor,
                int(increment * mult_factor),
            ):
                measurement = np.zeros(10)
                for j in range(0, 10):
                    try:
                        current = self.keithley.query_ascii_values("MEAS:CURR?")
                        measurement[j] = current[0]
                        time.sleep(0.1)
                    except:
                        time.sleep(0.1)
                        # print("Error in measurement")
                        pass

                    time.sleep(machine_sleep_time)
                print(
                    "Data for voltage",
                    i / mult_factor,
                    "is recorded. Change the voltage. Next measurement is in 10 seconds",
                )
                print(
                    str(time.asctime())
                    + "\t"
                    + str(i / mult_factor)
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                    + "\t"
                    + "Increasing"
                )
                f.writelines(
                    str(time.asctime())
                    + "\t"
                    + str(i / mult_factor)
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                    + "\t"
                    + "Increasing"
                    + "\n"
                )
                time.sleep(sleep_time)
            # if circular == True:
            for i in range(
                range_end * mult_factor,
                range_start * mult_factor,
                -int(increment * mult_factor),
            ):
                measurement = np.zeros(10)
                for j in range(0, 10):
                    try:
                        current = self.keithley.query_ascii_values("MEAS:CURR?")
                        time.sleep(0.1)
                    except:
                        time.sleep(0.1)
                        # print("Error in measurement")
                        pass

                    # self.keithley.write("OUTP 0")
                    measurement[j] = current[0]
                    time.sleep(machine_sleep_time)
                print(
                    "Data for voltage",
                    i / mult_factor,
                    "is recorded. Change the voltage. Next measurement is in 10 seconds",
                )
                print(
                    str(time.asctime())
                    + "\t"
                    + str(i / mult_factor)
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                    + "\t"
                    + "Decreasing"
                )
                f.writelines(
                    str(time.asctime())
                    + "\t"
                    + str(i / mult_factor)
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                    + "\t"
                    + "Decreasing"
                    + "\n"
                )
                time.sleep(sleep_time)
        self.keithley.write("OUTP 0")
        self.keithley.write("SYST:LOC")
        self.keithley.close()
        final_time = time.time()
        print("Measurement is done for temp", temperature, "K")
        print(
            "Time taken for the full measurement =",
            str(round((final_time - ini_time) / 60)),
            "minutes.",
        )
        print("======================================================================")
        return (filename, temperature)

    def animate(i):
        pullData = open("dynamicgraph.txt", "r").read()
        dataArray = pullData.split("\n")
        xar = []
        yar = []
        for eachLine in dataArray:
            if len(eachLine) > 1:
                x, y = eachLine.split(",")
                xar.append(int(x))
                yar.append(int(y))
        ax1.clear()
        ax1.plot(xar, yar)

    def RT_measurement(self, manual=True, machine_sleep_time=0.5, sleep_time=1):
        """Resistant time measurement function"""

        if manual is True:
            print("For now the code is set to manual by default.")
            print("You need to manually input the temperature.")
        # temperature = input("Input the measurement temperature in K: ")
        filename = "RT"  # input("Input file name: ")
        filename = filename + "_" + str(int(time.time())) + ".txt"
        print("Please try to fix the temperature.")
        print("Measurement is starting...")
        print("======================================================================")
        ini_time = time.time()
        with open(filename, "a") as f:
            f.write(
                "Time" + "\tTemperature" + "\tResistance" + "\tStandard Deviation\n"
            )
            while True:
                temperature = input("Input the measurement temperature: ")
                measurement = np.zeros(10)
                for j in range(0, 10):
                    resistance = self.measure_resistance()
                    measurement[j] = resistance
                    time.sleep(machine_sleep_time)
                print(
                    "Data for temperature",
                    temperature,
                    "is recorded. You may change the temperature.",
                )
                print(
                    str(time.asctime())
                    + "\t"
                    + str(temperature)
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                )
                f.writelines(
                    str(time.asctime())
                    + "\t"
                    + str(temperature)
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                    + "\n"
                )
                time.sleep(sleep_time)
                proceed_statement = input(
                    "Do you want to take another data? Y for yes and N for No (default is Yes): "
                )

                if proceed_statement == "N" or "n":
                    self.keithley.close()
                    final_time = time.time()
                    print("Measurement is done for temp", temperature, "K")
                    print(
                        "Time taken for the full measurement =",
                        str(round((final_time - ini_time) / 60)),
                        "minutes.",
                    )
                    print(
                        "======================================================================"
                    )
                    print("The file is saved in", filename)
                    sys.exit(1)

                else:
                    print("")
                    continue

    def Itime_measurement(self, manual=True, machine_sleep_time=0.5, sleep_time=1):
        """Resistant time measurement function"""

        if manual is True:
            print("For now the code is set to manual by default.")
            print("You need to manually input the temperature.")
        # temperature = input("Input the measurement temperature in K: ")
        filename = "Itime"  # input("Input file name: ")
        filename = filename + "_" + str(int(time.time())) + ".txt"
        print("Please try to fix the temperature.")
        print("Measurement is starting...")
        print("======================================================================")
        ini_time = time.time()
        with open(filename, "a") as f:
            f.write("Time" + "Current" + "\tStandard Deviation\n")
            while True:
                temperature = input("Input the measurement temperature: ")
                measurement = np.zeros(10)
                for j in range(0, 10):
                    current = self.measure_current()
                    measurement[j] = current
                    time.sleep(machine_sleep_time)
                print(
                    "Data for temperature",
                    temperature,
                    "is recorded. You may change the temperature.",
                )
                print(
                    str(time.asctime())
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                )
                f.writelines(
                    str(time.asctime())
                    + "\t"
                    + str(np.average(measurement))
                    + "\t"
                    + str(np.std(measurement))
                    + "\n"
                )
                time.sleep(sleep_time)

    # auto I-V measurement function
    def auto_IV_measurement(
        self,
        measurement_sleep_time=1,
        machine_sleep_time=1,
    ):
        """Current-Voltage measurement function"""
        temperature = input("Input the measurement temperature in K: ")
        filename = input("Input file name: ")
        filename = (
            filename + "_" + str(temperature) + "K_" + str(int(time.time())) + ".txt"
        )
        print("Measurement is starting...")
        print("======================================================================")
        vol_range = np.linspace(-5, 5, 51)
        ini_time = time.time()
        self.keithley.write("SOUR:CURR 1")
        self.keithley.write("OUTP 1")

        with open(filename, "a") as f:
            f.write("Time" + "\tVoltage" + "\tCurrent" + "\tStandard Deviation\n")
            for i in vol_range:
                try:
                    self.arduinoobj.arduino_set_voltage((i + 5.0) / 2.0)
                    current = self.keithley.query_ascii_values("MEAS:CURR?")
                    time.sleep(measurement_sleep_time)
                    print(
                        str(time.asctime())
                        + "\t"
                        + str(i)
                        + "\t"
                        + str(current[0])
                        + "\t"
                        + str(current[1])
                        + "\t"
                        + "Increasing"
                    )
                    f.writelines(
                        str(time.asctime())
                        + "\t"
                        + str(i)
                        + "\t"
                        + str(current[0])
                        + "\t"
                        + str(current[1])
                        + "\t"
                        + "Increasing"
                        + "\n"
                    )
                    time.sleep(measurement_sleep_time)
                except:
                    time.sleep(1)
                    print("Error in measurement")
                    pass
                #
                time.sleep(machine_sleep_time)
            for i in vol_range[::-1]:
                # print("Accuring data for reverse voltage ramp", i)
                try:
                    self.arduinoobj.arduino_set_voltage((i + 5.0) / 2.0)
                    current = self.keithley.query_ascii_values("MEAS:CURR?")
                    # print(current)
                    time.sleep(measurement_sleep_time)
                    print(
                        str(time.asctime())
                        + "\t"
                        + str(i)
                        + "\t"
                        + str(current[0])
                        + "\t"
                        + str(current[1])
                        + "\t"
                        + "Decreasing"
                    )
                    f.writelines(
                        str(time.asctime())
                        + "\t"
                        + str(i)
                        + "\t"
                        + str(current[0])
                        + "\t"
                        + str(current[1])
                        + "\t"
                        + "Decreasing"
                        + "\n"
                    )
                except:
                    time.sleep(1)
                    print("Error in measurement")
                    pass

                time.sleep(machine_sleep_time)
        self.keithley.write("OUTP 0")
        self.keithley.write("SYST:LOC")
        self.keithley.close()
        final_time = time.time()
        print("Measurement is done for temp", temperature, "K")
        print(
            "Time taken for the full measurement =",
            str(round((final_time - ini_time) * 1.0 / 60.0)),
            "minutes.",
        )
        print("======================================================================")
        return (filename, temperature)

    def auto_IV_loop_measurement(
        self,
        filename,
        temperature,
        voltage_minimum=-5,
        voltage_maxima=5,
        step_size=0.2,
        loop=1,
        measurement_sleep_time=1,
        machine_sleep_time=1,
    ):
        """Current-Voltage measurement function"""
        print(time.asctime(),"Measurement is starting...")
        print("======================================================================")
        vol_range = np.arange(voltage_minimum, voltage_maxima, step_size)
        ini_time = time.time()
        self.keithley.write("SOUR:CURR 1")
        self.keithley.write("OUTP 1")
        with open(filename, "a") as f:
            f.write("Time" + "\tVoltage" + "\tCurrent" + "\tStandard Deviation\n")

        for j in range(loop):
            print("The loop number is", j+1)
            with open(filename, "a") as f:

                for i in vol_range:
                    try:
                        self.arduinoobj.arduino_set_voltage((i + 5.0) / 2.0)
                        current = self.keithley.query_ascii_values("MEAS:CURR?")
                        time.sleep(measurement_sleep_time)
                        print(
                            str(time.asctime())
                            + "\t"
                            + str(round(i, 2))
                            + "\t"
                            + str(current[0])
                            + "\t"
                            + str(current[1])
                            + "\t"
                            + "Increasing"
                        )
                        f.writelines(
                            str(time.asctime())
                            + "\t"
                            + str(round(i, 2))
                            + "\t"
                            + str(current[0])
                            + "\t"
                            + str(current[1])
                            + "\t"
                            + "Increasing"
                            + "\n"
                        )
                        time.sleep(measurement_sleep_time)
                    except:
                        time.sleep(1)
                        print("Error in measurement")
                        pass
                    time.sleep(machine_sleep_time)
                for i in vol_range[::-1]:
                    # print("Accuring data for reverse voltage ramp", i)
                    try:
                        self.arduinoobj.arduino_set_voltage((i + 5.0) / 2.0)
                        current = self.keithley.query_ascii_values("MEAS:CURR?")
                        # print(current)
                        time.sleep(measurement_sleep_time)
                        print(
                            str(time.asctime())
                            + "\t"
                            + str(round(i, 2))
                            + "\t"
                            + str(current[0])
                            + "\t"
                            + str(current[1])
                            + "\t"
                            + "Decreasing"
                        )
                        f.writelines(
                            str(time.asctime())
                            + "\t"
                            + str(round(i, 2))
                            + "\t"
                            + str(current[0])
                            + "\t"
                            + str(current[1])
                            + "\t"
                            + "Decreasing"
                            + "\n"
                        )
                    except:
                        time.sleep(1)
                        print("Error in measurement")
                        pass

                    time.sleep(machine_sleep_time)
        self.keithley.write("OUTP 0")
        self.keithley.write("SYST:LOC")
        self.keithley.close()
        final_time = time.time()
        print(time.asctime(), "Measurement is done for temp", temperature, "K")
        print(time.asctime(),
            "Time taken for the full measurement =",
            str(round((final_time - ini_time) * 1.0 / 60.0)),
            "minutes.",
        )
        print("======================================================================")
        return (filename, temperature, round((final_time - ini_time) * 1.0 / 60.0))

    def auto_QV_loop_measurement(
        self,
        filename,
        temperature,
        voltage_minimum=-5,
        voltage_maxima=5,
        step_size=0.2,
        loop=1,
        measurement_sleep_time=1,
        machine_sleep_time=1,
    ):
        """Current-Voltage measurement function"""
        print(time.asctime(),"Measurement is starting...")
        print("======================================================================")
        vol_range = np.arange(voltage_minimum, voltage_maxima, step_size)
        ini_time = time.time()
        self.keithley.write("SOUR:CHAR 1")
        self.keithley.write("OUTP 1")

        for j in range(loop):
            with open(filename, "a") as f:
                f.write("Time" + "\tVoltage" + "\tCharge" + "\tStandard Deviation\n")
                for i in vol_range:
                    try:
                        self.arduinoobj.arduino_set_voltage((i + 5.0) / 2.0)
                        charge = self.keithley.query_ascii_values("MEAS:CHAR?")
                        time.sleep(measurement_sleep_time)
                        print(
                            str(time.asctime())
                            + "\t"
                            + str(i)
                            + "\t"
                            + str(charge[0])
                            + "\t"
                            + str(charge[1])
                            + "\t"
                            + "Increasing"
                        )
                        f.writelines(
                            str(time.asctime())
                            + "\t"
                            + str(i)
                            + "\t"
                            + str(charge[0])
                            + "\t"
                            + str(charge[1])
                            + "\t"
                            + "Increasing"
                            + "\n"
                        )
                        time.sleep(measurement_sleep_time)
                    except:
                        time.sleep(1)
                        print("Error in measurement")
                        pass
                    time.sleep(machine_sleep_time)
                for i in vol_range[::-1]:
                    # print("Accuring data for reverse voltage ramp", i)
                    try:
                        self.arduinoobj.arduino_set_voltage((i + 5.0) / 2.0)
                        charge = self.keithley.query_ascii_values("MEAS:CHAR?")
                        # print(current)
                        time.sleep(measurement_sleep_time)
                        print(
                            str(time.asctime())
                            + "\t"
                            + str(i)
                            + "\t"
                            + str(charge[0])
                            + "\t"
                            + str(charge[1])
                            + "\t"
                            + "Decreasing"
                        )
                        f.writelines(
                            str(time.asctime())
                            + "\t"
                            + str(i)
                            + "\t"
                            + str(charge[0])
                            + "\t"
                            + str(charge[1])
                            + "\t"
                            + "Decreasing"
                            + "\n"
                        )
                    except:
                        time.sleep(1)
                        print("Error in measurement")
                        pass

                    time.sleep(machine_sleep_time)
        self.keithley.write("OUTP 0")
        self.keithley.write("SYST:LOC")
        self.keithley.close()
        final_time = time.time()
        print(time.asctime(),"Measurement is done for temp", temperature, "K")
        print(time.asctime(),
            "Time taken for the full measurement =",
            str(round((final_time - ini_time) * 1.0 / 60.0)),
            "minutes.",
        )
        print("======================================================================")
        return (filename, temperature)


def IV_plot_file(filename, temperature, logscale=False, errorplot=False):

    """Plots the IV data with error bars and without error bars"""
    x = []
    y = []
    yerr = []
    with open(filename, "r") as f:

        lines = f.readlines()
        for line in lines[1:]:
            words = line.split("\t")
            try:
                x.append(float(words[1]))
                y.append(float(words[2]))
            except:
                pass
            if errorplot is True:
                yerr.append(float(words[3]))

    # print(x,y)
    plt.scatter(
        np.array(x[: int(len(x) / 2)]),
        np.array(y[: int(len(y) / 2)]),
        label="UP",
    )
    plt.scatter(
        np.array(x[int(len(x) / 2) :]),
        np.array(y[int(len(y) / 2) :]),
        label="DOWN",
    )
    filename = str(filename).strip(".txt")
    plt.xlabel("Voltage in V")
    plt.ylabel("Current in A")
    plt.legend()
    plt.savefig(filename + ".png")
    plt.show()
    if errorplot is True:
        plt.errorbar(x, y, yerr=yerr, fmt=".-")
    # if you want a log plot:
    if logscale == True:
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Voltage in V")
        plt.ylabel("Current in A")
        plt.title("I-V Data for temperature " + str(temperature) + " K")
        plt.savefig(filename + "err.png")
        plt.show()
