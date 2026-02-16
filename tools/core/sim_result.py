from __future__ import annotations

from typing import Dict

from core.sim_types import TimelineStep


class SingleResultWrapper:
    def __init__(self, step: TimelineStep, dict_view: Dict[str, TimelineStep]):
        # Keep explicit attributes for strict backward compatibility.
        self._step = step
        self._dict = dict_view

        self.t = step.t
        self.step_duration = step.step_duration
        self.ctrl_rc_id = step.ctrl_rc_id
        self.effective_prev_rc = step.effective_prev_rc
        self.effective_next_rc = step.effective_next_rc
        self.rc_states = step.rc_states
        self.switch_states = step.switch_states
        self.signal_states = step.signal_states
        self.modes = step.modes
        self.lz_state = step.lz_state
        self.lz_variant = step.lz_variant
        self.flags = step.flags

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self._dict.values())[key]
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def __iter__(self):
        return iter(self._dict)

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def __repr__(self):
        return f"TimelineStep({self.ctrl_rc_id}, t={self.t}, lz={self.lz_state}, flags={self.flags})"
