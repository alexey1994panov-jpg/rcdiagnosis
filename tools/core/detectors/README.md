# Detectors Submodules

Этот каталог содержит выделенные части движка детекторов.

- `types.py`: dataclass-структуры `DetectorsConfig`, `DetectorsState`, `DetectorsResult`.
- `phase_exceptions.py`: централизованная фазовая навеска исключений (`MU`, `recent LS`, `DSP`) на детекторы.

Назначение:
- уменьшить размер `tools/core/detectors_engine.py`;
- упростить чтение и поддержку без изменения логики детекторов.
