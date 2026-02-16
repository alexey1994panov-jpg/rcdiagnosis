# Sandbox test scenarios (Visochino)

Импортируйте JSON в sandbox кнопкой `Импорт JSON`.

## Набор кейсов

1. `01_sw1_minus_unreachable_occupied.json`
   - При занятой `1-7СП` и `Sw1` в минус недостижимая ветка через `Sw5` не должна краснеть.

2. `02_sw1_minus_unreachable_locked.json`
   - То же для замкнутой свободной секции (`1-7СП=4`).

3. `03_sw1_minus_unreachable_free.json`
   - То же для свободной не замкнутой секции (`1-7СП=3`).

4. `04_sw1_plus_reachable_branch.json`
   - При `Sw1` в плюс подсвечивается только достижимая ветка.

5. `05_sw1_toggle_minus_plus.json`
   - Переключение `Sw1` минус -> плюс между шагами.

6. `06_rc_3p_independent_section.json`
   - `3П` светится только от собственного state.

7. `07_indicator_linked_basic.json`
   - Linked-индикатор (`IЧ1УП`) 3 -> 4 -> 3.

8. `08_complex_mix_sw1_sw5_and_rc.json`
   - Комбинированный сценарий по `1-7СП`, `Sw1`, `Sw5`, `НП`, `3П`.

9. `09_lz13_ctrl_rc_baseline.json`
   - Базовый сценарий из steps для проверки контролируемой секции (`10-12СП`) и импульса по `1-7СП`.

10. `10_1p_pulse_baseline.json`
   - Пульс `1П` (3 -> 6 -> 3) при стабильной топологии.

## Формат

Все файлы в папке содержат `events` (не `steps`) для прямого импорта в MVP sandbox.
