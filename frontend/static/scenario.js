// static/scenario.js
// Dynamic scenario table: RC/SW/SIG columns come from scenario data and station layout.

const DEFAULT_RC_IDS = ["10-12SP", "1P", "1-7SP"];
const DEFAULT_SW_IDS = ["Sw10", "Sw1", "Sw5"];
const DEFAULT_SIG_IDS = ["Ч1", "НМ1", "ЧМ1", "М1"];
const DEFAULT_SCENARIO_VIEW = { showRc: true, showSw: true, showSig: true };

function getScenarioViewState() {
  const cur = window.scenarioViewState || {};
  const merged = { ...DEFAULT_SCENARIO_VIEW, ...cur };
  window.scenarioViewState = merged;
  return merged;
}

function setScenarioViewState(next) {
  window.scenarioViewState = { ...getScenarioViewState(), ...next };
}

function uniq(items) {
  return Array.from(new Set((items || []).filter(Boolean)));
}

function getLayoutData() {
  return window.stationLayoutData || null;
}

async function ensureScenarioLayoutLoaded() {
  const layout = getLayoutData();
  if (layout && Array.isArray(layout.rc_catalog) && Array.isArray(layout.switch_catalog) && Array.isArray(layout.signal_catalog)) {
    return layout;
  }
  const station = (window.scenario && window.scenario.station) ? window.scenario.station : "Visochino";
  const resp = await fetch(`/station-layout?station=${encodeURIComponent(station)}&_ts=${Date.now()}`, {
    cache: "no-store",
  });
  if (!resp.ok) throw new Error(`station-layout HTTP ${resp.status}`);
  const data = await resp.json();
  window.stationLayoutData = data;
  return data;
}

function asSwitchStateKey(swName) {
  const s = String(swName || "");
  return /^Sw/i.test(s) ? s : `Sw${s}`;
}

function getSwitchStateValue(step, swId) {
  const src = step?.switch_states || {};
  if (Object.prototype.hasOwnProperty.call(src, swId)) return src[swId];
  const raw = String(swId || "");
  if (/^Sw/i.test(raw)) {
    const alt = raw.slice(2);
    if (Object.prototype.hasOwnProperty.call(src, alt)) return src[alt];
  } else {
    const alt = asSwitchStateKey(raw);
    if (Object.prototype.hasOwnProperty.call(src, alt)) return src[alt];
  }
  return undefined;
}

function isManeuverSignal(sigId) {
  const s = String(sigId || "").toUpperCase();
  return s.startsWith("М");
}

function getDefaultSignalState(sigId) {
  return isManeuverSignal(sigId) ? 3 : 15;
}

function escCss(value) {
  const s = String(value || "");
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") return CSS.escape(s);
  return s.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function pickColumnsFromScenario(scn) {
  const rc = [];
  const sw = [];
  const sig = [];
  (scn?.steps || []).forEach((step) => {
    Object.keys(step?.rc_states || {}).forEach((k) => rc.push(k));
    Object.keys(step?.switch_states || {}).forEach((k) => sw.push(asSwitchStateKey(k)));
    Object.keys(step?.signal_states || {}).forEach((k) => sig.push(k));
  });
  return { rc: uniq(rc), sw: uniq(sw), sig: uniq(sig) };
}

function pickColumnsFromLayout() {
  const layout = getLayoutData();
  if (!layout) return { rc: [], sw: [], sig: [] };
  const rc = uniq(layout.rc_catalog || []);
  const sw = uniq((layout.switch_catalog || []).map((x) => asSwitchStateKey(x)));
  const sig = uniq(layout.signal_catalog || []);
  return { rc, sw, sig };
}

function getScenarioColumns() {
  const fromScenario = pickColumnsFromScenario(window.scenario || scenario);
  const fromLayout = pickColumnsFromLayout();
  const baseRc = uniq([...(fromLayout.rc || []), ...(fromScenario.rc || [])]);
  const baseSw = uniq([...(fromLayout.sw || []), ...(fromScenario.sw || [])]);
  const baseSig = uniq([...(fromLayout.sig || []), ...(fromScenario.sig || [])]);

  return {
    rc: baseRc.length ? baseRc : DEFAULT_RC_IDS,
    sw: baseSw.length ? baseSw : DEFAULT_SW_IDS,
    sig: baseSig.length ? baseSig : DEFAULT_SIG_IDS,
  };
}

function makeRcInput(value) {
  const td = document.createElement("td");
  const input = document.createElement("input");
  input.type = "number";
  input.step = "1";
  input.min = "0";
  input.max = "8";
  input.value = value !== undefined && value !== null ? String(value) : "3";
  input.addEventListener("change", () => {
    let v = Number(input.value || "3");
    if (Number.isNaN(v)) v = 3;
    if (v < 0) v = 0;
    if (v > 8) v = 8;
    input.value = String(v);
    if (window.applyRcStateClass) window.applyRcStateClass(td, v);
  });
  td.appendChild(input);
  if (window.applyRcStateClass) window.applyRcStateClass(td, Number(input.value || "3"));
  return { td, input };
}

function makeSwitchSelect(value) {
  const td = document.createElement("td");
  const sel = document.createElement("select");
  const states = Array.isArray(window.SW_VALID_STATES) ? window.SW_VALID_STATES : [0, 1, 2, 3, 4, 5, 6, 7, 8];
  states.forEach((code) => {
    const opt = document.createElement("option");
    opt.value = String(code);
    opt.textContent = String(code);
    sel.appendChild(opt);
  });
  sel.value = value !== undefined && value !== null ? String(value) : "3";
  sel.addEventListener("change", () => {
    td.classList.remove("sw-state-plus", "sw-state-minus", "sw-state-nocontrol");
    if (window.swClassForValue) td.classList.add(window.swClassForValue(Number(sel.value || "3")));
  });
  td.appendChild(sel);
  if (window.swClassForValue) td.classList.add(window.swClassForValue(Number(sel.value || "3")));
  return { td, sel };
}

function makeSignalSelect(value, signalId) {
  const td = document.createElement("td");
  const sel = document.createElement("select");
  const states = isManeuverSignal(signalId)
    ? [0, 1, 2, 3, 4, 5, 6, 7]
    : (Array.isArray(window.SIGNAL_VALID_STATES)
      ? window.SIGNAL_VALID_STATES
      : [0, 1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 27]);
  states.forEach((code) => {
    const opt = document.createElement("option");
    opt.value = String(code);
    opt.textContent = String(code);
    sel.appendChild(opt);
  });
  const defaultValue = getDefaultSignalState(signalId);
  sel.value = value !== undefined && value !== null ? String(value) : String(defaultValue);
  sel.addEventListener("change", () => {
    td.classList.remove(
      "signal-free", "signal-stop", "signal-nocontrol", "signal-maneuver-forbidden",
      "signal-maneuver-allowed", "signal-maneuver-failure", "signal-open", "signal-closed", "signal-warning",
    );
    if (window.applySignalClass) {
      const signalCode = isManeuverSignal(signalId) ? 3 : 4;
      const probe = document.createElement("div");
      window.applySignalClass(probe, Number(sel.value || String(defaultValue)), signalCode);
      probe.classList.forEach((x) => td.classList.add(x));
    }
  });
  td.appendChild(sel);
  sel.dispatchEvent(new Event("change"));
  return { td, sel };
}

function rebuildScenarioHeader(columns) {
  const table = document.getElementById("scenariotable");
  if (!table) return;
  const thead = table.querySelector("thead");
  if (!thead) return;

  const tr = document.createElement("tr");
  const push = (txt, cls = "") => {
    const th = document.createElement("th");
    th.textContent = txt;
    if (cls) th.classList.add(cls);
    tr.appendChild(th);
  };

  push("dt, s");
  columns.rc.forEach((rcId) => push(rcId, "col-rc"));
  columns.sw.forEach((swId) => push(swId, "col-sw"));
  columns.sig.forEach((sigId) => push(sigId, "col-sig"));
  push("Actions");

  thead.innerHTML = "";
  thead.appendChild(tr);
}

function applyScenarioColumnVisibility() {
  const table = document.getElementById("scenariotable");
  if (!table) return;
  const view = getScenarioViewState();
  table.querySelectorAll(".col-rc").forEach((el) => el.classList.toggle("col-hidden", !view.showRc));
  table.querySelectorAll(".col-sw").forEach((el) => el.classList.toggle("col-hidden", !view.showSw));
  table.querySelectorAll(".col-sig").forEach((el) => el.classList.toggle("col-hidden", !view.showSig));
}

function ensureScenarioControls() {
  const root = document.getElementById("scenario-column-controls");
  if (!root) return;
  const view = getScenarioViewState();
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

  mkCheck("RC", view.showRc, (v) => { setScenarioViewState({ showRc: v }); applyScenarioColumnVisibility(); });
  mkCheck("Стрелки", view.showSw, (v) => { setScenarioViewState({ showSw: v }); applyScenarioColumnVisibility(); });
  mkCheck("Сигналы", view.showSig, (v) => { setScenarioViewState({ showSig: v }); applyScenarioColumnVisibility(); });
}

function addScenarioRow(tbody, step, columns) {
  const tr = document.createElement("tr");

  const tdDt = document.createElement("td");
  const inpDt = document.createElement("input");
  inpDt.type = "number";
  inpDt.min = "0.1";
  inpDt.step = "0.1";
  inpDt.value = step?.t ?? 1;
  inpDt.dataset.kind = "dt";
  tdDt.appendChild(inpDt);
  tr.appendChild(tdDt);

  columns.rc.forEach((rcId) => {
    const { td, input } = makeRcInput(step?.rc_states?.[rcId] ?? 3);
    td.classList.add("col-rc");
    input.dataset.kind = "rc";
    input.dataset.key = rcId;
    tr.appendChild(td);
  });

  columns.sw.forEach((swId) => {
    const { td, sel } = makeSwitchSelect(getSwitchStateValue(step, swId) ?? 3);
    td.classList.add("col-sw");
    sel.dataset.kind = "sw";
    sel.dataset.key = swId;
    tr.appendChild(td);
  });

  columns.sig.forEach((sigId) => {
    const { td, sel } = makeSignalSelect(
      step?.signal_states?.[sigId] ?? getDefaultSignalState(sigId),
      sigId
    );
    td.classList.add("col-sig");
    sel.dataset.kind = "sig";
    sel.dataset.key = sigId;
    tr.appendChild(td);
  });

  const tdAction = document.createElement("td");
  const btnDel = document.createElement("button");
  btnDel.type = "button";
  btnDel.textContent = "✕";
  btnDel.title = "Удалить строку";
  btnDel.style.color = "red";
  btnDel.style.fontWeight = "bold";
  btnDel.onclick = () => deleteRow(tr);
  tdAction.appendChild(btnDel);
  tr.appendChild(tdAction);

  tbody.appendChild(tr);
  scenarioTableRows.push(tr);
}

function extractStepFromRow(tr, columns) {
  const dtInput = tr.querySelector('input[data-kind="dt"]');
  const t = parseFloat(dtInput?.value || "0");
  if (!t || t <= 0) return null;

  const rc_states = {};
  const switch_states = {};
  const signal_states = {};

  columns.rc.forEach((rcId) => {
    const el = tr.querySelector(`input[data-kind="rc"][data-key="${escCss(rcId)}"]`);
    const v = parseInt(el?.value || "3", 10);
    rc_states[rcId] = Number.isNaN(v) ? 3 : v;
  });
  columns.sw.forEach((swId) => {
    const el = tr.querySelector(`select[data-kind="sw"][data-key="${escCss(swId)}"]`);
    const v = parseInt(el?.value || "3", 10);
    switch_states[swId] = Number.isNaN(v) ? 3 : v;
  });
  columns.sig.forEach((sigId) => {
    const el = tr.querySelector(`select[data-kind="sig"][data-key="${escCss(sigId)}"]`);
    const fallback = getDefaultSignalState(sigId);
    const v = parseInt(el?.value || String(fallback), 10);
    signal_states[sigId] = Number.isNaN(v) ? fallback : v;
  });
  return {
    t,
    rc_states,
    switch_states,
    modes: {},
    signal_states,
  };
}

function deleteRow(tr) {
  const idx = scenarioTableRows.indexOf(tr);
  if (idx === -1) return;
  tr.remove();
  scenarioTableRows.splice(idx, 1);
  applyScenarioTableToJson();
}

async function initScenarioTable() {
  const tbody = document.querySelector("#scenariotable tbody");
  if (!tbody) return;

  if (window.scenario) scenario = window.scenario;
  try {
    await ensureScenarioLayoutLoaded();
  } catch (e) {
    console.error("Failed to load station-layout for scenario table", e);
  }
  const columns = getScenarioColumns();
  window.scenarioColumns = columns;
  ensureScenarioControls();
  rebuildScenarioHeader(columns);

  scenarioTableRows = [];
  tbody.innerHTML = "";
  if (Array.isArray(scenario.steps) && scenario.steps.length > 0) {
    scenario.steps.forEach((s) => addScenarioRow(tbody, s, columns));
  } else {
    addScenarioRow(tbody, null, columns);
  }
  applyScenarioColumnVisibility();

  const addBtn = document.getElementById("addsteprow");
  if (addBtn) addBtn.onclick = () => addScenarioRow(tbody, null, columns);

  const repeatBtn = document.getElementById("repeatprevrow");
  if (repeatBtn) {
    repeatBtn.onclick = () => {
      if (!scenarioTableRows.length) return;
      const lastTr = scenarioTableRows[scenarioTableRows.length - 1];
      const step = extractStepFromRow(lastTr, columns);
      if (step) addScenarioRow(tbody, step, columns);
      applyScenarioColumnVisibility();
    };
  }

  const applyBtn = document.getElementById("applyscenariotable");
  if (applyBtn) applyBtn.onclick = () => applyScenarioTableToJson();
}

async function rebuildScenarioTableFromScenario() {
  await initScenarioTable();
  if (typeof renderScenarioTextarea === "function") renderScenarioTextarea();
}

function applyScenarioTableToJson(silent = false) {
  const tbody = document.querySelector("#scenariotable tbody");
  if (!tbody) return;
  if (window.scenario) scenario = window.scenario;

  const columns = window.scenarioColumns || getScenarioColumns();
  const rows = Array.from(tbody.querySelectorAll("tr"));
  scenario.steps = rows.map((tr) => extractStepFromRow(tr, columns)).filter(Boolean);
  window.scenario = scenario;

  if (typeof renderScenarioTextarea === "function") renderScenarioTextarea();
  if (!silent) alert(`Таблица сценария применена: ${scenario.steps.length} шаг(ов).`);
}

window.initScenarioTable = initScenarioTable;
window.rebuildScenarioTableFromScenario = rebuildScenarioTableFromScenario;
window.applyScenarioTableToJson = applyScenarioTableToJson;
