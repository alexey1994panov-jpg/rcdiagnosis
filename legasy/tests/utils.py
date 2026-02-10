# tests/utils.py
from typing import Iterable

def has_flag(flags: Iterable[str], name: str, rc: str | None = None) -> bool:
    """
    Унифицированная проверка флага.
    name: 'llz_v1', 'llz_v1_open', 'lls_v6_closed' и т.д.
    rc=None — флаг с любым rc, rc='1P' — конкретная РЦ.
    """
    if rc is None:
        prefix = name + ":rc="
        return any(f == name or f.startswith(prefix) for f in flags)
    return any(f == f"{name}:rc={rc}" for f in flags)
