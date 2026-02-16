from __future__ import annotations

from typing import Any, Dict, List

from api.sim.schemas import ScenarioIn, TimelineStepOut
from api.services.simulate_service import simulate_scenario
from fastapi import FastAPI


def register_routes(app: FastAPI, ctx: Dict[str, Any]) -> None:
    @app.post("/simulate", response_model=List[TimelineStepOut])
    def simulate_endpoint(scenario: ScenarioIn) -> List[TimelineStepOut]:
        return simulate_scenario(
            scenario,
            default_options=ctx["DEFAULT_OPTIONS"],
            canonicalize_options=ctx["_canonicalize_options"],
            resolve_rc_id=ctx["_resolve_rc_id"],
            build_detectors_config=ctx["_build_detectors_config"],
            to_float=ctx["_to_float"],
            convert_rc_states=ctx["_convert_rc_states"],
            convert_switch_states=ctx["_convert_switch_states"],
            convert_signal_states=ctx["_convert_signal_states"],
            run_simulation_contract=ctx["run_simulation_contract"],
            parse_flag=ctx["_parse_flag"],
            states_ids_to_names=ctx["_states_ids_to_names"],
            id_to_name=ctx["ID_TO_NAME"],
        )
