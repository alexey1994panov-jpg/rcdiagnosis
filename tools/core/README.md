# Core

Ядро симуляции и детекторов.

- `detectors_engine.py`: оркестрация вариантов ЛЗ/ЛС, обновление состояния и результат.
- `detectors/`: выделенные подмодули детекторов (типы и фазовые исключения).
- `sim_core.py`: основной цикл симуляции по шагам сценария.
- `sim_types.py`: типы симуляции (`ScenarioStep`, `TimelineStep`, `SimulationConfig`).
- `sim_result.py`: совместимая обертка результата для single-RC режима.
- `sim_runner.py`: прогон сценария (`SimulationContext.run`) с постобработкой исключений.
- `sim_step_runner.py`: подшаговая обработка одной РЦ (`_step_single_rc`).
- `topology_manager.py`: динамическая топология соседних РЦ по положениям стрелок.
- `flags_engine.py`: формирование флагов открытия/закрытия.
