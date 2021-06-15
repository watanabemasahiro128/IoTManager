from smbus2 import SMBus

BME280_ADR = 0x76

BUS_NUMBER = 1
i2c = SMBus(BUS_NUMBER)

dig_t = []
dig_p = []
dig_h = []
t_fine = 0


def measure_temperature():
    __setup()
    __get_calib_param()

    data = []
    for i in range(0xF7, 0xF7+8):
        data.append(bus.read_byte_data(BME280_ADR, i))
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    temperature = __compensate_temperature(temp_raw)

    return temperature


def measure_pressure():
    __setup()
    __get_calib_param()

    data = []
    for i in range(0xF7, 0xF7+8):
        data.append(bus.read_byte_data(BME280_ADR, i))
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    pressure = __compensate_pressure(pres_raw)

    return pressure


def measure_humidity():
    __setup()
    __get_calib_param()

    data = []
    for i in range(0xF7, 0xF7+8):
        data.append(bus.read_byte_data(BME280_ADR, i))
    hum_raw = (data[6] << 8) | data[7]
    humidity = __compensate_humidity(hum_raw)

    return humidity


def __setup():
    osrs_t = 1  # Temperature oversampling x 1
    osrs_p = 1  # Pressure oversampling x 1
    osrs_h = 1  # Humidity oversampling x 1
    mode = 3  # Normal mode
    t_sb = 5  # Tstandby 1000ms
    filter = 0  # Filter off
    spi3w_en = 0  # 3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h

    __write_reg(0xF2, ctrl_hum_reg)
    __write_reg(0xF4, ctrl_meas_reg)
    __write_reg(0xF5, config_reg)


def __write_reg(reg_address, data):
    bus.write_byte_data(BME280_ADR, reg_address, data)


def __get_calib_param():
    calib = []
    for i in range(0x88, 0x88+24):
        calib.append(bus.read_byte_data(BME280_ADR, i))
    calib.append(bus.read_byte_data(BME280_ADR, 0xA1))
    for i in range(0xE1, 0xE1+7):
        calib.append(bus.read_byte_data(BME280_ADR, i))

    dig_t.append((calib[1] << 8) | calib[0])
    dig_t.append((calib[3] << 8) | calib[2])
    dig_t.append((calib[5] << 8) | calib[4])
    dig_p.append((calib[7] << 8) | calib[6])
    dig_p.append((calib[9] << 8) | calib[8])
    dig_p.append((calib[11] << 8) | calib[10])
    dig_p.append((calib[13] << 8) | calib[12])
    dig_p.append((calib[15] << 8) | calib[14])
    dig_p.append((calib[17] << 8) | calib[16])
    dig_p.append((calib[19] << 8) | calib[18])
    dig_p.append((calib[21] << 8) | calib[20])
    dig_p.append((calib[23] << 8) | calib[22])
    dig_h.append(calib[24])
    dig_h.append((calib[26] << 8) | calib[25])
    dig_h.append(calib[27])
    dig_h.append((calib[28] << 4) | (0x0F & calib[29]))
    dig_h.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
    dig_h.append(calib[31])

    for i in range(1, 2):
        if dig_t[i] & 0x8000:
            dig_t[i] = (-dig_t[i] ^ 0xFFFF) + 1
    for i in range(1, 8):
        if dig_p[i] & 0x8000:
            dig_p[i] = (-dig_p[i] ^ 0xFFFF) + 1
    for i in range(0, 6):
        if dig_h[i] & 0x8000:
            dig_h[i] = (-dig_h[i] ^ 0xFFFF) + 1


def __compensate_temperature(adc_t):
    global t_fine
    v1 = (adc_t / 16384 - dig_t[0] / 1024) * dig_t[1]
    v2 = (adc_t / 131072 - dig_t[0] / 8192) * (adc_t / 131072 - dig_t[0] / 8192) * dig_t[2]
    t_fine = v1 + v2
    temperature = t_fine / 5120

    return temperature


def __compensate_pressure(adc_p):
    global t_fine
    v1 = (t_fine / 2) - 64000
    v2 = (((v1 / 4) * (v1 / 4)) / 2048) * dig_p[5]
    v2 += ((v1 * dig_p[4]) * 2)
    v2 = (v2 / 4) + (dig_p[3] * 65536)
    v1 = (((dig_p[2] * (((v1 / 4) * (v1 / 4)) / 8192)) / 8) + ((dig_p[1] * v1) / 2)) / 262144
    v1 = ((32768 + v1) * dig_p[0]) / 32768

    if v1 == 0:
        return 0

    pressure = ((1048576 - adc_p) - (v2 / 4096)) * 3125
    if pressure < 0x80000000:
        pressure = (pressure * 2) / v1
    else:
        pressure = (pressure / v1) * 2
    v1 = (dig_p[8] * (((pressure / 8) * (pressure / 8)) / 8192)) / 4096
    v2 = ((pressure / 4) * dig_p[7]) / 8192
    pressure += ((v1 + v2 + dig_p[6]) / 16)
    pressure /= 100

    return pressure


def __compensate_humidity(adc_h):
    global t_fine
    humidity = t_fine - 76800

    if humidity == 0:
        return 0

    humidity = (adc_h - (dig_h[3] * 64 + dig_h[4] / 16384 * humidity)) * (dig_h[1] / 65536 * (1 + dig_h[5] / 67108864 * humidity * (1 + dig_h[2] / 67108864 * humidity)))
    humidity *= (1 - dig_h[0] * humidity / 524288)
    if humidity > 100:
        humidity = 100
    elif humidity < 0:
        humidity = 0

    return humidity
