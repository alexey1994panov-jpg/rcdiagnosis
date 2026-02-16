// static/timeline-render.js

let timelineRows = [];
let selectedIndex = -1;

const DEFAULT_VIEW_STATE = {
  showRc: true,
  showSw: true,
  showSig: true,
  showExceptions: true,
  showFlags: false,
  showDescription: true,
  focusRc: "",
};

function getViewState() {
  const cur = window.timelineViewState || {};
  const merged = { ...DEFAULT_VIEW_STATE, ...cur };
  window.timelineViewState = merged;
  return merged;
}

function setViewState(next) {
  window.timelineViewState = { ...getViewState(), ...next };
}

function getTableBody() {
  const table = document.getElementById("timelinetable");
  return table ? table.querySelector("tbody") : null;
}

function uniq(items) {
  return Array.from(new Set((items || []).filter(Boolean)));
}

function getTimelineColumns(timeline) {
  const rc = [];
  const sw = [];
  const sig = [];
  (timeline || []).forEach((row) => {
    Object.keys(row?.rc_states || row?.rcstates || {}).forEach((k) => rc.push(k));
    Object.keys(row?.switch_states || row?.switchstates || {}).forEach((k) => sw.push(k));
    Object.keys(row?.signal_states || row?.signalstates || {}).forEach((k) => sig.push(k));
  });
  return {
    rc: uniq(rc),
    sw: uniq(sw),
    sig: uniq(sig),
  };
}

function normalizeRow(row) {
  const rcStates = row.rc_states || row.rcstates || {};
  const swStates = row.switch_states || row.switchstates || {};
  const sigStates = row.signal_states || row.signalstates || {};

  const t = typeof row.t === "number" ? row.t : (typeof row.t === "string" ? Number(row.t) || 0 : 0);
  const stepDurationRaw = row.step_duration !== undefined && row.step_duration !== null ? row.step_duration : (row.stepduration ?? 0);
  const stepDuration = typeof stepDurationRaw === "number" ? stepDurationRaw : (typeof stepDurationRaw === "string" ? Number(stepDurationRaw) || 0 : 0);

  const flagsDetailed = Array.isArray(row.flags)
    ? row.flags
      .map((f) => (typeof f === "string" ? { raw: f } : (f || {})))
      .map((f) => ({
        raw: String(f.raw || ""),
        rc_id: f.rc_id ? String(f.rc_id) : "",
        type: f.type ? String(f.type) : "",
        variant: f.variant ? String(f.variant) : "",
        phase: f.phase ? String(f.phase) : "",
      }))
      .filter((f) => f.raw)
    : [];
  const flagsRaw = flagsDetailed.map((f) => f.raw);
  const modes = row.modes || {};
  const activeExceptions = Object.keys(modes).filter((k) => k.startsWith("exc_") && Boolean(modes[k]));
  const suppressedFromFlags = flagsDetailed
    .filter((f) => f.raw.startsWith("lz_suppressed:") || f.raw.startsWith("ls_suppressed:"))
    .map((f) => ({ raw: f.raw, rc_id: f.rc_id || "" }));

  return {
    t,
    tEnd: t + stepDuration,
    stepDuration,
    ctrlRcId: String(row.ctrl_rc_id || row.ctrlrcid || ""),
    topologyByRc: row.topology_by_rc || row.topologybyrc || {},
    lzState: row.lz_state ?? row.lzstate ?? false,
    variant: row.variant ?? "",
    prevId: row.effective_prev_rc || row.effectiveprevrc || "",
    nextId: row.effective_next_rc || row.effectivenextrc || "",
    rcStates,
    swStates,
    sigStates,
    flags: flagsRaw,
    flagsDetailed,
    activeExceptions,
    suppressedFlags: suppressedFromFlags,
  };
}

function makeTh(text, cls = "") {
  const th = document.createElement("th");
  th.textContent = text;
  if (cls) th.className = cls;
  return th;
}

function makeTd(text, cls = "") {
  const cell = document.createElement("td");
  cell.textContent = text === undefined || text === null ? "" : String(text);
  if (cls) cell.className = cls;
  return cell;
}

function makeBadgesTd(items, cls, colClass = "") {
  const td = document.createElement("td");
  if (colClass) td.classList.add(colClass);
  (items || []).forEach((item) => {
    const span = document.createElement("span");
    span.className = `flag-badge ${cls}`.trim();
    span.textContent = String(item);
    td.appendChild(span);
  });
  return td;
}

function makeTriggerBadgesTd(items, colClass = "") {
  const td = document.createElement("td");
  if (colClass) td.classList.add(colClass);
  (items || []).forEach((item) => {
    const span = document.createElement("span");
    const kind = item?.kind === "ls" ? "flag-badge-ls" : "flag-badge-lz";
    span.className = `flag-badge ${kind}`.trim();
    span.textContent = String(item?.text || "");
    td.appendChild(span);
  });
  return td;
}

function rebuildTimelineHeader(columns) {
  const table = document.getElementById("timelinetable");
  if (!table) return;
  const thead = table.querySelector("thead");
  if (!thead) return;

  const tr = document.createElement("tr");
  tr.appendChild(makeTh("t_start, с", "col-base"));
  tr.appendChild(makeTh("t_end, с", "col-base"));
  tr.appendChild(makeTh("Δt, с", "col-base"));
  tr.appendChild(makeTh("ЛЗ", "col-base"));
  tr.appendChild(makeTh("Вар", "col-base"));
  tr.appendChild(makeTh("Ctrl RC", "col-topology"));
  tr.appendChild(makeTh("Пред(focus)", "col-topology"));
  tr.appendChild(makeTh("След(focus)", "col-topology"));

  columns.rc.forEach((rcId) => tr.appendChild(makeTh(rcId, "col-rc")));
  columns.sw.forEach((swId) => tr.appendChild(makeTh(swId, "col-sw")));
  columns.sig.forEach((sigId) => tr.appendChild(makeTh(sigId, "col-sig")));

  tr.appendChild(makeTh("Исключения/Подавления", "col-exc"));
  tr.appendChild(makeTh("Flags", "col-flags"));
  tr.appendChild(makeTh("Срабатывания", "col-desc"));

  thead.innerHTML = "";
  thead.appendChild(tr);
}

function applyColumnVisibility() {
  const view = getViewState();
  const table = document.getElementById("timelinetable");
  if (!table) return;

  table.querySelectorAll(".col-rc").forEach((el) => el.classList.toggle("col-hidden", !view.showRc));
  table.querySelectorAll(".col-sw").forEach((el) => el.classList.toggle("col-hidden", !view.showSw));
  table.querySelectorAll(".col-sig").forEach((el) => el.classList.toggle("col-hidden", !view.showSig));
  table.querySelectorAll(".col-exc").forEach((el) => el.classList.toggle("col-hidden", !view.showExceptions));
  table.querySelectorAll(".col-flags").forEach((el) => el.classList.toggle("col-hidden", !view.showFlags));
  table.querySelectorAll(".col-desc").forEach((el) => el.classList.toggle("col-hidden", !view.showDescription));
}

function ensureTimelineControls(timeline) {
  const root = document.getElementById("timeline-column-controls");
  if (!root) return;

  const rcMap = (window.stationLayoutData && window.stationLayoutData.rc_id_to_name) || {};
  const allRcIds = Object.keys(rcMap);
  const timelineCtrlIds = uniq((timeline || []).map((r) => String(r?.ctrl_rc_id || r?.ctrlrcid || "")).filter(Boolean));
  const focusIds = allRcIds.length ? allRcIds : timelineCtrlIds;
  const view = getViewState();

  if (view.focusRc && focusIds.length && !focusIds.includes(view.focusRc)) {
    setViewState({ focusRc: "" });
  }

  root.innerHTML = "";
  root.className = "controls controls-compact";

  const mkCheck = (label, checked, onChange) => {
    const lbl = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = checked;
    cb.addEventListener("change", () => onChange(cb.checked));
    lbl.appendChild(cb);
    lbl.appendChild(document.createTextNode(label));
    root.appendChild(lbl);
  };

  mkCheck("RC", view.showRc, (v) => { setViewState({ showRc: v }); applyColumnVisibility(); });
  mkCheck("Стрелки", view.showSw, (v) => { setViewState({ showSw: v }); applyColumnVisibility(); });
  mkCheck("Сигналы", view.showSig, (v) => { setViewState({ showSig: v }); applyColumnVisibility(); });
  mkCheck("Исключения/Подавления", view.showExceptions, (v) => { setViewState({ showExceptions: v }); applyColumnVisibility(); });
  mkCheck("Flags", view.showFlags, (v) => { setViewState({ showFlags: v }); applyColumnVisibility(); });
  mkCheck("Срабатывания", view.showDescription, (v) => { setViewState({ showDescription: v }); applyColumnVisibility(); });

  const focusWrap = document.createElement("label");
  focusWrap.textContent = "Focus RC:";
  const sel = document.createElement("select");
  const optAll = document.createElement("option");
  optAll.value = "";
  optAll.textContent = "(all ctrl RC)";
  sel.appendChild(optAll);
  focusIds
    .slice()
    .sort((a, b) => {
      const an = rcMap[a] || a;
      const bn = rcMap[b] || b;
      return an.localeCompare(bn, "ru");
    })
    .forEach((rcId) => {
    const opt = document.createElement("option");
    opt.value = rcId;
    const rcName = rcMap[rcId] || rcId;
    opt.textContent = `${rcName} (${rcId})`;
    sel.appendChild(opt);
    });
  sel.value = getViewState().focusRc || "";
  sel.addEventListener("change", () => {
    setViewState({ focusRc: sel.value });
    if (Array.isArray(window.lastTimeline)) renderTimeline(window.lastTimeline);
  });
  focusWrap.appendChild(sel);
  root.appendChild(focusWrap);
}

function renderTimeline(timeline) {
  const tableBody = getTableBody();
  if (!tableBody) return;

  window.lastTimeline = Array.isArray(timeline) ? timeline : [];
  ensureTimelineControls(window.lastTimeline);

  timelineRows = [];
  selectedIndex = window.lastTimeline.length ? 0 : -1;
  tableBody.innerHTML = "";

  const columns = getTimelineColumns(window.lastTimeline);
  rebuildTimelineHeader(columns);

  const view = getViewState();
  let prevSuppressedKeys = new Set();
  const lastLzVariantByRc = {};
  const lastLsVariantByRc = {};

  window.lastTimeline.forEach((rawRow, idx) => {
    const row = normalizeRow(rawRow);
    const tr = document.createElement("tr");
    tr.dataset.index = String(idx);
    timelineRows.push(tr);

    const flagsText = row.flags.join(", ");
    const rcNameById = (window.stationLayoutData && window.stationLayoutData.rc_id_to_name) || {};
    const shownCtrlRcId = view.focusRc || row.ctrlRcId;
    (row.flagsDetailed || []).forEach((f) => {
      const rcId = f.rc_id || shownCtrlRcId || "";
      if (!rcId) return;
      const lz = String(f.raw || "").match(/^llz_v(\d+)(?:_|$)/);
      if (lz) {
        lastLzVariantByRc[rcId] = Number(lz[1]);
      }
      const ls = String(f.raw || "").match(/^lls_(?:v)?(\d+)(?:_|$)/);
      if (ls) {
        lastLsVariantByRc[rcId] = Number(ls[1]);
      }
    });
    const triggerBadges = window.describeTriggerBadges
      ? window.describeTriggerBadges(row.flagsDetailed, { rcNameById })
      : [];
    const curSuppressedKeys = new Set(
      (row.suppressedFlags || []).map((item) => {
        const rcId = item?.rc_id || shownCtrlRcId || "";
        return `${rcId}|${String(item?.raw || "")}`;
      }),
    );
    const newSuppressedAll = (row.suppressedFlags || []).filter((item) => {
      const rcId = item?.rc_id || shownCtrlRcId || "";
      const key = `${rcId}|${String(item?.raw || "")}`;
      return !prevSuppressedKeys.has(key);
    });
    // Prefer variant-qualified suppression (e.g. lz_suppressed:v2:recent_ls) over generic one.
    const typedSuppSet = new Set(
      newSuppressedAll
        .map((item) => String(item?.raw || ""))
        .filter((raw) => /^(lz_suppressed|ls_suppressed):v\d+:/.test(raw))
        .map((raw) => raw.replace(/^((?:lz|ls)_suppressed):v\d+:/, "$1:")),
    );
    const newSuppressed = newSuppressedAll.filter((item) => {
      const raw = String(item?.raw || "");
      if (/^(lz_suppressed|ls_suppressed):v\d+:/.test(raw)) return true;
      return !typedSuppSet.has(raw);
    });
    prevSuppressedKeys = curSuppressedKeys;

    const suppressedLabels = newSuppressed.map((item) => {
      const rcId = item?.rc_id || shownCtrlRcId;
      const rcLabel = rcId ? (rcNameById[rcId] || rcId) : "";
      const raw = String(item?.raw || "");
      const rawBody = (window.describeSuppressedKey ? window.describeSuppressedKey(raw) : raw);
      let body = rawBody;
      if (raw.startsWith("lz_suppressed:")) {
        let v = 0;
        const mv = raw.match(/^lz_suppressed:v(\d+):/);
        if (mv) {
          v = Number(mv[1]);
        } else if (Number(row.variant) > 0 && Number(row.variant) < 100) {
          v = Number(row.variant);
        } else if (rcId && Number(lastLzVariantByRc[rcId]) > 0) {
          v = Number(lastLzVariantByRc[rcId]);
        }
        body = rawBody.replace("ЛЗ:", `ЛЗ${v > 0 ? String(v) : "N"}:`);
      } else if (raw.startsWith("ls_suppressed:")) {
        let v = 0;
        const mv = raw.match(/^ls_suppressed:v(\d+):/);
        if (mv) {
          v = Number(mv[1]);
        } else if (Number(row.variant) >= 100) {
          v = Number(row.variant) - 100;
        } else if (rcId && Number(lastLsVariantByRc[rcId]) > 0) {
          v = Number(lastLsVariantByRc[rcId]);
        }
        body = rawBody.replace("ЛС:", `ЛС${v > 0 ? String(v) : "N"}:`);
      }
      return rcLabel ? `${rcLabel}: ${body}` : body;
    });
    const exSuppLabels = suppressedLabels;

    const focusTopo = view.focusRc ? (row.topologyByRc[view.focusRc] || null) : null;
    const shownCtrlRc = shownCtrlRcId ? `${rcNameById[shownCtrlRcId] || shownCtrlRcId} (${shownCtrlRcId})` : "";
    const shownPrev = focusTopo ? (focusTopo.prev || "") : row.prevId;
    const shownNext = focusTopo ? (focusTopo.next || "") : row.nextId;

    tr.appendChild(makeTd(row.t.toFixed(1), "col-base"));
    tr.appendChild(makeTd(row.tEnd.toFixed(1), "col-base"));
    tr.appendChild(makeTd(row.stepDuration, "col-base"));
    tr.appendChild(makeTd(row.lzState ? "1" : "0", "col-base"));
    tr.appendChild(makeTd(row.variant, "col-base"));
    tr.appendChild(makeTd(shownCtrlRc, "col-topology"));
    tr.appendChild(makeTd(shownPrev, "col-topology"));
    tr.appendChild(makeTd(shownNext, "col-topology"));

    columns.rc.forEach((rcId) => {
      const val = row.rcStates[rcId] ?? "";
      const td = makeTd(val, "col-rc");
      if (window.applyRcStateClass) window.applyRcStateClass(td, val);
      tr.appendChild(td);
    });
    columns.sw.forEach((swId) => {
      const val = row.swStates[swId] ?? "";
      const td = makeTd(val, "col-sw");
      if (window.swClassForValue) td.classList.add(window.swClassForValue(val));
      tr.appendChild(td);
    });
    columns.sig.forEach((sigId) => {
      const val = row.sigStates[sigId] ?? "";
      const td = makeTd(val, "col-sig");
      if (window.applySignalClass) {
        const code = String(sigId).startsWith("\u041c") ? 3 : 4;
        const probe = document.createElement("div");
        window.applySignalClass(probe, val, code);
        probe.classList.forEach((x) => td.classList.add(x));
      }
      tr.appendChild(td);
    });

    tr.appendChild(makeBadgesTd(exSuppLabels, "flag-badge-exc", "col-exc"));
    tr.appendChild(makeTd(flagsText, "col-flags"));
    tr.appendChild(makeTriggerBadgesTd(triggerBadges, "col-desc"));

    tr.addEventListener("click", () => moveSelection(idx));
    tableBody.appendChild(tr);
  });

  if (window.lastTimeline.length) {
    const last = normalizeRow(window.lastTimeline[window.lastTimeline.length - 1]);
    const endTr = document.createElement("tr");
    endTr.className = "timeline-end-row";
    endTr.appendChild(makeTd(last.tEnd.toFixed(1), "col-base"));
    endTr.appendChild(makeTd(last.tEnd.toFixed(1), "col-base"));
    endTr.appendChild(makeTd("0", "col-base"));
    endTr.appendChild(makeTd("", "col-base"));
    endTr.appendChild(makeTd("END", "col-base"));
    endTr.appendChild(makeTd("", "col-topology"));
    endTr.appendChild(makeTd("", "col-topology"));
    endTr.appendChild(makeTd("", "col-topology"));
    columns.rc.forEach(() => endTr.appendChild(makeTd("", "col-rc")));
    columns.sw.forEach(() => endTr.appendChild(makeTd("", "col-sw")));
    columns.sig.forEach(() => endTr.appendChild(makeTd("", "col-sig")));
    endTr.appendChild(makeTd("", "col-exc"));
    endTr.appendChild(makeTd("", "col-flags"));
    endTr.appendChild(makeTd("", "col-desc"));
    tableBody.appendChild(endTr);
  }

  applyColumnVisibility();
  renderTimebar(window.lastTimeline);
  updateSelectionHighlight();
  if (selectedIndex >= 0 && window.updateTrackScheme && window.lastTimeline[selectedIndex]) {
    window.updateTrackScheme(window.lastTimeline[selectedIndex]);
  }
}

function renderTimebar(timeline) {
  const bar = document.getElementById("timebarcontainer");
  const info = document.getElementById("timebarinfo");
  if (!bar) return;
  bar.innerHTML = "";
  if (!timeline || !timeline.length) {
    if (info) info.textContent = "";
    return;
  }

  const first = timeline[0] || {};
  const last = timeline[timeline.length - 1] || {};
  const tStart = typeof first.t === "number" ? first.t : 0;
  const lastT = typeof last.t === "number" ? last.t : 0;
  const lastStep = last.step_duration ?? last.stepduration ?? 0;
  const tEnd = lastT + lastStep;
  const total = Math.max(tEnd - tStart, 1e-6);

  timeline.forEach((row, idx) => {
    const seg = document.createElement("div");
    seg.className = "timebar-segment";
    const sd = row.step_duration ?? row.stepduration ?? 0;
    seg.style.width = `${Math.max((sd / total) * 100, 0.5)}%`;

    const lzState = row.lz_state ?? row.lzstate ?? false;
    if (lzState) seg.classList.add("timebar-segment-lz");

    const flags = Array.isArray(row.flags)
      ? row.flags.map((f) => (typeof f === "string" ? f : (f?.raw || ""))).filter(Boolean)
      : [];
    if (flags.some((f) => String(f).endsWith("_closed"))) seg.classList.add("timebar-segment-closed");
    if (flags.some((f) => String(f).startsWith("lz_suppressed:"))) seg.classList.add("timebar-segment-suppressed");
    if (idx === selectedIndex) seg.classList.add("timebar-segment-selected");

    seg.title = `t=${row.t ?? ""}, variant=${row.variant ?? ""}`;
    seg.addEventListener("click", () => moveSelection(idx));
    bar.appendChild(seg);
  });

  if (info) {
    const cur = timeline[selectedIndex];
    const tVal = cur && typeof cur.t === "number" ? cur.t.toFixed(1) : "-";
    info.textContent = `t = ${tVal} с, интервалов: ${timeline.length}, конец: ${tEnd.toFixed(1)} с`;
  }
}

function moveSelection(newIndex) {
  if (newIndex < 0 || newIndex >= timelineRows.length) return;
  selectedIndex = newIndex;
  updateSelectionHighlight();
  if (window.updateTrackScheme && window.lastTimeline && window.lastTimeline[selectedIndex]) {
    window.updateTrackScheme(window.lastTimeline[selectedIndex]);
  }
  renderTimebar(window.lastTimeline);
}

function updateSelectionHighlight() {
  const tableBody = getTableBody();
  if (!tableBody) return;
  Array.from(tableBody.querySelectorAll("tr")).forEach((tr) => {
    const idx = Number(tr.dataset.index);
    tr.classList.toggle("timeline-selected", idx === selectedIndex);
  });
}

function scrollToRow(index) {
  const tableBody = getTableBody();
  if (!tableBody) return;
  const tr = tableBody.querySelector(`tr[data-index="${index}"]`);
  if (tr && typeof tr.scrollIntoView === "function") tr.scrollIntoView({ block: "nearest" });
}

function moveSelectionRelativeImpl(delta) {
  if (!window.lastTimeline || !window.lastTimeline.length) return;
  const newIndex = Math.min(window.lastTimeline.length - 1, Math.max(0, selectedIndex + delta));
  moveSelection(newIndex);
}

export {
  renderTimeline,
  renderTimebar,
  moveSelection,
  moveSelectionRelativeImpl,
  updateSelectionHighlight,
  scrollToRow,
};

window.renderTimeline = renderTimeline;
window.renderTimebar = renderTimebar;
window.moveSelectionRelativeImpl = moveSelectionRelativeImpl;
