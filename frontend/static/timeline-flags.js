// static/timeline-flags.js

// Универсальные словари для ЛЗ/ЛС
const LZ_VARIANT_LABELS = {
  1: "ЛЗ v1: Смежные свободны ",
  2: "ЛЗ v2: Одна смежная занята",
  3: "ЛЗ v3: Смежные заняты",
  4: "ЛЗ v4: Выезд из тупика с СВТ",
  5: "ЛЗ v5: Занятие с замыканием",
  6: "ЛЗ v6: Занятие без замыкания",
  7: "ЛЗ v7: бесстрелочная с учётом смежных",
  8: "ЛЗ v8: По хвосту",
  9: "ЛЗ v9: Пробой",
  10: "ЛЗ v10:Выезд с пути без особождения",
  11: "ЛЗ v11: Занятость при закрытых светофорах",
  12: "ЛЗ v12: Выезд из тупика без СВТ",
  13: "ЛЗ v13: Выезд за закрытый светофор",
};

const LS_VARIANT_LABELS = {
  1: "ЛС v1: Смежные свободны",
  2: "ЛС v2: Одна смежная занята",
  4: "ЛС v4: Смежные заняты",
  5: "ЛС v5: Перепрыгивание с замыканием",
  6: "ЛС v6: Выезд из тупика по СВТ",
  9: "ЛС v9: Без смежных",
};

// Описания статусов открытия/закрытия детектора
const OPEN_LABEL = "открылось";
const CLOSE_LABEL = "закрылось";

// Прочие флаги (не зависят от номера варианта)
const GENERIC_FLAGS = {
  falselz: "ЛЗ отработала некорректно (ложная ЛЗ при свободной РЦ)",
  nolzwhenoccupied: "ЛЗ не сработала при занятой РЦ",
  switchlostcontrolwithlz: "Потеря контроля стрелки при ЛЗ",
  lzsuppressedbyexception: "ЛЗ подавлена общим исключением",
  lzsuppresseddspautoactiontimeout:
    "ЛЗ подавлена из-за тайм-аута авто-действия ДСП",
};

// Префиксы подавления с id исключений (lz_suppressed:*, ls_suppressed:*)
const LZ_SUPPRESSED_PREFIX = "lz_suppressed:";
const LS_SUPPRESSED_PREFIX = "ls_suppressed:";

// Хелпер: человекочитаемый текст для варианта ЛЗ по номеру
function describeLzVariant(v) {
  return LZ_VARIANT_LABELS[v] || `ЛЗ v${v}`;
}

// Хелпер: человекочитаемый текст для варианта ЛС по номеру
function describeLsVariant(v) {
  return LS_VARIANT_LABELS[v] || `ЛС v${v}`;
}

// Парсинг флагов вида llz_vX / llz_vX_open / llz_vX_closed
function describeLzFlag(flag) {
  const baseMatch = flag.match(/^llz_v(\d+)(?:_(open|closed))?$/);
  if (!baseMatch) return null;

  const variantNum = Number(baseMatch[1]);
  const status = baseMatch[2]; // undefined | "open" | "closed"

  const baseLabel = describeLzVariant(variantNum);

  if (!status) {
    return `${baseLabel}: детектор активен`;
  }
  if (status === "open") {
    return `${baseLabel}: ${OPEN_LABEL}`;
  }
  if (status === "closed") {
    return `${baseLabel}: ${CLOSE_LABEL}`;
  }
  return null;
}

// Парсинг флагов вида lls_vX / lls_vX_open / lls_vX_closed
function describeLsFlag(flag) {
  const baseMatch = flag.match(/^lls_v(\d+)(?:_(open|closed))?$/);
  if (!baseMatch) return null;

  const variantNum = Number(baseMatch[1]);
  const status = baseMatch[2];

  const baseLabel = describeLsVariant(variantNum);

  if (!status) {
    return `${baseLabel}: детектор активен`;
  }
  if (status === "open") {
    return `${baseLabel}: ${OPEN_LABEL}`;
  }
  if (status === "closed") {
    return `${baseLabel}: ${CLOSE_LABEL}`;
  }
  return null;
}

// Парсинг подавления: lz_suppressed:<exc_id>, ls_suppressed:<exc_id>
function describeSuppressionFlag(flag) {
  if (flag === "lzsuppressedbyexception") {
    return GENERIC_FLAGS[flag];
  }
  if (flag === "lzsuppresseddspautoactiontimeout") {
    return GENERIC_FLAGS[flag];
  }

  if (flag.startsWith(LZ_SUPPRESSED_PREFIX)) {
    const excId = flag.substring(LZ_SUPPRESSED_PREFIX.length);
    return `ЛЗ подавлена исключением ${excId}`;
  }
  if (flag.startsWith(LS_SUPPRESSED_PREFIX)) {
    const excId = flag.substring(LS_SUPPRESSED_PREFIX.length);
    return `ЛС подавлена исключением ${excId}`;
  }
  return null;
}

// Главная функция: принимает массив флагов и возвращает человекочитаемую строку
function describeFlags(flags) {
  if (!Array.isArray(flags) || flags.length === 0) {
    return "";
  }

  const result = [];

  for (const f of flags) {
    let desc = null;

    // 1) ЛЗ
    if (!desc) {
      desc = describeLzFlag(f);
    }
    // 2) ЛС
    if (!desc) {
      desc = describeLsFlag(f);
    }
    // 3) Подавления
    if (!desc) {
      desc = describeSuppressionFlag(f);
    }
    // 4) Общие флаги
    if (!desc && GENERIC_FLAGS[f]) {
      desc = GENERIC_FLAGS[f];
    }
    // 5) Фолбэк — сырой флаг
    if (!desc) {
      desc = f;
    }

    result.push(desc);
  }

  // UI ожидает строку; разделяем точкой с запятой
  return result.join("; ");
}

// --- Классификация состояний светофоров по Uni_State_ID ---
// Упрощённо, в духе python-функций signal_is_open / signal_is_shunting / и т.п.

function signalIsOpen(value) {
    return [3, 4, 13, 20, 22, 23, 27].includes(value);
}

function signalIsShunting(value) {
    return [16, 17, 11, 12, 14, 4, 5].includes(value);
}

function signalHasInvitation(value) {
    return [18, 24, 23].includes(value);
}

function signalIsClosed(value) {
    return [15, 21, 3, 7].includes(value);
}

function signalFailure(value) {
    return [19, 24, 21, 6].includes(value);
}

function signalClassForValue(value) {
    if (!value) return "signal-off";
    if (signalFailure(value)) return "signal-failure";
    if (signalHasInvitation(value)) return "signal-open"; // подсветим как разрешение
    if (signalIsShunting(value)) return "signal-shunting";
    if (signalIsOpen(value)) return "signal-open";
    if (signalIsClosed(value)) return "signal-closed";
    return "signal-unknown";
}

function applySignalClass(el, value /*, signalId */) {
    if (!el) return;
    el.classList.remove(
        "signal-open",
        "signal-shunting",
        "signal-closed",
        "signal-off",
        "signal-failure",
        "signal-unknown"
    );
    el.classList.add(signalClassForValue(Number(value) || 0));
}

// делаем доступным глобально
//window.signalClassForValue = signalClassForValue;
//window.applySignalClass = applySignalClass;


// Экспорт для ES‑модулей и для глобального доступа
export { describeFlags };
window.describeFlags = describeFlags;
