import spidev

DUMMY      = 0xff
START      = 0x47
INPUT_MODE = 0x20
MSB        = 0x08
CHANNEL    = 0x00


def measure():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    spi.bits_per_word = 8
    ad = spi.xfer2([(START + MSB + INPUT_MODE + CHANNEL), DUMMY])
    val = ((ad[0] & 0x03) << 8) + ad[1]
    voltage = (val * 3.3) / 1023
    spi.close()

    return val, voltage
