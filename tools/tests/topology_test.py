from station.station_model import load_station_from_config
from core.topology_manager import UniversalTopologyManager
from station.station_config import NODES

def test_topology_no_switches():
    model = load_station_from_config()
    tm = UniversalTopologyManager(model)
    
    # РЎРµРєС†РёСЏ СЃРѕ СЃС‚СЂРµР»РєР°РјРё, РЅР°РїСЂРёРјРµСЂ 1-7СП (ID Р·Р°РІРёСЃРёС‚ РѕС‚ NODES, РЅР°Р№РґРµРј РїРѕ РёРјРµРЅРё)
    rc_id_17sp = next(k for k, v in NODES.items() if v.get('name') == '1-7СП')
    print(f"Testing RC {rc_id_17sp} (1-7СП)")
    node_17sp = model.rc_nodes[rc_id_17sp]
    print(f"  Next links: {node_17sp.next_links}")
    print(f"  Prev links: {node_17sp.prev_links}")
    
    prev, nxt = tm.get_active_neighbors(rc_id_17sp, {}, 0.0)
    print(f"  Resolved neighbors with EMPTY switch_states: prev={prev}, next={nxt}")
    
    if nxt == "":
        print("  SUCCESS: Bug fixed! Link to 81 is now switch-dependent.")
    else:
        print(f"  STILL BUGGY: next={nxt}")

if __name__ == "__main__":
    test_topology_no_switches()



