# Validation Report (MVP)

Проверка эталонных сценариев для MVP-мнемосхемы.

## Coverage

- Геометрия РЦ/стрелок по состояниям.
- Недостижимые ветки в стрелочных секциях.
- Базовые переходы по времени (`t`).
- Linked-индикаторы (`PrevSec/NextSec`).
- Смешанные сценарии (RC + switch + indicator).

## Scenarios

- 01: minus/unreachable occupied
- 02: minus/unreachable locked
- 03: minus/unreachable free
- 04: plus/reachable branch
- 05: switch toggle timeline
- 06: independent RC section
- 07: linked indicator basic
- 08: complex mixed case
- 09: ctrl RC baseline from steps
- 10: 1P pulse baseline

## Result

Статус: `PASS` для MVP sandbox (визуальная проверка).

## Notes

- Используется формат `events` как канонический для UI sandbox.
- `steps` допускаются как исходник, но в sandbox рекомендуется хранить эталоны в `events`.
