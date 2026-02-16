// static/timeline-flags.js

const EXCEPTION_LABELS = {
  exc_lz_mu_active: "ЛЗ: MU-исключение",
  exc_lz_recent_ls: "ЛЗ: недавняя ЛС",
  exc_lz8_dsp_timeout: "ЛЗ8: ДСП тайм-аут маневра",
  exc_lz_dsp_timeout: "ЛЗ: ДСП тайм-аут маневра",
  exc_ls_mu_active: "ЛС: MU-исключение",
  exc_ls_after_lz: "ЛС: после ЛЗ",
  exc_ls_dsp_timeout: "ЛС: ДСП тайм-аут маневра",
};

const SUPPRESSION_REASON_LABELS = {
  local_mu: "локальный MU",
  recent_ls: "недавняя ЛС",
  dsp_autoaction_timeout: "ДСП/автодействие тайм-аут",
  dsp_autoaction: "ДСП/автодействие",
  after_lz: "после ЛЗ",
};

const LZ_SUPPRESSED_PREFIX = "lz_suppressed:";
const LS_SUPPRESSED_PREFIX = "ls_suppressed:";

function parseFlagItem(item) {
  if (typeof item === "string") {
    return { raw: item, rc_id: "" };
  }
  return {
    raw: String(item?.raw || ""),
    rc_id: item?.rc_id ? String(item.rc_id) : "",
  };
}

function describeLzFlag(raw) {
  const m = raw.match(/^llz_v(\d+)(?:_(open|closed))?$/);
  if (!m) return null;
  const v = Number(m[1]);
  const phase = m[2];
  if (!phase) return `ЛЗ${v} активен`;
  if (phase === "open") return `ЛЗ${v} открыт`;
  return `ЛЗ${v} закрыт`;
}

function describeLsFlag(raw) {
  const m = raw.match(/^lls_(?:v)?(\d+)(?:_(open|closed))?$/);
  if (!m) return null;
  const v = Number(m[1]);
  const phase = m[2];
  if (!phase) return `ЛС${v} активен`;
  if (phase === "open") return `ЛС${v} открыт`;
  return `ЛС${v} закрыт`;
}

function describeExceptionKey(raw) {
  return EXCEPTION_LABELS[String(raw || "")] || String(raw || "");
}

function describeSuppressedKey(raw) {
  const key = String(raw || "");
  if (key.startsWith(LZ_SUPPRESSED_PREFIX)) {
    const tail = key.substring(LZ_SUPPRESSED_PREFIX.length);
    const mv = tail.match(/^v(\d+):(.*)$/);
    if (mv) {
      const v = Number(mv[1]);
      const reason = mv[2];
      return `ЛЗ${v}: ${SUPPRESSION_REASON_LABELS[reason] || reason}`;
    }
    const reason = tail;
    return `ЛЗ: ${SUPPRESSION_REASON_LABELS[reason] || reason}`;
  }
  if (key.startsWith(LS_SUPPRESSED_PREFIX)) {
    const tail = key.substring(LS_SUPPRESSED_PREFIX.length);
    const mv = tail.match(/^v(\d+):(.*)$/);
    if (mv) {
      const v = Number(mv[1]);
      const reason = mv[2];
      return `ЛС${v}: ${SUPPRESSION_REASON_LABELS[reason] || reason}`;
    }
    const reason = tail;
    return `ЛС: ${SUPPRESSION_REASON_LABELS[reason] || reason}`;
  }
  return key;
}

function describeFlags(flags, context = {}) {
  if (!Array.isArray(flags) || flags.length === 0) return "";

  const details = flags.map(parseFlagItem).filter((f) => f.raw);
  const openedBases = new Set();
  details.forEach((f) => {
    const m = f.raw.match(/^(llz_v\d+|lls_(?:v)?\d+)_open$/);
    if (m) openedBases.add(m[1]);
  });

  const rcNameById = context.rcNameById || {};
  const out = [];
  for (const f of details) {
    if (openedBases.has(f.raw) && /^(llz_v\d+|lls_(?:v)?\d+)$/.test(f.raw)) {
      continue;
    }
    const text = describeLzFlag(f.raw) || describeLsFlag(f.raw);
    if (!text) continue;

    const rcLabel = f.rc_id ? (rcNameById[f.rc_id] || f.rc_id) : "";
    out.push(rcLabel ? `${rcLabel}: ${text}` : text);
  }
  return out.join("; ");
}

function describeTriggerBadges(flags, context = {}) {
  if (!Array.isArray(flags) || flags.length === 0) return [];
  const details = flags.map(parseFlagItem).filter((f) => f.raw);
  const openedBases = new Set();
  details.forEach((f) => {
    const m = f.raw.match(/^(llz_v\d+|lls_(?:v)?\d+)_open$/);
    if (m) openedBases.add(m[1]);
  });

  const rcNameById = context.rcNameById || {};
  const out = [];
  for (const f of details) {
    if (openedBases.has(f.raw) && /^(llz_v\d+|lls_(?:v)?\d+)$/.test(f.raw)) continue;
    if (f.raw === "no_lz_when_occupied") continue;

    const lz = describeLzFlag(f.raw);
    const ls = describeLsFlag(f.raw);
    if (!lz && !ls) continue;

    const text = lz || ls;
    const kind = lz ? "lz" : "ls";
    const rcLabel = f.rc_id ? (rcNameById[f.rc_id] || f.rc_id) : "";
    out.push({
      text: rcLabel ? `${rcLabel}: ${text}` : text,
      kind,
    });
  }
  return out;
}

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
  if (signalHasInvitation(value)) return "signal-open";
  if (signalIsShunting(value)) return "signal-shunting";
  if (signalIsOpen(value)) return "signal-open";
  if (signalIsClosed(value)) return "signal-closed";
  return "signal-unknown";
}

function applySignalClass(el, value) {
  if (!el) return;
  el.classList.remove(
    "signal-open",
    "signal-shunting",
    "signal-closed",
    "signal-off",
    "signal-failure",
    "signal-unknown",
  );
  el.classList.add(signalClassForValue(Number(value) || 0));
}

export { describeFlags, describeTriggerBadges, describeExceptionKey, describeSuppressedKey, signalClassForValue, applySignalClass };
window.describeFlags = describeFlags;
window.describeTriggerBadges = describeTriggerBadges;
window.describeExceptionKey = describeExceptionKey;
window.describeSuppressedKey = describeSuppressedKey;
window.signalClassForValue = signalClassForValue;
window.applySignalClass = applySignalClass;
