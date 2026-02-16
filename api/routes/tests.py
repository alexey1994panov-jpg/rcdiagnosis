from __future__ import annotations

from typing import Any, Dict, List

from api.services.tests_service import (
    delete_test_record,
    get_test_record,
    list_test_records,
    save_test_record,
    update_test_status_record,
)
from fastapi import FastAPI


def register_routes(app: FastAPI, ctx: Dict[str, Any]) -> None:
    tests_dir = ctx["TESTS_DIR"]
    fix_mojibake = ctx["_fix_mojibake"]

    @app.get("/tests")
    def list_tests() -> List[Dict[str, Any]]:
        return list_test_records(tests_dir=tests_dir, fix_mojibake=fix_mojibake)

    @app.get("/tests/{test_id}")
    def get_test(test_id: str) -> Dict[str, Any]:
        return get_test_record(test_id, tests_dir=tests_dir, fix_mojibake=fix_mojibake)

    @app.post("/tests")
    def save_test(test_data: Dict[str, Any]) -> Dict[str, str]:
        return save_test_record(test_data, tests_dir=tests_dir)

    @app.post("/tests/{test_id}/status")
    def update_test_status(test_id: str, status_data: Dict[str, Any]) -> Dict[str, str]:
        return update_test_status_record(test_id, status_data, tests_dir=tests_dir)

    @app.delete("/tests/{test_id}")
    def delete_test(test_id: str) -> Dict[str, str]:
        return delete_test_record(test_id, tests_dir=tests_dir)
