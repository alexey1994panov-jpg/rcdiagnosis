# -*- coding: utf-8 -*-
# build_switch_logic.py — полная логика всех РЦ

from station_rc_sections import RC_SECTIONS
from station_config import NODES

SWITCH_LOGIC = {}

def build_stem(switches):
    """Строит ствол стрелок."""
    if not switches:
        return []
    
    graph = {sw['name']: sw for sw in switches}
    stem = []
    current = next((sw['name'] for sw in switches if sw['PrevSw'] is None), switches[0]['name'])
    
    while current and current not in stem:
        stem.append(current)
        next_sw = graph[current].get('NextSwPl') or graph[current].get('NextSwMi')
        if not next_sw:
            break
        current = next_sw
    
    return stem

def collect_adjacent(switches):
    """Собирает примыкающие РЦ."""
    plus_rc = set()
    minus_rc = set()
    for sw in switches:
        if sw['NextPl']:
            plus_rc.add(sw['NextPl'])
        if sw['NextMi']:
            minus_rc.add(sw['NextMi'])
    return sorted(plus_rc), sorted(minus_rc)

# Строим полную логику
for rc_name, rc_data in RC_SECTIONS.items():
    switches = rc_data.get('Switches', [])
    stem = build_stem(switches)
    plus_rc, minus_rc = collect_adjacent(switches)
    
    SWITCH_LOGIC[rc_name] = {
        'PrevSec': rc_data.get('PrevSec'),
        'NextSec': rc_data.get('NextSec'),
        'stem': stem,
        'plus_rc': plus_rc,
        'minus_rc': minus_rc,
    }

if __name__ == '__main__':
    import pprint
    print("=== ПОЛНЫЙ SWITCH_LOGIC ===")
    pprint.pprint(SWITCH_LOGIC, width=100, sort_dicts=False)
    
    import pathlib
    out_path = pathlib.Path(__file__).with_name('station_switch_logic.py')
    out_path.write_text(
        '# -*- coding: utf-8 -*-\n' +
        'SWITCH_LOGIC = ' + pprint.pformat(SWITCH_LOGIC, width=120, sort_dicts=False),
        encoding='utf-8'
    )
    print(f"\n✅ Сохранено: {out_path}")
    print("\n📋 Примеры:")
    for rc_name in ['1-7СП', '1П', '10-12СП']:
        print(f"{rc_name}: {SWITCH_LOGIC[rc_name]}")
