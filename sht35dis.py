from smbus2 import SMBus

SHT35DIS_ADR = 0x45
CTRL_REG1    = 0x2C

BUS_NUMBER   = 1
i2c = SMBus(BUS_NUMBER)


def measure_temperature():
    if not __setup():
        return -1

    try:
        return __compensate_temperature()
    except OSError:
        return -1


def measure_humidity():
    if not __setup():
        return -1

    try:
        return __compensate_humidity()
    except OSError:
        return -1


def __setup():
    try:
        __enable_default()

        return True
    except OSError:
        return False


def __enable_default():
    __write_reg(CTRL_REG1, 0x06)


def __write_reg(reg, value):
    val = [value]
    i2c.write_i2c_block_data(SHT35DIS_ADR, reg, val)


def __read_reg(reg):
    value = i2c.read_i2c_block_data(SHT35DIS_ADR, reg, 1)

    return value


def __compensate_temperature():
    data = i2c.read_i2c_block_data(SHT35DIS_ADR, 0x00, 6)
    st = data[0] << 8 | data[1]
    temperature = -45 + (175 * st / float((2 ** 16 - 1)))

    return temperature


def __compensate_humidity():
    data = i2c.read_i2c_block_data(SHT35DIS_ADR, 0x00, 6)
    srh = data[3] << 8 | data[4]
    humidity = 100 * srh / float((2 ** 16 - 1))

    return humidity
