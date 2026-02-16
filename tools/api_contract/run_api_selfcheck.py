"""
Run API self-check without pytest.

Usage:
    python tools/run_api_selfcheck.py
"""

import sys


def main() -> int:
    # Local import to keep script standalone and explicit.
    from test_api_contract import (
        test_api_metadata_contract,
        test_api_run_simulation_single_rc_contract,
    )

    try:
        test_api_run_simulation_single_rc_contract()
        test_api_metadata_contract()
    except Exception as exc:  # pragma: no cover - operational script
        print(f"api_selfcheck_failed: {exc}")
        return 1

    print("api_selfcheck_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

