import logging
from typing import Dict, Any, List
from malduck import base64
from malduck import procmem
from malduck.extractor import Extractor

log = logging.getLogger(__name__)


def read_wide_dotnet_strings(p: procmem, str_count: int, start_addr: int) -> List[str]:
    str_list = []
    while len(str_list) != str_count:
        string_len = p.uint8v(start_addr)
        start_addr += 1
        str_data = p.readv(start_addr, string_len)
        for ch in [b"\x00", b"\x01"]:
            str_data = str_data.replace(ch, b"")

        string = str_data.decode("utf-8")
        start_addr += string_len
        str_list.append(string)

    return str_list


class Njrat(Extractor):
    yara_rules = ("win_njrat",)
    family = "njrat"

    @Extractor.extractor
    def op_config_07d(self, p: procmem, match: int) -> Dict[str, Any]:
        # Skip to the config address by adding number of bytes
        # in the op_config.
        start_addr = match + 17
        str_list = read_wide_dotnet_strings(p, 8, start_addr)

        str_list[0] = base64.decode(str_list[0])
        config = {
            "id": str_list[0],
            "version": str_list[1],
            "filename": str_list[2],
            "directory": str_list[3],
            "registry": str_list[4],
            "cncs": [{"host": str_list[5], "port": str_list[6]}],
            "registry_key": str_list[7],
        }

        return config

    @Extractor.extractor
    def op_config_07d_indirect(self, p: procmem, match: int) -> Dict[str, Any]:
        start_addr = match - 1
        str_list = read_wide_dotnet_strings(p, 9, start_addr)
        (
            directory,
            filename,
            c2,
            _,
            port,
            registry_key,
            registry,
            _id,
            version,
        ) = str_list

        c2s = None
        if c2.startswith("http"):
            c2s = [{"url": c2}]
        else:
            c2s = [{"host": c2, "port": port}]

        config = {
            "id": _id,
            "version": version,
            "filename": filename[::-1],
            "directory": directory,
            "registry": registry,
            "cncs": c2s,
            "registry_key": registry_key,
        }

        return config

    @Extractor.extractor
    def op_config_07nc(self, p: procmem, match: int) -> Dict[str, Any]:
        # Skip to the config address by adding number of bytes
        # in the op_config.
        start_addr = match + 11
        str_list = read_wide_dotnet_strings(p, 6, start_addr)

        if str_list[1] and not str_list[1].isdigit():
            log.warning("Fetched port is not a number")
            return

        str_list[4] = base64.decode(str_list[4])
        config = {
            "id": str_list[4],
            "version": str_list[5],
            "registry": str_list[2],
            "cncs": [{"host": str_list[0], "port": str_list[1]}],
        }

        return config
