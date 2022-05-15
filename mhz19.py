import mh_z19


def measure_co2():
    return mh_z19.read(serial_console_untouched=True)["co2"]
