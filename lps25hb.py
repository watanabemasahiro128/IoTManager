from smbus2 import SMBus

SA0_LOW_ADDRESS       = 0x5C
SA0_HIGH_ADDRESS      = 0x5D
LPS25HB_ADR           = SA0_HIGH_ADDRESS
TEST_REG_NACK         = -1
LPS25HB_WHO_ID        = 0xBD

REF_P_XL              = 0x08
REF_P_L               = 0x09
REF_P_H               = 0x0A

WHO_AM_I              = 0x0F

RES_CONF              = 0x10

CTRL_REG1             = 0x20
CTRL_REG2             = 0x21
CTRL_REG3             = 0x22
CTRL_REG4             = 0x23

STATUS_REG            = 0x27

PRESS_OUT_XL          = 0x28
PRESS_OUT_L           = 0x29
PRESS_OUT_H           = 0x2A
TEMP_OUT_L            = 0x2B
TEMP_OUT_H            = 0x2C

FIFO_CTRL             = 0x2E
FIFO_STATUS           = 0x2F

RPDS_L                = 0x39
RPDS_H                = 0x3A

INTERRUPT_CFG         = -1
INT_SOURCE            = -2
THS_P_L               = -3
THS_P_H               = -4

LPS25HB_INTERRUPT_CFG = 0x24
LPS25HB_INT_SOURCE    = 0x25
LPS25HB_THS_P_L       = 0x30
LPS25HB_THS_P_H       = 0x31

BUS_NUMBER            = 1
i2c = SMBus(BUS_NUMBER)

translated_regs = [0]


def measure_pressure_millibars():
    if not __setup():
        return -1

    try:
        return __read_pressure_raw() / 4096
    except OSError:
        return -1


def measure_pressure_inches_hg():
    if not __setup():
        return -1

    try:
        return __read_pressure_raw() / 138706.5
    except OSError:
        return -1


def measure_temperature_c():
    if not __setup():
        return -1

    try:
        return 42.5 + __read_temperature_raw() / 480
    except OSError:
        return -1


def measure_temperature_f():
    if not __setup():
        return -1

    try:
        return 108.5 + __read_temperature_raw() / 480 * 1.8
    except OSError:
        return -1


def pressure_to_altitude_meters(pressure_mbar, altimeter_setting_mbar=1013.25):
    return (1 - pow(pressure_mbar / altimeter_setting_mbar, 0.190263)) * 44330.8


def pressure_to_altitude_feet(pressure_inHg, altimeter_setting_inHg=29.9213):
    return (1 - pow(pressure_inHg / altimeter_setting_inHg, 0.190263)) * 145442


def __setup():
    if not __init_lps25hb():
        return False

    try:
        __enable_default()
        return True
    except OSError:
        return False


def __init_lps25hb():
    if not __detect_device():
        return False

    translated_regs.append(LPS25HB_INTERRUPT_CFG)
    translated_regs.append(LPS25HB_INT_SOURCE)
    translated_regs.append(LPS25HB_THS_P_L)
    translated_regs.append(LPS25HB_THS_P_H)

    return True


def __detect_device():
    try:
        id = __test_who_am_i()
        if not id[0] == LPS25HB_WHO_ID:
            raise Exception

        return True
    except OSError:
        return False


def __test_who_am_i():
    return __read_reg(WHO_AM_I)


def __write_reg(reg, value):
    if (reg < 0):
        reg = translated_regs[-reg]
    val = [value]
    i2c.write_i2c_block_data(LPS25HB_ADR, reg, val)


def __read_reg(reg):
    if(reg < 0):
        reg = translated_regs[-reg]

    return i2c.read_i2c_block_data(LPS25HB_ADR, reg, 1)


def __enable_default():
    # PD = 1 (active mode), ODR = 011 (12.5Hz)
    # 0xB0 = 0b10110000
    __write_reg(CTRL_REG1, 0xB0)


def __read_pressure_raw():
    p = i2c.read_i2c_block_data(LPS25HB_ADR, PRESS_OUT_XL, 1)
    p += i2c.read_i2c_block_data(LPS25HB_ADR, PRESS_OUT_L, 1)
    p += i2c.read_i2c_block_data(LPS25HB_ADR, PRESS_OUT_H, 1)

    return p[2] << 16 | p[1] << 8 | p[0]


def __read_temperature_raw():
    t = i2c.read_i2c_block_data(LPS25HB_ADR, TEMP_OUT_L, 1)
    t += i2c.read_i2c_block_data(LPS25HB_ADR, TEMP_OUT_H, 1)

    return (t[1] << 8 | t[0]) - 65535
