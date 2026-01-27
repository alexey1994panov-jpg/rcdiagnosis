// static/timeline-render.js

// Ожидается, что describeFlags и updateTrackScheme лежат в window.

let timelineRows = [];
let selectedIndex = -1;

function getTableBody() {
  const table = document.getElementById("timelinetable");
  return table ? table.querySelector("tbody") : null;
}

// Унифицированный доступ к полям строки таймлайна (старый/новый формат)
function normalizeRow(row) {
  const rcStates = row.rc_states || row.rcstates || {};
  const swStates = row.switch_states || row.switchstates || {};

  const prevId = row.effective_prev_rc || row.effectiveprevrc || "10-12SP";
  const currId = "1P";
  const nextId = row.effective_next_rc || row.effectivenextrc || "1-7SP";

  const t =
    typeof row.t === "number"
      ? row.t
      : (typeof row.t === "string" ? Number(row.t) || 0 : 0);

  const stepDurationRaw =
    row.step_duration !== undefined && row.step_duration !== null
      ? row.step_duration
      : (row.stepduration ?? 0);
  const stepDuration =
    typeof stepDurationRaw === "number"
      ? stepDurationRaw
      : (typeof stepDurationRaw === "string" ? Number(stepDurationRaw) || 0 : 0);

  // Пока бэкенд отдаёт одно поле mu_state – дублируем его на три колонки MU.
  const muRaw = row.mu_state;
  const muVal = muRaw === undefined || muRaw === null ? "" : String(muRaw);

  return {
    t,
    stepDuration,

    lzState: row.lz_state ?? row.lzstate ?? false,
    variant: row.variant ?? "",

    prevId,
    currId,
    nextId,

    prevState: prevId ? (rcStates[prevId] ?? "") : "",
    currState: rcStates[currId] ?? "",
    nextState: nextId ? (rcStates[nextId] ?? "") : "",

    sw10State: swStates["Sw10"] ?? "",
    sw1State:  swStates["Sw1"]  ?? "",
    sw5State:  swStates["Sw5"]  ?? "",

    muPrev: muVal,
    muCurr: muVal,
    muNext: muVal,

    dspState:  row.dsp_state  ?? row.dspstate  ?? "",
    nasState:  row.nas_state  ?? row.nasstate  ?? "",
    chasState: row.chas_state ?? row.chasstate ?? "",

    flags: row.flags || []
  };
}

function makeTd(text) {
  const cell = document.createElement("td");
  cell.textContent = text === undefined || text === null ? "" : String(text);
  return cell;
}

function renderTimeline(timeline) {
  const tableBody = getTableBody();
  if (!tableBody) return;

  window.lastTimeline = Array.isArray(timeline) ? timeline : [];
  timelineRows = [];
  selectedIndex = window.lastTimeline.length ? 0 : -1;

  tableBody.innerHTML = "";

  window.lastTimeline.forEach((rawRow, idx) => {
    const row = normalizeRow(rawRow);

    const tr = document.createElement("tr");
    tr.dataset.index = String(idx);
    timelineRows.push(tr);

    const flagsText = row.flags.join(", ");
    const flagsDesc = window.describeFlags ? window.describeFlags(row.flags) : "";

    // t, c
    tr.appendChild(makeTd(row.t.toFixed(1)));
    // Δt, c
    tr.appendChild(makeTd(row.stepDuration));
    // ЛЗ
    tr.appendChild(makeTd(row.lzState ? "1" : "0"));
    // Вар
    tr.appendChild(makeTd(row.variant));
    // Пред (effective prev RC id)
    tr.appendChild(makeTd(row.prevId));

    // 10-12SP (состояние РЦ)
    const tdPrevState = makeTd(row.prevState);
    if (window.applyRcStateClass) window.applyRcStateClass(tdPrevState, row.prevState);
    tr.appendChild(tdPrevState);

    // Ст.10-12SP (идентификатор РЦ)
    tr.appendChild(makeTd("10-12SP"));

    // Sw10
    const tdSw10 = makeTd(row.sw10State);
    if (window.swClassForValue) tdSw10.classList.add(window.swClassForValue(row.sw10State));
    tr.appendChild(tdSw10);

    // 1P (состояние контролируемой РЦ)
    const tdCurrState = makeTd(row.currState);
    if (window.applyRcStateClass) window.applyRcStateClass(tdCurrState, row.currState);
    tr.appendChild(tdCurrState);

    // Ст.1P
    tr.appendChild(makeTd(row.currId));

    // 1-7SP (состояние РЦ)
    const tdNextState = makeTd(row.nextState);
    if (window.applyRcStateClass) window.applyRcStateClass(tdNextState, row.nextState);
    tr.appendChild(tdNextState);

    // Ст.1-7SP
    tr.appendChild(makeTd(row.nextId));

    // Sw1
    const tdSw1 = makeTd(row.sw1State);
    if (window.swClassForValue) tdSw1.classList.add(window.swClassForValue(row.sw1State));
    tr.appendChild(tdSw1);

    // Sw5
    const tdSw5 = makeTd(row.sw5State);
    if (window.swClassForValue) tdSw5.classList.add(window.swClassForValue(row.sw5State));
    tr.appendChild(tdSw5);

    // MU 10-12SP / 1P / 1-7SP
    tr.appendChild(makeTd(row.muPrev));
    tr.appendChild(makeTd(row.muCurr));
    tr.appendChild(makeTd(row.muNext));

    // ДСП / НАС / ЧАС
    tr.appendChild(makeTd(row.dspState));
    tr.appendChild(makeTd(row.nasState));
    tr.appendChild(makeTd(row.chasState));

    // Flags
    tr.appendChild(makeTd(flagsText));

    // Описание
    tr.appendChild(makeTd(flagsDesc));

    tr.addEventListener("click", () => {
      moveSelection(idx);
    });

    tableBody.appendChild(tr);
  });

  renderTimebar(window.lastTimeline);
  updateSelectionHighlight();
  if (selectedIndex >= 0 && window.updateTrackScheme && window.lastTimeline[selectedIndex]) {
    window.updateTrackScheme(window.lastTimeline[selectedIndex]);
  }
}

function renderTimebar(timeline) {
  const bar  = document.getElementById("timebarcontainer");
  const info = document.getElementById("timebarinfo");
  if (!bar) return;

  bar.innerHTML = "";
  if (!timeline || !timeline.length) {
    if (info) info.textContent = "";
    return;
  }

  const first = timeline[0] || {};
  const last  = timeline[timeline.length - 1] || {};

  const tStart   = typeof first.t === "number" ? first.t : 0;
  const lastT    = typeof last.t === "number" ? last.t : 0;
  const lastStep = last.step_duration ?? last.stepduration ?? 0;
  const tEnd     = lastT + lastStep;
  const total    = Math.max(tEnd - tStart, 1e-6);

  const equalDurations = timeline.every(
    r => (r.step_duration ?? r.stepduration ?? 0) === (timeline[0].step_duration ?? timeline[0].stepduration ?? 0)
  );

  timeline.forEach((row, idx) => {
    const seg = document.createElement("div");
    seg.className = "timebar-segment";

    const sd = row.step_duration ?? row.stepduration ?? 0;
    let widthPct;
    if (equalDurations && sd > 0) {
      widthPct = 100 / timeline.length;
    } else {
      widthPct = (sd / total) * 100;
    }
    seg.style.width = `${Math.max(widthPct, 0.5)}%`;

    const lzState = row.lz_state ?? row.lzstate ?? false;
    if (lzState) seg.classList.add("timebar-segment-lz");

    const flags = row.flags || [];
    if (
      flags.includes("llz_v1_closed") ||
      flags.includes("llz_v2_closed") ||
      flags.includes("llz_v3_closed") ||
      flags.includes("llz_v6_closed") ||
      flags.includes("llz_v8_closed") ||
      flags.includes("lls_v1_closed") ||
      flags.includes("lls_v2_closed") ||
      flags.includes("lls_v4_closed") ||
      flags.includes("lls_v9_closed")
    ) {
      seg.classList.add("timebar-segment-closed");
    }
    if (flags.some(f => f.startsWith("lz_suppressed:"))) {
      seg.classList.add("timebar-segment-suppressed");
    }

    if (idx === selectedIndex) seg.classList.add("timebar-segment-selected");

    seg.title = "t=" + (row.t ?? "") + ", variant=" + (row.variant ?? "");
    seg.addEventListener("click", () => {
      moveSelection(idx);
    });

    bar.appendChild(seg);
  });

  if (info) {
    const cur = timeline[selectedIndex];
    const tVal = cur && typeof cur.t === "number" ? cur.t.toFixed(1) : "-";
    info.textContent = `t = ${tVal} с`;
  }
}

function moveSelection(newIndex) {
    if (newIndex < 0 || newIndex >= timelineRows.length) return;
    selectedIndex = newIndex;
    updateSelectionHighlight();

    if (window.updateTrackScheme && window.lastTimeline && window.lastTimeline[selectedIndex]) {
        window.updateTrackScheme(window.lastTimeline[selectedIndex]);
    }

    // УБРАЛИ scrollToRow, чтобы страница не прыгала
    // scrollToRow(selectedIndex);

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
  if (tr && typeof tr.scrollIntoView === "function") {
    tr.scrollIntoView({ block: "nearest" });
  }
}

// Для кнопок «◀»/«▶»
function moveSelectionRelativeImpl(delta) {
  if (!window.lastTimeline || !window.lastTimeline.length) return;
  const newIndex = Math.min(
    window.lastTimeline.length - 1,
    Math.max(0, selectedIndex + delta),
  );
  moveSelection(newIndex);
}

// ES‑экспорт для timeline.js
export {
  renderTimeline,
  renderTimebar,
  moveSelection,
  moveSelectionRelativeImpl,
  updateSelectionHighlight,
  scrollToRow,
};

// Глобальные ссылки для старого кода
window.renderTimeline = renderTimeline;
window.renderTimebar = renderTimebar;
window.moveSelectionRelativeImpl = moveSelectionRelativeImpl;
