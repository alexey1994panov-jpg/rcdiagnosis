from typing import Dict

from api_contract.api_schema import MetadataDTO
from core.variants_common import mask_to_string


def _build_variant_labels() -> Dict[str, str]:
    return {
        "1": "LZ1",
        "2": "LZ2",
        "3": "LZ3",
        "4": "LZ4",
        "5": "LZ5",
        "6": "LZ6",
        "7": "LZ7",
        "8": "LZ8",
        "9": "LZ9",
        "10": "LZ10",
        "11": "LZ11",
        "12": "LZ12",
        "13": "LZ13",
        "101": "LS1",
        "102": "LS2",
        "104": "LS4",
        "105": "LS5",
        "106": "LS6",
        "109": "LS9",
    }


def _build_flag_labels() -> Dict[str, str]:
    labels: Dict[str, str] = {
        "false_lz": "False occupancy while RC is free",
        "no_lz_when_occupied": "No occupancy flag while RC is occupied",
    }

    for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
        labels[f"llz_v{n}"] = f"LZ{n} active"
        labels[f"llz_v{n}_open"] = f"LZ{n} open"
        labels[f"llz_v{n}_closed"] = f"LZ{n} closed"

    for n in [1, 2, 4, 5, 6, 9]:
        labels[f"lls_{n}"] = f"LS{n} active"
        labels[f"lls_{n}_open"] = f"LS{n} open"
        labels[f"lls_{n}_closed"] = f"LS{n} closed"

    return labels


def _build_mask_labels() -> Dict[int, str]:
    masks: Dict[int, str] = {}
    ranges = [
        range(1, 200),
        range(200, 230),
        range(500, 540),
        range(600, 620),
        range(900, 940),
        range(1000, 1110),
        range(1300, 1310),
        range(1600, 1610),
    ]
    for r in ranges:
        for mask_id in r:
            name = mask_to_string(mask_id)
            if not name.startswith("UNKNOWN("):
                masks[int(mask_id)] = name
    return masks


def get_metadata_dto() -> MetadataDTO:
    return MetadataDTO(
        variants=_build_variant_labels(),
        flags=_build_flag_labels(),
        masks=_build_mask_labels(),
    )


