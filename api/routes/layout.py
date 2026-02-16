from __future__ import annotations

from typing import Any, Dict, List

from api.services.layout_service import build_node_catalog, build_station_layout_response
from fastapi import FastAPI


def register_routes(app: FastAPI, ctx: Dict[str, Any]) -> None:
    xml_dir = ctx["XML_DIR"]
    layout_cache = ctx["_LAYOUT_CACHE"]
    api_build = ctx["API_BUILD"]
    build_station_layout = ctx["build_station_layout"]
    fix_mojibake = ctx["_fix_mojibake"]
    nodes = ctx["NODES"]
    rc_sections = ctx["RC_SECTIONS"]

    @app.get("/station-layout")
    def get_station_layout(station: str = "Visochino") -> Dict[str, Any]:
        return build_station_layout_response(
            station,
            xml_dir=xml_dir,
            layout_cache=layout_cache,
            api_build=api_build,
            build_station_layout=build_station_layout,
            fix_mojibake=fix_mojibake,
            nodes=nodes,
            rc_sections=rc_sections,
        )

    @app.get("/node-catalog")
    def get_node_catalog() -> Dict[str, Any]:
        return build_node_catalog(nodes=nodes, fix_mojibake=fix_mojibake)
