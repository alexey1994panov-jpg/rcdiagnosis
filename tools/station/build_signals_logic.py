# -*- coding: utf-8 -*-
# build_signals_logic.py вЂ” РІСЃРµ СЃРІРµС‚РѕС„РѕСЂС‹ (РјР°РЅРµРІСЂРѕРІС‹Рµ + РїСѓС‚РµРІС‹Рµ/РїРѕР·РґРЅРёРµ)

from station.station_config import NODES


SIGNALS_LOGIC = {}


def get_sec_name(sec_name: str) -> str | None:
    """
    sec_name -> РёРјСЏ СЃРµРєС†РёРё (Р Р¦), РµСЃР»Рё РµСЃС‚СЊ С‚Р°РєРѕР№ СѓР·РµР» СЃ type == 1 Рё name == sec_name.
    Р’РѕР·РІСЂР°С‰Р°РµС‚ sec_name, РёРЅР°С‡Рµ None.
    """
    for node in NODES.values():
        if node.get("type") == 1 and node.get("name") == sec_name:
            return sec_name
    return None


for node_id, node_data in NODES.items():
    node_type = node_data.get("type")
    name = node_data.get("name", "")

    # РёРЅС‚РµСЂРµСЃСѓСЋС‚ С‚РѕР»СЊРєРѕ СЃРІРµС‚РѕС„РѕСЂС‹
    if node_type not in (3, 4):
        continue

    # Р·РґРµСЃСЊ Р»РµР¶Р°С‚ РРњР•РќРђ Р Р¦, Р° РЅРµ ID
    prev_names = node_data.get("prev_links") or []
    next_names = node_data.get("next_links") or []

    prev_sec = None
    next_sec = None

    # Р±РµСЂС‘Рј РїРµСЂРІСѓСЋ РІР°Р»РёРґРЅСѓСЋ СЃРµРєС†РёСЋ РёР· prev_links
    for pname in prev_names:
        sec = get_sec_name(pname)
        if sec is not None:
            prev_sec = sec
            break

    # Р±РµСЂС‘Рј РїРµСЂРІСѓСЋ РІР°Р»РёРґРЅСѓСЋ СЃРµРєС†РёСЋ РёР· next_links
    for nname in next_names:
        sec = get_sec_name(nname)
        if sec is not None:
            next_sec = sec
            break

    sig_type = "SIG" if node_type == 3 else "LATE_SIG"

    SIGNALS_LOGIC[name] = {
        "type": sig_type,
        "node_id": node_id,
        "PrevSec": prev_sec,
        "NextSec": next_sec,
    }


if __name__ == "__main__":
    import pprint
    import pathlib

    print("=== SIGNALS_LOGIC (РјР°РЅРµРІСЂРѕРІС‹Рµ + РїСѓС‚РµРІС‹Рµ) ===")
    pprint.pprint(SIGNALS_LOGIC, width=100, sort_dicts=False)

    out_path = pathlib.Path(__file__).with_name("station_signals_logic.py")
    out_path.write_text(
        "# -*- coding: utf-8 -*-\n"
        "SIGNALS_LOGIC = "
        + pprint.pformat(SIGNALS_LOGIC, width=120, sort_dicts=False),
        encoding="utf-8",
    )
    print(f"\nРЎРѕС…СЂР°РЅРµРЅРѕ: {out_path}")
    print(f"\nРќР°Р№РґРµРЅРѕ СЃРІРµС‚РѕС„РѕСЂРѕРІ: {len(SIGNALS_LOGIC)}")

