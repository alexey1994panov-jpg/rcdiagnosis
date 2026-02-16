from station.station_capabilities import RC_CAPABILITIES
from station.station_config import NODES
from station.station_rc_sections import RC_SECTIONS

endpoints = ["РќРџ", "РќР”Рџ", "Р§Рџ", "Р§Р”Рџ"]
to_id = {v['name']: k for k, v in NODES.items() if v.get('name') in endpoints}

print(f"Check endpoints: {to_id}")

for name, rc_id in to_id.items():
    cap = RC_CAPABILITIES.get(rc_id, {})
    can_lock = cap.get('can_lock')
    
    # Get neighbors from RC_SECTIONS
    sec_data = RC_SECTIONS.get(name, {})
    prev_name = sec_data.get("PrevSec")
    next_name = sec_data.get("NextSec")
    
    print(f"\nRC {name} ({rc_id}): can_lock={can_lock}")
    
    for neigh_name in [prev_name, next_name]:
        if not neigh_name: continue
        neigh_id = next((k for k, v in NODES.items() if v.get('name') == neigh_name), None)
        if neigh_id:
            neigh_cap = RC_CAPABILITIES.get(neigh_id, {})
            n_can_lock = neigh_cap.get('can_lock')
            print(f"  Neighbor {neigh_name} ({neigh_id}): can_lock={n_can_lock}")

