import struct
import zlib
from collections import namedtuple

_SinaraTuple = namedtuple("Sinara", (
    "name",          # 10s, name of the board, human redable
    "board",         # H, board ID
    "data_rev",      # B, EEPROM data format revision
    "major",         # B, board major revision
    "minor",         # B, board minor revision
    "variant",       # B, board variant
    "port",          # B, board port
    "vendor",        # B, vendor id
    "vendor_data",   # 8s, vendor reserved: serial number/data
    "project_data",  # 16s, project reserved
    "user_data",     # 16s, user reserved
    "board_data",    # 64s, board data
    "eui48",         # 6s, EUI-48
))


class Sinara(_SinaraTuple):
    _defaults = _SinaraTuple(name="Unknown", board=0, data_rev=0,
                             major=0, minor=0, variant=0, port=0, vendor=0,
                             vendor_data=b"\xff"*8, project_data=b"\xff"*16,
                             user_data=b"\xff"*16, board_data=b"\xff"*64,
                             eui48=b"\xff"*6)
    _struct = struct.Struct(">I H 10s HBBBBBB 8s 16s 16s 64s 122s 6s")
    assert _struct.size == 256
    _magic = 0x391e
    _crc = zlib.crc32
    _pad = b"\xff" * 122

    boards = [
        "invalid",
        "VHDCI_Carrier",
        "Sayma_RTM",
        "Sayma_AMC",
        "Metlino",
        "Kasli",
        "DIO_BNC",
        "DIO_SMA",
        "DIO_RJ45",
        "Urukul",
        "Zotino",
        "Novogorny",
        "Sampler",
        "Grabber",
        "Mirny",
        "Banker",
        "Humpback",
        "Stabilizer",
        "Kasli-BP",
        # ...
    ]
    board_descriptions = {
        "Kasli": "8/12 EEM FPGA",
        "DIO_BNC": "8x iso BNC IO",
        "DIO_SMA": "8x iso SMA IO",
        "DIO_RJ45": "16x LVDS RJ45 IO",
        "Urukul": "4x 1GS/s DDS",
        "Zotino": "32x 1MS/s 16b DAC",
        "Novogorny": "8x 16b ADC",
        "Sampler": "8x 1.5MS/s 16b ADC",
        "Grabber": "CCD frame grabber",
        "Mirny": "4x 53-13600MHz PLL",
        "Banker": "128x IO+FPGA",
        "Humpback": "uC+FPGA carrier",
        "Stabilizer": "2x 16b ADC+DAC+uC",
        "Kasli_BP": "Kasli backplane adapter",
    }
    board_variants = {
        "Urukul": ["AD9910", "AD9912"],
        }

    vendors = [
        "invalid",
        "Technosystem",
        "Creotech",
        "QUARTIQ",
        # ...
    ]
    vendor_description = {
        "QUARTIQ": "QUARTIQ GmbH\nRudower Chaussee 29\n12489 Berlin, Germany",
    }

    def pack(self):
        name = self[0].encode()
        eui48 = self[-1]
        data = self._struct.pack(
            0, self._magic, name, *self[1:-1], self._pad, eui48)
        crc = struct.pack(">I", self._crc(data[4:]))
        data = crc + data[4:]
        assert len(data) == self._struct.size
        return data

    @classmethod
    def unpack(cls, data, check=True):
        crc, magic, *fields, pad, eui48 = cls._struct.unpack(data)
        if check:
            if magic != cls._magic:
                raise ValueError("Invalid magic")
            if pad != cls._pad:
                raise ValueError("Unexpected read-only pad data")
            if crc != cls._crc(data[4:]):
                raise ValueError("Invalid CRC")
        fields[0] = fields[0].strip(b"\x00").decode()
        return cls(*fields, eui48)


Sinara.__new__.__defaults__ = Sinara._defaults


if __name__ == "__main__":
    s = Sinara(name="DIO-BNC",
               board=Sinara.boards.index("DIO-BNC"),
               data_rev=Sinara.data_rev, major=1, minor=1, variant=0, port=0,
               vendor=Sinara.vendors.index("Technosystem"))
    print(s)
    print(s.pack())
    assert Sinara.unpack(s.pack()) == s
