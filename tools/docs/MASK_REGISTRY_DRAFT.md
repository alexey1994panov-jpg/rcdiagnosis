# MASK REGISTRY DRAFT (for review)

## Purpose
Единый реестр масок для всех вариантов с правилами:
- Простые маски: ID с `1` и далее `+1`.
- Сложные маски (`OR`/составные): ID с `100` и далее `+1`.
- Имена без привязки к варианту (`LZ/LS`, `DANO/KOGDA` не использовать).
- Нотация состояний:
  - `P` = prev RC, `C` = ctrl RC, `N` = next RC.
  - `0` = свободна, `1` = занята, `X` = не важно, `N` = NC/не контролируется.
  - Сигналы: `S1` = открыт, `S0` = закрыт, `SX` = не важно.
  - Замыкание: `L1` = замкнута, `L0` = не замкнута.

## Canonical naming
Формат сухого имени:
- `RC_P{0|1|X|N}_C{0|1|X|N}_N{0|1|X|N}`
- Добавки через `__`: `__SIG_S1`, `__SIG_S0`, `__LOCK_CTRL_L1`, `__LOCK_ADJ_L1`, `__NC_PREV`, `__NC_NEXT`

## Registry table

| Current ID | Current name/function | Proposed ID | Proposed canonical name | What is checked (RC/signal/NC/lock) | Human-readable mask | Used in |
|---:|---|---:|---|---|---|---|
| 0 | `mask_000` | 1 | `RC_0_0_0` | `P=0, C=0, N=0` | `000` | LZ1, LS1, LZ2(OR), (LZ11/13 aliases  |
| 1 | `mask_010` | 2 | `RC_0_1_0` | `P=0, C=1, N=0` | `010` | LZ1, LZ8, LS1, LZ11/13 aliases |
| 2 | `mask_101` | 3 | `RC_1_0_1` | `P=1, C=0, N=1` | `101` | LZ3, LS4 |
| 3 | `mask_111` | 4 | `RC_1_1_1` | `P=1, C=1, N=1` | `111` | LZ3, LS4 |
| 4 | `mask_100` | 5 | `RC_1_0_0` | `P=1, C=0, N=0` | `100` | LZ2, LS2 |
| 5 | inline LZ2 (`110`) должна быть маска  `mask_110` | 6 | `RC_1_1_0` | `P=1, C=1, N=0` | `110` | LZ2, LS2 |
| 6 | `mask_001` | 7 | `RC_P0_C0_N1` | `P=0, C=0, N=1` | `001` | LZ2, LS2 |
| 7 | `mask_011` | 8 | `RC_P0_C1_N1` | `P=0, C=1, N=1` | `011` | LZ2, LZ8, LS2 |
| 200 | `mask_x0x` | 9 | `RC_PX_C0_NX` | `C=0` | `X0X` | LZ7 |
| 201 | `mask_x0x_occ` | 10 | `RC_PX_C1_NX` | `C=1` | `X1X` | LZ7 |
| 202 | `mask_00x` | 11 | `RC_P0_C0_NX` | `P=0, C=0` | `00X` | LZ7 |
| 203 | `mask_00x_occ` | 12 | `RC_P0_C1_NX` | `P=0, C=1` | `01X` | LZ7 |
| 204 | `mask_x00` | 13 | `RC_PX_C0_N0` | `C=0, N=0` | `X00` | LZ7 |
| 205 | `mask_x00_occ` | 14 | `RC_PX_C1_N0` | `C=1, N=0` | `X10` | LZ7 |
| 600 | `mask_ctrl_free` | 15 | `RC_CTRL_0` | `C=0` | `C0` | LZ6, LS9, LZ13 helper |
| 601 | `mask_ctrl_occupied` | 16 | `RC_CTRL_1` | `C=1` | `C1` | LZ6, LS9, LZ13 helper |
| 500 | `mask_0_not_locked` | 17 | `RC_CTRL_0__LOCK_CTRL_L0__CANLOCK_1` | `C=0, ctrl unlocked, can_lock=1` | `C0 & Lc0 & can_lock` | LZ5 |
| 501 | `mask_1_not_locked` | 18 | `RC_CTRL_1__LOCK_CTRL_L0__CANLOCK_1` | `C=1, ctrl unlocked, can_lock=1` | `C1 & Lc0 & can_lock` | LZ5 |
| 505 | `mask_ls5_prev_locked_p0` | 19 | `RC_P1_C0_NX__LOCK_P1__LOCK_C1` | `P=1(lock), C=0(lock)` | `P1L1 C0L1` | LS5 |
| 506 | `mask_ls5_next_locked_p0` | 20 | `RC_PX_C0_N1__LOCK_N1__LOCK_C1` | `N=1(lock), C=0(lock)` | `N1L1 C0L1` | LS5 |
| 507 | `mask_ls5_both_locked_p1` | 21 | `RC_P1_C0_N1__LOCK_P1__LOCK_C1__LOCK_N1` | `P=1(lock), C=0(lock), N=1(lock)` | `P1L1 C0L1 N1L1` | LS5 |
| 512 | `mask_lz12_prev_nc_p0` | 22 | `RC_CTRL_0__NC_PREV` | `prev_nc=1, C=0` | `PN C0` | LZ12 |
| 513 | `mask_lz12_prev_nc_p1` | 23 | `RC_CTRL_1__NC_PREV` | `prev_nc=1, C=1` | `PN C1` | LZ12 |
| 514 | `mask_lz12_next_nc_p0` | 24 | `RC_CTRL_0__NC_NEXT` | `next_nc=1, C=0` | `NN C0` | LZ12 |
| 515 | `mask_lz12_next_nc_p1` | 25 | `RC_CTRL_1__NC_NEXT` | `next_nc=1, C=1` | `NN C1` | LZ12 |
| 520 | local LZ4 prev p0 | 26 | `RC_CTRL_0__NC_PREV__SIG_S0` | `prev_nc=1, C=0, signal closed` | `PN C0 S0` | LZ4 |
| 521 | local LZ4 prev p1 | 27 | `RC_CTRL_1__NC_PREV__SIG_S0` | `prev_nc=1, C=1, signal closed` | `PN C1 S0` | LZ4 |
| 522 | local LZ4 next p0 | 28 | `RC_CTRL_0__NC_NEXT__SIG_S0` | `next_nc=1, C=0, signal closed` | `NN C0 S0` | LZ4 |
| 523 | local LZ4 next p1 | 29 | `RC_CTRL_1__NC_NEXT__SIG_S0` | `next_nc=1, C=1, signal closed` | `NN C1 S0` | LZ4 |
| 1600 | local LS6 p0 | 30 | `RC_CTRL_0__NC_ONE__ADJ_0__LOCK_CTRL_L1__LOCK_ADJ_L1__SIG_S1` | `one_nc=1, C=0(lock), adj=0(lock), signal open` | `NC C0L1 A0L1 S1` | LS6 |
| 1601 | local LS6 p1 | 31 | `RC_CTRL_0__NC_ONE__ADJ_1__LOCK_CTRL_L1__LOCK_ADJ_L1` | `one_nc=1, C=0(lock), adj=1(lock)` | `NC C0L1 A1L1` | LS6 |
| 900 | `mask_lz9_given` | 32 | `RC_CTRL_0__ADJ_FREE_OR_NC` | `C=0 and all adj are free or NC` | `C0 A(0/N)` | LZ9 |
| 901 | `mask_lz9_ctrl_occ_adj_free` | 33 | `RC_CTRL_1__ADJ_FREE_OR_NC` | `C=1 and adj free/NC` | `C1 A(0/N)` | LZ9 |
| 902 | `mask_lz9_ctrl_free_adj_occ` | 34 | `RC_CTRL_0__ADJ_OCC` | `C=0 and any adj occupied (not NC)` | `C0 A1` | LZ9 |
| 903 | `mask_lz9_both_occ` | 35 | `RC_CTRL_1__ADJ_OCC` | `C=1 and any adj occupied (not NC)` | `C1 A1` | LZ9 |
| 904 | `mask_lz9_ctrl_occ_prev_occ` | 36 | `RC_CTRL_1__PREV_OCC` | `C=1 and prev occupied (not NC)` | `C1 P1` | LZ9 |
| 905 | `mask_lz9_ctrl_occ_next_occ` | 37 | `RC_CTRL_1__NEXT_OCC` | `C=1 and next occupied (not NC)` | `C1 N1` | LZ9 |
| 1100 | LZ11 phase0 | 38 | `RC_CTRL_0__SIGA_S0__SIGB_S0` | `C=0 and sigA closed and sigB closed` | `C0 SA0 SB0` | LZ11 |
| 1101 | LZ11 phase1 | 39 | `RC_CTRL_1__SIGA_S0__SIGB_S0` | `C=1 and sigA closed and sigB closed` | `C1 SA0 SB0` | LZ11 |
| 1300 | LZ13 phase0 | 40 | `RC_CTRL_0__ADJ_0__LOCK_ADJ_L1__SIG_S0` | `adj free+lock, C=0, signal closed` | `A0L1 C0 S0` | LZ13 |
| 1301 | LZ13 phase1 | 41 | `RC_CTRL_0__ADJ_1__LOCK_ADJ_L1__SIG_S0` | `adj occ+lock, C=0, signal closed` | `A1L1 C0 S0` | LZ13 |
| 1302 | LZ13 phase2 | 42 | `RC_CTRL_1__ADJ_1__LOCK_ADJ_L1__SIG_S0` | `adj occ+lock, C=1, signal closed` | `A1L1 C1 S0` | LZ13 |
| 1010 | LZ10 phase0 | 43 | `RC_P0_C1_N0__SIG_S1` | `P=0,C=1,N=0 and signal open` | `010 S1` | LZ10 |
| 1011 | LZ10 phase1 | 44 | `RC_DIR_STEP2__SIG_S1` | `to_next:011 / to_prev:110, signal open` | `(011|110) S1` | LZ10 |
| 1012 | LZ10 phase2 | 45 | `RC_DIR_STEP2__SIG_S0` | `to_next:011 / to_prev:110, signal closed` | `(011|110) S0` | LZ10 |
| 1013 | LZ10 phase3 | 46 | `RC_P0_C1_N0__SIG_S0` | `P=0,C=1,N=0 and signal closed` | `010 S0` | LZ10 |
| 100 | `mask_100_or_000` | 100 | `RC_P1_C0_N0_OR_P0_C0_N0` | `(100) OR (000)` | `100|000` | LZ2 |
| 101 | `mask_001_or_000` | 101 | `RC_P0_C0_N1_OR_P0_C0_N0` | `(001) OR (000)` | `001|000` | LZ2 |
| 106 | alias used in LZ2 | 101 (alias) | `RC_P0_C0_N1_OR_P0_C0_N0` | alias of 101 | `001|000` | LZ2 |
| 208 | `mask_110_or_111` | 102 | `RC_P1_C1_N0_OR_P1_C1_N1` | `(110) OR (111)` | `110|111` | LZ8 |
| 209 | `mask_011_or_111` | 103 | `RC_P0_C1_N1_OR_P1_C1_N1` | `(011) OR (111)` | `011|111` | LZ8 |
| 210 | `mask_01x_or_x10` | 104 | `RC_P0_C1_NX_OR_PX_C1_N0` | `(01X) OR (X10)` | `01X|X10` | LZ8 |

## Notes for implementation after review
- Убрать в `mask_to_string` и `get_mask_by_id` названия вида `LZ*`, `LS*`, `DANO/KOGDA`.
- В фабриках заменить локальные названия (`mask_dano`, `mask_kogda`, `mask_p01`) на имена по canonical mask.
- Вынести локальные маски (`520..523`, `1010..1013`, `1600..1601`) в общий реестр.
- Оставить временные alias для обратной совместимости (`106 -> 101`).
