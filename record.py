import os
import time
import json
import argparse
import pigpio

p = argparse.ArgumentParser()
p.add_argument("-g", "--gpio", help="GPIO for RX/TX", type=int, default=18)
p.add_argument("--id", help="IR codes", required=True, type=str)
p.add_argument("--freq", help="frequency kHz", type=float, default=38.0)
p.add_argument("--glitch", help="glitch us", type=int, default=100)
p.add_argument("--post", help="postamble ms", type=int, default=120)
p.add_argument("--pre", help="preamble ms", type=int, default=200)
p.add_argument("--short", help="short code length", type=int, default=10)
p.add_argument("--tolerance", help="tolerance percent", type=int, default=15)
p.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
p.add_argument("--no-confirm", help="No confirm needed", action="store_true")
args = p.parse_args()

GPIO       = args.gpio
FILE       = "signals.json"
ID         = args.id
FREQ       = args.freq
GLITCH     = args.glitch
POST_MS    = args.post
PRE_MS     = args.pre
SHORT      = args.short
TOLERANCE  = args.tolerance
VERBOSE    = args.verbose
NO_CONFIRM = args.no_confirm

POST_US    = POST_MS * 1000
PRE_US     = PRE_MS * 1000
CONFIRM    = not NO_CONFIRM
TOLER_MIN  = (100 - TOLERANCE) / 100.0
TOLER_MAX  = (100 + TOLERANCE) / 100.0

last_tick = 0
in_code = False
code = []
fetching_code = False


def cbf(gpio, level, tick):
    global last_tick, in_code, code, fetching_code
    if level != pigpio.TIMEOUT:
        edge = pigpio.tickDiff(last_tick, tick)
        last_tick = tick
        if fetching_code:
            if (edge > PRE_US) and (not in_code):
                in_code = True
                pi.set_watchdog(GPIO, POST_MS)
            elif (edge > POST_US) and in_code:
                in_code = False
                pi.set_watchdog(GPIO, 0)
                end_of_code()
            elif in_code:
                code.append(edge)
    else:
        pi.set_watchdog(GPIO, 0)
        if in_code:
            in_code = False
            end_of_code()


def end_of_code():
    global code, fetching_code
    if len(code) > SHORT:
        normalise(code)
        fetching_code = False
    else:
        code = []
        print("Short code, probably a repeat, try again")


def normalise(c):
    if VERBOSE:
        print("before normalise", c)
    entries = len(c)
    p = [0] * entries
    for i in range(entries):
        if not p[i]:
            v = c[i]
            tot = v
            similar = 1.0
            for j in range(i + 2, entries, 2):
                if not p[j]:
                    if (c[j]*TOLER_MIN) < v < (c[j] * TOLER_MAX):
                        tot += c[j]
                        similar += 1.0
            newv = round(tot / similar, 2)
            c[i] = newv
            for j in range(i + 2, entries, 2):
                if not p[j]:
                    if (c[j] * TOLER_MIN) < v < (c[j] * TOLER_MAX):
                        c[j] = newv
                        p[j] = 1
    if VERBOSE:
        print("after normalise", c)


def compare(p1, p2):
    if len(p1) != len(p2):
        return False

    for i in range(len(p1)):
        v = p1[i] / p2[i]
        if (v < TOLER_MIN) or (v > TOLER_MAX):
            return False

    for i in range(len(p1)):
        p1[i] = int(round((p1[i] + p2[i]) / 2.0))
    if VERBOSE:
        print("after compare", p1)
    return True


def tidy(records):
    tidy_mark_space(records, 0)
    tidy_mark_space(records, 1)


def tidy_mark_space(records, base):
    ms = {}
    for rec in records:
        rl = len(records[rec])
        for i in range(base, rl, 2):
            if records[rec][i] in ms:
                ms[records[rec][i]] += 1
            else:
                ms[records[rec][i]] = 1
    if VERBOSE:
        print("t_m_s A", ms)
    v = None
    for plen in sorted(ms):
        if v is None:
            e = [plen]
            v = plen
            tot = plen * ms[plen]
            similar = ms[plen]
        elif plen < (v * TOLER_MAX):
            e.append(plen)
            tot += (plen * ms[plen])
            similar += ms[plen]
        else:
            v = int(round(tot / float(similar)))
            for i in e:
                ms[i] = v
            e = [plen]
            v = plen
            tot = plen * ms[plen]
            similar = ms[plen]
    v = int(round(tot / float(similar)))
    for i in e:
        ms[i] = v
    if VERBOSE:
        print("t_m_s B", ms)
    for rec in records:
        rl = len(records[rec])
        for i in range(base, rl, 2):
            records[rec][i] = ms[records[rec][i]]


def backup(f):
    try:
        os.rename(os.path.realpath(f) + ".bak1", os.path.realpath(f) + ".bak2")
    except FileNotFoundError:
        pass
    try:
        os.rename(os.path.realpath(f) + ".bak", os.path.realpath(f) + ".bak1")
    except FileNotFoundError:
        pass
    try:
        os.rename(os.path.realpath(f), os.path.realpath(f) + ".bak")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        exit(0)

    try:
        f = open(FILE, "r")
        records = json.load(f)
        f.close()
    except FileNotFoundError:
        records = {}

    pi.set_mode(GPIO, pigpio.INPUT)
    pi.set_glitch_filter(GPIO, GLITCH)
    cb = pi.callback(GPIO, pigpio.EITHER_EDGE, cbf)

    print("Recording")
    print(f"Press key for '{ID}'")
    code = []
    fetching_code = True

    while fetching_code:
        time.sleep(0.1)
    print("Okay")
    time.sleep(0.5)

    if CONFIRM:
        press_1 = code[:]
        done = False
        tries = 0

        while not done:
            print(f"Press key for '{ID}' to confirm")
            code = []
            fetching_code = True

            while fetching_code:
                time.sleep(0.1)
            press_2 = code[:]
            the_same = compare(press_1, press_2)

            if the_same:
                done = True
                records[ID] = press_1[:]
                print("Okay")
                time.sleep(0.5)
            else:
                tries += 1
                if tries <= 3:
                    print("No match")
                else:
                    print(f"Giving up on key '{ID}'")
                    done = True
                time.sleep(0.5)
    else:
        records[ID] = code[:]

    pi.set_glitch_filter(GPIO, 0)
    pi.set_watchdog(GPIO, 0)

    tidy(records)
    backup(FILE)
    f = open(FILE, "w")
    f.write(json.dumps(records, sort_keys=True).replace("],", "],\n") + "\n")
    f.close()

    pi.stop()
