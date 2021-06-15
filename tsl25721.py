from smbus2 import SMBus

TSL25721_WHO_ID   = 0x34

TSL25721_ADR      = 0x39
TSL25721_COMMAND  = 0x80
TSL25721_TYPE_REP = 0x00
TSL25721_TYPE_INC = 0x20
TSL25721_ALSIFC   = 0x66

TSL25721_SAI      = 0x40
TSL25721_AIEN     = 0x10
TSL25721_WEN      = 0x80
TSL25721_AEN      = 0x02
TSL25721_PON      = 0x01

TSL25721_ENABLE   = 0x00
TSL25721_ATIME    = 0x01
TSL25721_WTIME    = 0x03
TSL25721_AILTL    = 0x04
TSL25721_AILTH    = 0x05
TSL25721_AIHTL    = 0x06
TSL25721_AIHTH    = 0x07
TSL25721_PRES     = 0x0C
TSL25721_CONFIG   = 0x0D
TSL25721_CONTROL  = 0x0F
TSL25721_ID       = 0x12
TSL25721_STATUS   = 0x13
TSL25721_C0DATA   = 0x14
TSL25721_C0DATAH  = 0x15
TSL25721_C1DATA   = 0x16
TSL25721_C1DATAH  = 0x17

ATIME             = 0xC0
GAIN              = 1.0

BUS_NUMBER        = 1
i2c = SMBus(BUS_NUMBER)


def measure_illuminance():
    if not __setup():
        return -1

    try:
        adc = __read_illuminance()
        cpl = (2.73 * (256 - ATIME) * GAIN) / (60.0)
        lux1 = ((adc[0] * 1.00) - (adc[1] * 1.87)) / cpl
        lux2 = ((adc[0] * 0.63) - (adc[1] * 1.00)) / cpl

        return max(0, lux1, lux2)
    except OSError:
        return -1


def __setup():
    if not __init_tsl2572():
        return False

    return True


def __init_tsl2572():
    if not __detect_device():
        return False

    try:
        __write_reg(TSL25721_COMMAND | TSL25721_TYPE_INC | TSL25721_CONTROL, 0x00)
        __write_reg(TSL25721_COMMAND | TSL25721_TYPE_INC | TSL25721_CONFIG, 0x00)
        __write_reg(TSL25721_COMMAND | TSL25721_TYPE_INC | TSL25721_ATIME, ATIME)
        __write_reg(TSL25721_COMMAND | TSL25721_TYPE_INC | TSL25721_ENABLE, TSL25721_AEN | TSL25721_PON)

        return True
    except OSError:
        return False


def __detect_device():
    try:
        id = __test_who_am_i()
        if not id[0] == TSL25721_WHO_ID:
            return False

        return True
    except OSError:
        return False


def __test_who_am_i():
    return __read_reg(TSL25721_COMMAND | TSL25721_TYPE_INC | TSL25721_ID)


def __write_reg(reg, value):
    i2c.write_byte_data(TSL25721_ADR, reg, value)


def __read_reg(reg):
    return i2c.read_i2c_block_data(TSL25721_ADR, TSL25721_COMMAND | TSL25721_TYPE_INC | reg, 1)


def __read_illuminance():
    dat = i2c.read_i2c_block_data(TSL25721_ADR, TSL25721_COMMAND | TSL25721_TYPE_INC | TSL25721_C0DATA, 4)
    adc0 = (dat[1] << 8) | dat[0]
    adc1 = (dat[3] << 8) | dat[2]

    return [adc0, adc1]
