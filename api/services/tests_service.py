from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import HTTPException


def list_test_records(*, tests_dir: Path, fix_mojibake: Any) -> List[Dict[str, Any]]:
    tests: List[Dict[str, Any]] = []
    for test_file in sorted(tests_dir.glob("*.json")):
        try:
            data = json.loads(test_file.read_text(encoding="utf-8"))
        except Exception:
            tests.append(
                {
                    "id": test_file.stem,
                    "name": f"{test_file.stem} (INVALID JSON)",
                    "variant": None,
                    "direction": None,
                    "lastStatus": "unknown",
                    "comment": "",
                }
            )
            continue
        test_id = data.get("id") or test_file.stem
        display_name = fix_mojibake(str(data.get("name") or test_file.stem))
        tests.append(
            {
                "id": test_id,
                "name": display_name,
                "variant": data.get("variant"),
                "direction": data.get("direction"),
                "lastStatus": data.get("lastStatus", "unknown"),
                "comment": fix_mojibake(str(data.get("comment", ""))),
            }
        )
    return tests


def get_test_record(test_id: str, *, tests_dir: Path, fix_mojibake: Any) -> Dict[str, Any]:
    test_path = tests_dir / f"{test_id}.json"
    if not test_path.exists():
        raise HTTPException(status_code=404, detail="Test not found")
    try:
        data = json.loads(test_path.read_text(encoding="utf-8"))
    except Exception:
        raise HTTPException(status_code=500, detail="Cannot read test file")
    data.setdefault("id", test_id)
    if isinstance(data.get("name"), str):
        data["name"] = fix_mojibake(data["name"])
    if isinstance(data.get("comment"), str):
        data["comment"] = fix_mojibake(data["comment"])
    return data


def save_test_record(test_data: Dict[str, Any], *, tests_dir: Path) -> Dict[str, str]:
    test_id = test_data.get("id")
    if not test_id:
        test_id = f"test_{int(datetime.now().timestamp())}"
        test_data["id"] = test_id
    test_path = tests_dir / f"{test_id}.json"
    test_path.write_text(json.dumps(test_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": str(test_id)}


def update_test_status_record(test_id: str, status_data: Dict[str, Any], *, tests_dir: Path) -> Dict[str, str]:
    test_path = tests_dir / f"{test_id}.json"
    if not test_path.exists():
        raise HTTPException(status_code=404, detail="Test not found")
    data = json.loads(test_path.read_text(encoding="utf-8"))
    status = status_data.get("status")
    if status is not None:
        data["lastStatus"] = status
    if "comment" in status_data:
        data["comment"] = status_data["comment"]
    test_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "updated"}


def delete_test_record(test_id: str, *, tests_dir: Path) -> Dict[str, str]:
    test_path = tests_dir / f"{test_id}.json"
    if not test_path.exists():
        raise HTTPException(status_code=404, detail="Test not found")
    try:
        os.remove(test_path)
    except OSError:
        raise HTTPException(status_code=500, detail="Cannot delete test file")
    return {"status": "deleted", "id": test_id}
