from typing import Any, Optional, Tuple
from base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from base_wrapper import BaseVariantWrapper
from variants_common import mask_ctrl_free, mask_ctrl_occupied, _is_signal_open, _is_locked, rc_is_occupied, rc_is_free

MASK_LS6_P01 = 1600
MASK_LS6_KOGDA = 1601

def _make_ls6_branch(
    ctrl_rc_id: str,
    prev_rc_id: Optional[str],
    next_rc_id: Optional[str],
    other_side_nc_flag: str, # "prev" or "next"
    sig_id: str,
    ts01_ls6: float,
    tlz_ls6: float,
    tkon_ls6: float,
    branch_type: str, # "6.1" or "6.2"
) -> BaseDetector:
    
    def mask_ls6_p0_nc_wait_open(step, prev, ctrl, nxt) -> bool:
        # ДАНО: 
        # 6.1 (prev NC): prev NC, curr free+locked, next free+locked, sig_prev_to_ctrl open
        # 6.2 (next NC): prev free+locked, curr free+locked, next NC, sig_prev_to_ctrl open
        
        nc_side = step.modes.get(f"{other_side_nc_flag}_nc", False)
        
        # ctrl — это аргумент 'ctrl', который пришел в маску (ID)
        s_ctrl = step.rc_states.get(ctrl, 0)
        curr_free = rc_is_free(s_ctrl)
        curr_locked = _is_locked(step, ctrl)
        
        # В 6.1 NC слева (prev), контролируем соседа справа (nxt)
        # В 6.2 NC справа (nxt), контролируем соседа слева (prev)
        adj_id = nxt if branch_type == "6.1" else prev
        
        adj_free = False
        adj_locked = False
        if adj_id:
            s_adj = step.rc_states.get(adj_id, 0)
            adj_free = rc_is_free(s_adj)
            adj_locked = _is_locked(step, adj_id)
            
        sig_open = _is_signal_open(step, sig_id)
        
        res = nc_side and curr_free and curr_locked and adj_free and adj_locked and sig_open
        
        if not res and (nc_side or curr_free or adj_free):
            print(f"DEBUG LS6 P01 ({branch_type}) for {ctrl}: nc={nc_side}, curr_f={curr_free}, curr_l={curr_locked}, adj_id={adj_id}, adj_f={adj_free}, adj_l={adj_locked}, sig_o={sig_open} -> {res}")
            
        return res
        
    def mask_ls6_p1_wait_occ(step, prev, ctrl, nxt) -> bool:
        # КОГДА:
        # 6.1: prev NC, curr free+locked, next occ+locked
        # 6.2: prev occ+locked, curr free+locked, next NC
        
        nc_side = step.modes.get(f"{other_side_nc_flag}_nc", False)

        s_ctrl = step.rc_states.get(ctrl, 0)
        curr_free = rc_is_free(s_ctrl)
        curr_locked = _is_locked(step, ctrl)

        adj_id = nxt if branch_type == "6.1" else prev
        adj_occ = False
        adj_locked = False
        if adj_id:
            s_adj = step.rc_states.get(adj_id, 0)
            adj_occ = rc_is_occupied(s_adj)
            adj_locked = _is_locked(step, adj_id)
            
        res = nc_side and curr_free and curr_locked and adj_occ and adj_locked
        
        if not res and (nc_side or curr_free or adj_occ):
             print(f"DEBUG LS6 KOGDA ({branch_type}) for {ctrl}: nc={nc_side}, curr_f={curr_free}, curr_l={curr_locked}, adj_id={adj_id}, adj_o={adj_occ}, adj_l={adj_locked} -> {res}")

        return res

    phases = [
        PhaseConfig(0, float(ts01_ls6), 1, reset_on_exit=True, mask_id=MASK_LS6_P01, mask_fn=mask_ls6_p0_nc_wait_open, requires_neighbors=NeighborRequirement.ONE_NC),
        PhaseConfig(1, float(tlz_ls6), -1, reset_on_exit=True, mask_id=MASK_LS6_KOGDA, mask_fn=mask_ls6_p1_wait_occ, requires_neighbors=NeighborRequirement.ONE_NC),
    ]
    
    config = DetectorConfig(0, phases, float(tkon_ls6), CompletionMode.OCCUPIED_TIME, variant_name=f"ls6_{branch_type}")
    return BaseDetector(config, prev_rc_name=prev_rc_id, ctrl_rc_name=ctrl_rc_id, next_rc_name=next_rc_id)

def make_ls6_detector(
    ctrl_rc_id: str,
    prev_rc_id: Optional[str],
    next_rc_id: Optional[str],
    sig_prev: Optional[str],
    ts01_ls6: float,
    tlz_ls6: float,
    tkon_ls6: float,
) -> Any:
    detectors = []
    # Теперь мы создаем детекторы, если задан СИГНАЛ.
    # Динамическая топология сама найдет соседа (prev или next) во время симуляции.
    if sig_prev:
        # Ветка 6.1: вход со стороны prev (NC на prev), детекция на next
        detectors.append(_make_ls6_branch(ctrl_rc_id, prev_rc_id, next_rc_id, "prev", sig_prev, ts01_ls6, tlz_ls6, tkon_ls6, "6.1"))
        # Ветка 6.2: вход со стороны next (NC на next), детекция на prev
        detectors.append(_make_ls6_branch(ctrl_rc_id, prev_rc_id, next_rc_id, "next", sig_prev, ts01_ls6, tlz_ls6, tkon_ls6, "6.2"))
    
    if not detectors:
        return None
    if len(detectors) == 1:
        return detectors[0]
    return BaseVariantWrapper(detectors)
