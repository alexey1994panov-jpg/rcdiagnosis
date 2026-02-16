from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse


def register_routes(app: FastAPI, ctx: Dict[str, Any]) -> None:
    frontend_dir = ctx["FRONTEND_DIR"]
    exceptions_config_path = ctx["EXCEPTIONS_CONFIG_PATH"]
    api_build = ctx["API_BUILD"]
    default_options = ctx["DEFAULT_OPTIONS"]
    canonicalize_options = ctx["_canonicalize_options"]
    legacy_to_canonical = ctx["LEGACY_TO_CANONICAL_OPTION_KEYS"]

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        index_path = frontend_dir / "index.html"
        if not index_path.exists():
            return HTMLResponse("index.html not found", status_code=500)
        return HTMLResponse(index_path.read_text(encoding="utf-8"))

    @app.get("/defaults")
    def get_defaults() -> Dict[str, Any]:
        options = canonicalize_options(dict(default_options))
        canonical_keys = set(legacy_to_canonical.values())
        passthrough_keys = {
            "t_pk",
            "sig_lz4_prev_to_ctrl",
            "sig_lz4_ctrl_to_next",
            "sig_lz10_to_next",
            "sig_lz10_to_prev",
            "sig_lz11_a",
            "sig_lz11_b",
            "sig_lz13_prev",
            "sig_lz13_next",
            "sig_ls6_prev",
            "t_mu",
            "t_recent_ls",
            "t_min_maneuver_v8",
            "t_ls_mu",
            "t_ls_after_lz",
            "t_ls_dsp",
            "enable_lz_exc_mu",
            "enable_lz_exc_recent_ls",
            "enable_lz_exc_dsp",
            "lz_exc_dsp_variants",
            "enable_ls_exc_mu",
            "enable_ls_exc_after_lz",
            "enable_ls_exc_dsp",
            "enable_ls1",
            "enable_ls2",
            "enable_ls4",
            "enable_ls5",
            "enable_ls6",
            "enable_ls9",
        }
        out: Dict[str, Any] = {}
        for k, v in options.items():
            if k in canonical_keys or k in passthrough_keys:
                out[k] = v
        return out

    @app.get("/health")
    def get_health() -> Dict[str, Any]:
        return {"status": "ok", "api_build": api_build}

    @app.get("/exceptions-config")
    def get_exceptions_config() -> Dict[str, Any]:
        if not exceptions_config_path.exists():
            return {"version": 1, "objects": []}
        try:
            return json.loads(exceptions_config_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Cannot read exceptions config: {exc}")

    @app.put("/exceptions-config")
    def put_exceptions_config(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Payload must be a JSON object")
        if "objects" in payload and not isinstance(payload.get("objects"), list):
            raise HTTPException(status_code=400, detail="'objects' must be a list")
        try:
            exceptions_config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Cannot save exceptions config: {exc}")
        return {"status": "ok", "path": str(exceptions_config_path)}
