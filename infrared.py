import time
import json
import pigpio

GPIO = 17
FILE = "signals.json"
FREQ = 38.0

last_tick = 0
in_code = False
code = []
fetching_code = False


def send(arg):
    pi = pigpio.pi()
    if not pi.connected:
        return False

    try:
        f = open(FILE, "r")
    except FileNotFoundError:
        print(f"Can't open: {FILE}")
        return False
    records = json.load(f)
    f.close()

    pi.set_mode(GPIO, pigpio.OUTPUT)
    pi.wave_add_new()
    print("Playing")
    if arg in records:
        code = records[arg]
        wave = [0] * len(code)
        marks_wid = {}
        spaces_wid = {}
        for i in range(0, len(code)):
            ci = code[i]
            if i & 1:
                if ci not in spaces_wid:
                    pi.wave_add_generic([pigpio.pulse(0, 0, ci)])
                    spaces_wid[ci] = pi.wave_create()
                wave[i] = spaces_wid[ci]
            else:
                if ci not in marks_wid:
                    wf = __carrier(GPIO, FREQ, ci)
                    pi.wave_add_generic(wf)
                    marks_wid[ci] = pi.wave_create()
                wave[i] = marks_wid[ci]
        pi.wave_chain(wave)
        print("key " + arg)
        while pi.wave_tx_busy():
            time.sleep(0.002)
        for i in marks_wid:
            pi.wave_delete(marks_wid[i])
        marks_wid = {}
        for i in spaces_wid:
            pi.wave_delete(spaces_wid[i])
        spaces_wid = {}
        pi.stop()

        return True
    else:
        print(f"Id {arg} not found")
        pi.stop()

        return False


def __carrier(gpio, frequency, micros):
    wf = []
    cycle = 1000.0 / frequency
    cycles = int(round(micros / cycle))
    on = int(round(cycle / 2.0))
    sofar = 0
    for c in range(cycles):
        target = int(round((c + 1) * cycle))
        sofar += on
        off = target - sofar
        sofar += off
        wf.append(pigpio.pulse(1 << gpio, 0, on))
        wf.append(pigpio.pulse(0, 1 << gpio, off))

    return wf
