import logging
import sys
import json
import datetime
from collections import OrderedDict
import socket
# OrderedDict = dict

from sinara import Sinara
from kasli import Kasli
from chips import EEPROM
from label import render_zpl

logger = logging.getLogger(__name__)


__vendor__ = "QUARTIQ"

today = datetime.date.today().isoformat()


def get_kasli(description):
    target = description["target"].capitalize()
    v = Sinara.parse_hw_rev(description["hw_rev"])
    port = 0
    if "eui48" in description:
        eui48 = Sinara.parse_eui48(description["eui48"][port])
    else:
        eui48 = Sinara._defaults.eui48
    ee = [Sinara(
        name=target,
        board=Sinara.boards.index(target),
        major=v[0],
        minor=v[1],
        variant=description.get("hw_variant", 0),
        port=port,
        eui48=eui48,
        vendor=Sinara.vendors.index(description["vendor"]))]
    return ee


def get_eem(description):
    v = Sinara.parse_hw_rev(description["hw_rev"])
    name = description.get("board", description["type"].capitalize())
    if "variant" in description:
        variant = Sinara.variants.get(name, [None]).index(
            description["variant"])
    else:
        variant = 0
    if "eui48" in description:
        eui48 = [Sinara.parse_eui48(_) for _ in description["eui48"]]
    else:
        eui48 = [Sinara._defaults.eui48]*len(description["ports"])
    return [Sinara(
        name=name,
        board=Sinara.boards.index(name),
        major=v[0],
        minor=v[1],
        variant=variant,
        port=port,
        eui48=eui48[port],
        vendor=Sinara.vendors.index(__vendor__))
        for port in range(len(description["ports"]))]


def get_sinara_label(s):
    assert s.vendor_fmt == __vendor__
    return """
^XA
^LH20,10^CFA
^FO0,10^FB140,4^FD{s.name_fmt}\&{s.description}\&{s.eui48_fmt}^FS
^FO0,55^FB140,3^FDQUARTIQ GmbH\&Rudower Chaussee 29\&12489 Berlin, Germany^FS
^FO0,90^FB220,2^FD{s.url}\&{s.license} - {date}^FS
^FO140,0^BQN,2,2^FDQA,https://qr.quartiq.de/sinara/{s.eui48_fmt}^FS
^XZ""".format(s=s, date=today)


def flash(description, ss, ft_serial=None):
    ss_new = []
    url = "ftdi://ftdi:4232h{}/2".format(
            ":" + ft_serial if ft_serial is not None else "")
    with Kasli().configure(url) as bus:
        # bus.reset()
        ee = EEPROM(bus)
        try:
            for i, s in enumerate(ss):
                ss_new.append([])
                for j, si in enumerate(s):
                    if i == 0:
                        port = "LOC0"
                    else:
                        port = "EEM{:d}".format(
                            description["peripherals"][i - 1]["ports"][j])
                    bus.enable(port)  # TODO: Banker, Humpback switch
                    eui48 = ee.eui48()
                    if si.eui48 not in (eui48, si._defaults.eui48):
                        logger.warning("eui48 mismatch, %s->%s", si.eui48, eui48)
                    new = si._replace(eui48=eui48)
                    skip = False
                    try:
                        old = Sinara.unpack(ee.dump())
                        logger.debug("valid data %s", old)
                        new = new._replace(
                            project_data=old.project_data,
                            board_data=old.board_data,
                            user_data=old.user_data
                        )
                        if old != new:
                            old_dict = old._asdict()
                            new_dict = new._asdict()
                            logger.info("change data: %s", ", ".join(
                                "{}: {}->{}".format(
                                    k, old_dict[k], new_dict[k])
                                for k in old._fields))
                        else:
                            skip = True
                    except:
                        logger.debug("invalid data")
                    ss_new[-1].append(new)
                    if not skip:
                        ee.write(0, new.pack()[:128])
                        data = ee.dump()
                        try:
                            Sinara.unpack(data)
                            logger.debug("data readback valid")
                        except:
                            logger.error("data readback invalid %r",
                                         data, exc_info=True)
                    open("data/{}.bin".format(new.eui48_fmt), "wb"
                         ).write(new.pack())

        finally:
            bus.enable()
    return ss_new


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser()
    p.add_argument("-p", "--printer", type=str, default=None)
    p.add_argument("-u", "--update", action="store_true")
    p.add_argument("-s", "--serial", type=str, default=None)
    p.add_argument("description")
    args = p.parse_args()

    with open(args.description) as f:
        description = json.load(f, object_pairs_hook=OrderedDict)
    assert description["vendor"] == __vendor__

    ss = [get_kasli(description)]
    ss.extend(get_eem(p) for p in description["peripherals"])
    if args.update:
        ss = flash(description, ss, args.serial)
        description["eui48"] = [s.eui48_fmt for s in ss[0]]
        for i, s in enumerate(ss[1:]):
            description["peripherals"][i]["eui48"] = [si.eui48_fmt for si in s]
        with open("meta/{}.json".format(ss[0][0].eui48_fmt), "w") as f:
            f.write(json.dumps(description, indent=4))

    labels = [get_sinara_label(s[0]) for s in ss]
    labels.insert(0, labels[0])  # repeat first
    with open("labels/{}.zpl".format(ss[0][0].eui48_fmt), "w") as f:
        f.write("\n".join(labels))
    if args.printer:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.printer, 9100))
        sock.sendall("\n".join(labels).encode())
    # open("labels/{}.png".format(s.eui48_fmt), "wb").write(render_zpl(z))