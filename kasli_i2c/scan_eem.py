from kasli_i2c.chips import EEPROM
from kasli_i2c.kasli import Kasli
from kasli_i2c.sinara import Sinara


def scan_eem(bus):
    ports = filter(lambda x: x.startswith("EEM"), bus.ports)
    ports = sorted(ports, key=lambda x: int(x[3:]))

    eeprom = EEPROM(bus, addr=0x57)

    for port in ports:
        bus.enable(port)
        active_addrs = bus.scan()
        if eeprom.addr in active_addrs:
            try:
                bd = Sinara.unpack(eeprom.dump())
                print(f"{port}: {bd.name} v{bd.major}.{bd.minor} ({Sinara.vendors[bd.vendor]} / {bd.eui48_fmt})")
            except ValueError:
                print(f"{port}: Unrecognized device")


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("-s", "--serial", default="0")
    # port 2 for Kasli v1.1
    # port 3 for Kasli v1.0
    p.add_argument("-p", "--port", default=2, type=int)
    # EEM1 (port 5) SDA shorted on Kasli-v1.0-2
    p.add_argument("-k", "--skip", action="append", default=[])

    args = p.parse_args()

    url = "ftdi://ftdi:4232h:{}/{}".format(args.serial, args.port)
    with Kasli().configure(url) as bus:
        bus.skip = args.skip
        bus.reset()
        try:
            scan_eem(bus)
        finally:
            bus.enable()
