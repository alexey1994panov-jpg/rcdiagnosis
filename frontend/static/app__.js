// Базовый шаблон сценария
let scenario = {
  station: "Visochino",
  target_rc: "1P",
  dt: 1,
  options: {}, // заполняется с бэка через /defaults
  steps: [],
};

let lastTimeline = [];
let selectedIndex = -1;
let timelineRows = [];
let scenarioTableRows = [];

// допустимые состояния для РЦ / стрелок
const RC_VALID_STATES = [0, 1, 2, 3, 4, 5, 6, 7, 8];
const SW_VALID_STATES = [0, 1, 2, 3, 4, 5, 6, 7, 8];

// --- Загрузка дефолтов с бэка ---

async function loadDefaults() {
  try {
    const resp = await fetch("/defaults");
    if (!resp.ok) {
      console.error("Failed to load defaults, status", resp.status);
      return;
    }
    const data = await resp.json();

    // сохранить в scenario.options
    scenario.options = { ...data };

    // утилита для расстановки значений
    function setVal(id, key, type = "number") {
      const el = document.getElementById(id);
      if (!el || !(key in data)) return;
      if (type === "checkbox") {
        el.checked = Boolean(data[key]);
      } else {
        el.value = String(data[key]);
      }
    }

    // ЛЗ v1
    setVal("t_s0101", "t_s0101");
    setVal("t_lz01", "t_lz01");
    setVal("t_kon_v1", "t_kon_v1");
    setVal("t_pause_v1", "t_pause_v1");
    setVal("enable_v1", "enable_v1", "checkbox");

    // ЛЗ v2
    setVal("t_s0102", "t_s0102");
    setVal("t_s0202", "t_s0202");
    setVal("t_lz02", "t_lz02");
    setVal("t_kon_v2", "t_kon_v2");
    setVal("t_pause_v2", "t_pause_v2");
    setVal("enable_v2", "enable_v2", "checkbox");

    // ЛЗ v3
    setVal("t_s0103", "t_s0103");
    setVal("t_s0203", "t_s0203");
    setVal("t_lz03", "t_lz03");
    setVal("t_kon_v3", "t_kon_v3");
    setVal("t_pause_v3", "t_pause_v3");
    setVal("enable_v3", "enable_v3", "checkbox");

    // ЛЗ v6
    setVal("t_s06", "t_s06");
    setVal("t_lz06", "t_lz06");
    setVal("t_kon_v6", "t_kon_v6");
    setVal("enable_v6", "enable_v6", "checkbox");

    // ЛЗ v8
    setVal("t_s0108", "t_s0108");
    setVal("t_s0208", "t_s0208");
    setVal("t_lz08", "t_lz08");
    setVal("t_kon_v8", "t_kon_v8");
    setVal("t_pause_v8", "t_pause_v8");
    setVal("enable_v8", "enable_v8", "checkbox");

    // ЛС v1
    setVal("t_c0101_ls", "t_c0101_ls");
    setVal("t_ls01", "t_ls01");
    setVal("t_kon_ls1", "t_kon_ls1");
    setVal("t_pause_ls1", "t_pause_ls1");
    setVal("enable_ls1", "enable_ls1", "checkbox");

    // ЛС v2
    setVal("t_s0102_ls", "t_s0102_ls");
    setVal("t_s0202_ls", "t_s0202_ls");
    setVal("t_ls0102", "t_ls0102");
    setVal("t_ls0202", "t_ls0202");
    setVal("t_kon_ls2", "t_kon_ls2");
    setVal("t_pause_ls2", "t_pause_ls2");
    setVal("enable_ls2", "enable_ls2", "checkbox");

    // ЛС v4
    setVal("t_s0104_ls", "t_s0104_ls");
    setVal("t_s0204_ls", "t_s0204_ls");
    setVal("t_ls0104", "t_ls0104");
    setVal("t_ls0204", "t_ls0204");
    setVal("t_kon_ls4", "t_kon_ls4");
    setVal("t_pause_ls4", "t_pause_ls4");
    setVal("enable_ls4", "enable_ls4", "checkbox");

    // ЛС v9
    setVal("t_s0109_ls", "t_s0109_ls");
    setVal("t_s0209_ls", "t_s0209_ls");
    setVal("t_ls0109", "t_ls0109");
    setVal("t_ls0209", "t_ls0209");
    setVal("t_kon_ls9", "t_kon_ls9");
    setVal("t_pause_ls9", "t_pause_ls9");
    setVal("enable_ls9", "enable_ls9", "checkbox");

    // Исключения ЛЗ
    setVal("t_mu", "t_mu");
    setVal("t_recent_ls", "t_recent_ls");
    setVal("t_min_maneuver_v8", "t_min_maneuver_v8");
    setVal("enable_lz_exc_mu", "enable_lz_exc_mu", "checkbox");
    setVal("enable_lz_exc_recent_ls", "enable_lz_exc_recent_ls", "checkbox");
    setVal("enable_lz_exc_dsp", "enable_lz_exc_dsp", "checkbox");

    // Исключения ЛС
    setVal("enable_ls_exc_mu", "enable_ls_exc_mu", "checkbox");
    setVal("enable_ls_exc_after_lz", "enable_ls_exc_after_lz", "checkbox");
    setVal("enable_ls_exc_dsp", "enable_ls_exc_dsp", "checkbox");

    // Перерисуем JSON c этими дефолтами
    renderScenarioTextarea();
  } catch (e) {
    console.error("Failed to load defaults", e);
  }
}

// --- Чтение параметров из формы ---

function updateOptionsFromForm() {
  // ЛЗ v1
  const t_s0101 = parseFloat(document.getElementById("t_s0101").value || "0");
  const t_lz01 = parseFloat(document.getElementById("t_lz01").value || "0");
  const t_kon_v1 = parseFloat(document.getElementById("t_kon_v1").value || "0");
  const t_pause_v1 = parseFloat(document.getElementById("t_pause_v1").value || "0");
  const enable_v1 = document.getElementById("enable_v1").checked;

  // ЛЗ v2
  const t_s0102 = parseFloat(document.getElementById("t_s0102").value || "0");
  const t_s0202 = parseFloat(document.getElementById("t_s0202").value || "0");
  const t_lz02 = parseFloat(document.getElementById("t_lz02").value || "0");
  const t_kon_v2 = parseFloat(document.getElementById("t_kon_v2").value || "0");
  const t_pause_v2 = parseFloat(document.getElementById("t_pause_v2").value || "0");
  const enable_v2 = document.getElementById("enable_v2").checked;

  // ЛЗ v3
  const t_s0103 = parseFloat(document.getElementById("t_s0103").value || "0");
  const t_s0203 = parseFloat(document.getElementById("t_s0203").value || "0");
  const t_lz03 = parseFloat(document.getElementById("t_lz03").value || "0");
  const t_kon_v3 = parseFloat(document.getElementById("t_kon_v3").value || "0");
  const t_pause_v3 = parseFloat(document.getElementById("t_pause_v3").value || "0");
  const enable_v3 = document.getElementById("enable_v3").checked;

  // ЛЗ v6
  const t_s06 = parseFloat(document.getElementById("t_s06").value || "0");
  const t_lz06 = parseFloat(document.getElementById("t_lz06").value || "0");
  const t_kon_v6 = parseFloat(document.getElementById("t_kon_v6").value || "0");
  const enable_v6 = document.getElementById("enable_v6").checked;

  // ЛЗ v8
  const t_s0108 = parseFloat(document.getElementById("t_s0108").value || "0");
  const t_s0208 = parseFloat(document.getElementById("t_s0208").value || "0");
  const t_lz08 = parseFloat(document.getElementById("t_lz08").value || "0");
  const t_kon_v8 = parseFloat(document.getElementById("t_kon_v8").value || "0");
  const t_pause_v8 = parseFloat(document.getElementById("t_pause_v8").value || "0");
  const enable_v8 = document.getElementById("enable_v8").checked;

  // ЛС v1
  const t_c0101_ls = parseFloat(document.getElementById("t_c0101_ls").value || "0");
  const t_ls01 = parseFloat(document.getElementById("t_ls01").value || "0");
  const t_kon_ls1 = parseFloat(document.getElementById("t_kon_ls1").value || "0");
  const t_pause_ls1 = parseFloat(document.getElementById("t_pause_ls1").value || "0");
  const enable_ls1 = document.getElementById("enable_ls1").checked;

  // ЛС v2
  const t_s0102_ls = parseFloat(document.getElementById("t_s0102_ls").value || "0");
  const t_s0202_ls = parseFloat(document.getElementById("t_s0202_ls").value || "0");
  const t_ls0102 = parseFloat(document.getElementById("t_ls0102").value || "0");
  const t_ls0202 = parseFloat(document.getElementById("t_ls0202").value || "0");
  const t_kon_ls2 = parseFloat(document.getElementById("t_kon_ls2").value || "0");
  const t_pause_ls2 = parseFloat(document.getElementById("t_pause_ls2").value || "0");
  const enable_ls2 = document.getElementById("enable_ls2").checked;

  // ЛС v4
  const t_s0104_ls = parseFloat(document.getElementById("t_s0104_ls").value || "0");
  const t_s0204_ls = parseFloat(document.getElementById("t_s0204_ls").value || "0");
  const t_ls0104 = parseFloat(document.getElementById("t_ls0104").value || "0");
  const t_ls0204 = parseFloat(document.getElementById("t_ls0204").value || "0");
  const t_kon_ls4 = parseFloat(document.getElementById("t_kon_ls4").value || "0");
  const t_pause_ls4 = parseFloat(document.getElementById("t_pause_ls4").value || "0");
  const enable_ls4 = document.getElementById("enable_ls4").checked;

  // ЛС v9
  const t_s0109_ls = parseFloat(document.getElementById("t_s0109_ls").value || "0");
  const t_s0209_ls = parseFloat(document.getElementById("t_s0209_ls").value || "0");
  const t_ls0109 = parseFloat(document.getElementById("t_ls0109").value || "0");
  const t_ls0209 = parseFloat(document.getElementById("t_ls0209").value || "0");
  const t_kon_ls9 = parseFloat(document.getElementById("t_kon_ls9").value || "0");
  const t_pause_ls9 = parseFloat(document.getElementById("t_pause_ls9").value || "0");
  const enable_ls9 = document.getElementById("enable_ls9").checked;

  // Исключения ЛЗ
  const t_mu = parseFloat(document.getElementById("t_mu").value || "0");
  const t_recent_ls = parseFloat(document.getElementById("t_recent_ls").value || "0");
  const t_min_maneuver_v8 = parseFloat(
    document.getElementById("t_min_maneuver_v8").value || "0",
  );

  const enable_lz_exc_mu = document.getElementById("enable_lz_exc_mu").checked;
  const enable_lz_exc_recent_ls =
    document.getElementById("enable_lz_exc_recent_ls").checked;
  const enable_lz_exc_dsp = document.getElementById("enable_lz_exc_dsp").checked;

  // Исключения ЛС
  const enable_ls_exc_mu = document.getElementById("enable_ls_exc_mu").checked;
  const enable_ls_exc_after_lz =
    document.getElementById("enable_ls_exc_after_lz").checked;
  const enable_ls_exc_dsp = document.getElementById("enable_ls_exc_dsp").checked;

  scenario.options = {
    t_s0101,
    t_lz01,
    t_kon_v1,
    t_pause_v1,
    enable_v1,

    t_s0102,
    t_s0202,
    t_lz02,
    t_kon_v2,
    t_pause_v2,
    enable_v2,

    t_s0103,
    t_s0203,
    t_lz03,
    t_kon_v3,
    t_pause_v3,
    enable_v3,

    // ЛЗ v6
    t_s06,
    t_lz06,
    t_kon_v6,
    enable_v6,

    t_s0108,
    t_s0208,
    t_lz08,
    t_kon_v8,
    t_pause_v8,
    enable_v8,

    t_c0101_ls,
    t_ls01,
    t_kon_ls1,
    t_pause_ls1,
    enable_ls1,

    t_s0102_ls,
    t_s0202_ls,
    t_ls0102,
    t_ls0202,
    t_kon_ls2,
    t_pause_ls2,
    enable_ls2,

    t_s0104_ls,
    t_s0204_ls,
    t_ls0104,
    t_ls0204,
    t_kon_ls4,
    t_pause_ls4,
    enable_ls4,

    t_s0109_ls,
    t_s0209_ls,
    t_ls0109,
    t_ls0209,
    t_kon_ls9,
    t_pause_ls9,
    enable_ls9,

    t_mu,
    t_recent_ls,
    t_min_maneuver_v8,

    enable_lz_exc_mu,
    enable_lz_exc_recent_ls,
    enable_lz_exc_dsp,

    enable_ls_exc_mu,
    enable_ls_exc_after_lz,
    enable_ls_exc_dsp,
  };
}

function renderScenarioTextarea() {
  // синхронизация локальной переменной со ссылкой в window
  if (window.scenario) {
    scenario = window.scenario;
  }

  if (typeof updateOptionsFromForm === "function") {
    updateOptionsFromForm();
  }

  const area = document.getElementById("scenariotext");
  if (area) {
    area.value = JSON.stringify(scenario, null, 2);
  }

  console.log("renderScenarioTextarea: scenario.steps.length =", Array.isArray(scenario.steps) ? scenario.steps.length : "n/a");
}
window.renderScenarioTextarea = renderScenarioTextarea;

function clearScenario() {
  scenario.steps = [];
  renderScenarioTextarea();
}

// быстрый ввод одного шага (оставляем, но он теперь синхронизируется с таблицей)
function addStepFromForm() {
  const t = parseInt(document.getElementById("step_t").value || "0", 10);
  const rc_10_12 = parseInt(document.getElementById("rc_10_12sp").value || "0", 10);
  const rc_1p = parseInt(document.getElementById("rc_1p").value || "0", 10);
  const rc_1_7 = parseInt(document.getElementById("rc_1_7sp").value || "0", 10);
  const sw10 = parseInt(document.getElementById("sw_10").value || "0", 10);
  const sw1 = parseInt(document.getElementById("sw_1").value || "0", 10);
  const sw5 = parseInt(document.getElementById("sw_5").value || "0", 10);

  const step = {
    t,
    rc_states: {
      "10-12SP": rc_10_12,
      "1P": rc_1p,
      "1-7SP": rc_1_7,
    },
    switch_states: {
      Sw10: sw10,
      Sw1: sw1,
      Sw5: sw5,
    },
    modes: {},
    mu: {},
    dispatcher_control_state: undefined,
    auto_actions: undefined,
  };

  scenario.steps.push(step);
  renderScenarioTextarea();
  rebuildScenarioTableFromScenario();
}

// --- Табличный ввод сценария ---

function initScenarioTable() {
  const tbody = document.querySelector("#scenario_table tbody");
  if (!tbody) return;

  scenarioTableRows = [];
  tbody.innerHTML = "";

  function makeStateInput(value, isSwitch, onChange) {
    const td = document.createElement("td");
    const input = document.createElement("input");
    input.type = "number";
    input.step = "1";
    input.min = "0";
    input.max = "8";
    input.value = value !== undefined && value !== null ? String(value) : "0";

    function applyColor() {
      const v = Number(input.value || "0");
      td.classList.remove(
        "rc-state-free",
        "rc-state-occupied",
        "rc-state-nocontrol",
        "sw-state-plus",
        "sw-state-minus",
        "sw-state-nocontrol",
      );
      if (isSwitch) {
        td.classList.add(swClassForValue(v));
      } else {
        applyRcStateClass(td, v);
      }
    }

    input.addEventListener("change", () => {
      let v = Number(input.value || "0");
      if (Number.isNaN(v)) v = 0;
      if (v < 0) v = 0;
      if (v > 8) v = 8;
      input.value = String(v);
      applyColor();
      if (onChange) onChange(v);
    });

    td.appendChild(input);
    applyColor();
    return { td, input };
  }

  function makeEnumSelect(options, value) {
    const td = document.createElement("td");
    const sel = document.createElement("select");
    options.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = String(v);
      opt.textContent = String(v);
      sel.appendChild(opt);
    });
    sel.value = value !== undefined && value !== null ? String(value) : String(options[0]);
    td.appendChild(sel);
    return { td, sel };
  }

  function addRow(step) {
    const tr = document.createElement("tr");

    // Δt
    const tdDt = document.createElement("td");
    const inpDt = document.createElement("input");
    inpDt.type = "number";
    inpDt.min = "0.1";
    inpDt.step = "0.1";
    inpDt.value = step?.t ?? 1;
    tdDt.appendChild(inpDt);
    tr.appendChild(tdDt);

    const rcPrev = step?.rc_states?.["10-12SP"] ?? 0;
    const rcCtrl = step?.rc_states?.["1P"] ?? 0;
    const rcNext = step?.rc_states?.["1-7SP"] ?? 0;
    const sw10 = step?.switch_states?.["Sw10"] ?? 0;
    const sw1 = step?.switch_states?.["Sw1"] ?? 0;
    const sw5 = step?.switch_states?.["Sw5"] ?? 0;

    const { td: tdPrev } = makeStateInput(rcPrev, false);
    const { td: tdCtrl } = makeStateInput(rcCtrl, false);
    const { td: tdNext } = makeStateInput(rcNext, false);
    const { td: tdSw10 } = makeStateInput(sw10, true);
    const { td: tdSw1 } = makeStateInput(sw1, true);
    const { td: tdSw5 } = makeStateInput(sw5, true);

    tr.appendChild(tdPrev);
    tr.appendChild(tdCtrl);
    tr.appendChild(tdNext);
    tr.appendChild(tdSw10);
    tr.appendChild(tdSw1);
    tr.appendChild(tdSw5);

    const muPrev = step?.mu?.["10-12SP"] ?? 3;
    const muCurr = step?.mu?.["1P"] ?? 3;
    const muNext = step?.mu?.["1-7SP"] ?? 3;
    const dspVal = step?.dispatcher_control_state ?? 4;
    const nasVal = step?.auto_actions?.NAS ?? 4;
    const chasVal = step?.auto_actions?.CHAS ?? 4;

    const { td: tdMuPrev, sel: selMuPrev } = makeEnumSelect([1, 2, 3, 4], muPrev);
    const { td: tdMuCurr, sel: selMuCurr } = makeEnumSelect([1, 2, 3, 4], muCurr);
    const { td: tdMuNext, sel: selMuNext } = makeEnumSelect([1, 2, 3, 4], muNext);
    const { td: tdDsp, sel: selDsp } = makeEnumSelect([0, 1, 2, 3, 4], dspVal);
    const { td: tdNas, sel: selNas } = makeEnumSelect([0, 3, 4], nasVal);
    const { td: tdChas, sel: selChas } = makeEnumSelect([0, 3, 4], chasVal);

    tr.appendChild(tdMuPrev);
    tr.appendChild(tdMuCurr);
    tr.appendChild(tdMuNext);
    tr.appendChild(tdDsp);
    tr.appendChild(tdNas);
    tr.appendChild(tdChas);

    tbody.appendChild(tr);
    scenarioTableRows.push(tr);
  }

  if (Array.isArray(scenario.steps) && scenario.steps.length > 0) {
    scenario.steps.forEach((s) => addRow(s));
  } else {
    addRow(null);
  }

  const addBtn = document.getElementById("add_step_row");
  if (addBtn) addBtn.onclick = () => addRow(null);

  const repeatBtn = document.getElementById("repeat_prev_row");
  if (repeatBtn) {
    repeatBtn.onclick = () => {
      if (!scenarioTableRows.length) return;
      const lastTr = scenarioTableRows[scenarioTableRows.length - 1];
      const inputs = Array.from(lastTr.querySelectorAll("input,select"));
      const step = extractStepFromRow(inputs);
      addRow(step);
    };
  }

  const applyBtn = document.getElementById("apply_scenario_table");
  if (applyBtn) applyBtn.onclick = applyScenarioTableToJson;
}

function extractStepFromRow(inputs) {
  // порядок элементов должен совпадать с initScenarioTable
  const [
    inpDt,
    inpPrev,
    inpCtrl,
    inpNext,
    inpSw10,
    inpSw1,
    inpSw5,
    selMuPrev,
    selMuCurr,
    selMuNext,
    selDsp,
    selNas,
    selChas,
  ] = inputs;

  const t = parseFloat(inpDt.value || "0");
  if (!t || t <= 0) return null;

  const rc_states = {};
  const switch_states = {};
  const mu = {};
  const auto_actions = {};

  const vPrev = parseInt(inpPrev.value || "0", 10);
  const vCtrl = parseInt(inpCtrl.value || "0", 10);
  const vNext = parseInt(inpNext.value || "0", 10);
  const vSw10 = parseInt(inpSw10.value || "0", 10);
  const vSw1 = parseInt(inpSw1.value || "0", 10);
  const vSw5 = parseInt(inpSw5.value || "0", 10);

  if (vPrev) rc_states["10-12SP"] = vPrev;
  if (vCtrl) rc_states["1P"] = vCtrl;
  if (vNext) rc_states["1-7SP"] = vNext;
  if (vSw10) switch_states["Sw10"] = vSw10;
  if (vSw1) switch_states["Sw1"] = vSw1;
  if (vSw5) switch_states["Sw5"] = vSw5;

  const vMuPrev = parseInt(selMuPrev.value || "3", 10);
  const vMuCurr = parseInt(selMuCurr.value || "3", 10);
  const vMuNext = parseInt(selMuNext.value || "3", 10);

  mu["10-12SP"] = vMuPrev;
  mu["1P"] = vMuCurr;
  mu["1-7SP"] = vMuNext;

  const vDsp = parseInt(selDsp.value || "4", 10);
  const vNas = parseInt(selNas.value || "4", 10);
  const vChas = parseInt(selChas.value || "4", 10);

  auto_actions.NAS = vNas;
  auto_actions.CHAS = vChas;

  return {
    t,
    rc_states,
    switch_states,
    modes: {},
    mu,
    dispatcher_control_state: vDsp,
    auto_actions,
  };
}

function rebuildScenarioTableFromScenario() {
  const tbody = document.querySelector("#scenariotable tbody");
  if (!tbody) return;

  if (window.scenario) {
    scenario = window.scenario;
  }

  tbody.innerHTML = "";
  scenarioTableRows = [];

  if (Array.isArray(scenario.steps) && scenario.steps.length > 0) {
    scenario.steps.forEach((s) => addScenarioRow(tbody, s));
  } else {
    addScenarioRow(tbody, null);
  }

  if (typeof renderScenarioTextarea === "function") {
    renderScenarioTextarea();
  }

  console.log(
    "rebuildScenarioTableFromScenario: scenario.steps.length =",
    Array.isArray(scenario.steps) ? scenario.steps.length : "n/a"
  );
}
window.rebuildScenarioTableFromScenario = rebuildScenarioTableFromScenario;

function applyScenarioTableToJson() {
  const tbody = document.querySelector("#scenariotable tbody");
  if (!tbody) return;

  const rows = Array.from(tbody.querySelectorAll("tr"));

  const steps = rows
    .map((tr, idx) => {
      const inputs = Array.from(tr.querySelectorAll("input,select"));
      const step = extractStepFromRow(inputs);
      console.log("applyScenarioTableToJson: row", idx, "inputs =", inputs.length, "step =", step);
      return step;
    })
    .filter(Boolean);

  if (window.scenario) {
    scenario = window.scenario;
  }

  scenario.steps = steps;
  window.scenario = scenario;

  if (typeof renderScenarioTextarea === "function") {
    renderScenarioTextarea();
  }

  console.log(
    "applyScenarioTableToJson: processed rows =", rows.length,
    "steps.length =", steps.length,
    "first step =", steps[0] || null
  );
}

// --- Вызов симуляции ---

async function runSimulation() {
  try {
    updateOptionsFromForm();
    const text = document.getElementById("scenario_text").value.trim();
    if (text) {
      scenario = JSON.parse(text);
    }

    const resp = await fetch("/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scenario),
    });

    if (!resp.ok) {
      alert("Ошибка API: " + resp.status);
      return;
    }

    const timeline = await resp.json();
    renderTimeline(timeline);
  } catch (e) {
    console.error(e);
    alert("Ошибка парсинга JSON или вызова API");
  }
}

// --- Вспомогательные классы отображения ---

function applyRcStateClass(td, value) {
  const v = Number(value);
  td.classList.remove("rc-state-free", "rc-state-occupied", "rc-state-nocontrol");
  if ([3, 4, 5].includes(v)) {
    td.classList.add("rc-state-free");
  } else if ([6, 7, 8].includes(v)) {
    td.classList.add("rc-state-occupied");
  } else if ([0, 1, 2].includes(v)) {
    td.classList.add("rc-state-nocontrol");
  }
}

function swClassForValue(v) {
  const val = Number(v);
  if ([3, 4, 5].includes(val)) return "sw-state-plus";
  if ([6, 7, 8].includes(val)) return "sw-state-minus";
  return "sw-state-nocontrol";
}

// --- Обновление схемы участка + индикаторы МУ/автодействий ---

function updateTrackScheme(row) {
  const rcStates = row.rc_states || {};
  const swStates = row.switch_states || {};

  const prevId = row.effective_prev_rc || "10-12SP";
  const currId = "1P";
  const nextId = row.effective_next_rc || "1-7SP";

  const prevState = prevId ? rcStates[prevId] ?? "" : "";
  const currState = rcStates[currId] ?? "";
  const nextState = nextId ? rcStates[nextId] ?? "" : "";

  const sw10State = swStates["Sw10"] ?? "";
  const sw1State = swStates["Sw1"] ?? "";
  const sw5State = swStates["Sw5"] ?? "";

  document.getElementById("rc_prev_state_lbl").textContent = prevState || "—";
  document.getElementById("rc_curr_state_lbl").textContent = currState || "—";
  document.getElementById("rc_next_state_lbl").textContent = nextState || "—";

  const sw10Label = document.getElementById("sw10_label");
  const sw1Label = document.getElementById("sw1_label");
  const sw5Label = document.getElementById("sw5_label");

  const sw10Val = document.getElementById("sw10_state_lbl");
  const sw1Val = document.getElementById("sw1_state_lbl");
  const sw5Val = document.getElementById("sw5_state_lbl");

  sw10Val.textContent = sw10State || "—";
  sw1Val.textContent = sw1State || "—";
  sw5Val.textContent = sw5State || "—";

  const prevBlock = document.getElementById("rc_prev_block");
  const currBlock = document.getElementById("rc_curr_block");
  const nextBlock = document.getElementById("rc_next_block");

  [prevBlock, currBlock, nextBlock].forEach((b) => {
    b.classList.remove("rc-state-free", "rc-state-occupied", "rc-state-nocontrol");
  });

  if (prevState !== "") applyRcStateClass(prevBlock, prevState);
  if (currState !== "") applyRcStateClass(currBlock, currState);
  if (nextState !== "") applyRcStateClass(nextBlock, nextState);

  [sw10Label, sw1Label, sw5Label, sw10Val, sw1Val, sw5Val].forEach((el) => {
    el.classList.remove("sw-state-plus", "sw-state-minus", "sw-state-nocontrol");
  });

  if (sw10State !== "") {
    const cls = swClassForValue(sw10State);
    sw10Label.classList.add(cls);
    sw10Val.classList.add(cls);
  }

  if (sw1State !== "") {
    const cls = swClassForValue(sw1State);
    sw1Label.classList.add(cls);
    sw1Val.classList.add(cls);
  }

  if (sw5State !== "") {
    const cls = swClassForValue(sw5State);
    sw5Label.classList.add(cls);
    sw5Val.classList.add(cls);
  }

  // индикаторы местного управления и автодействий
  const muPrev = row.mu_state_prev ?? 3;
  const muCurr = row.mu_state ?? 3;
  const muNext = row.mu_state_next ?? 3;
  const nasState = row.nas_state ?? 4;
  const chasState = row.chas_state ?? 4;

  const muPrevEl = document.getElementById("mu_indicator_prev");
  const muCurrEl = document.getElementById("mu_indicator_curr");
  const muNextEl = document.getElementById("mu_indicator_next");
  const nasEl = document.getElementById("nas_indicator");
  const chasEl = document.getElementById("chas_indicator");

  [muPrevEl, muCurrEl, muNextEl, nasEl, chasEl].forEach((el) => {
    if (!el) return;
    el.classList.remove("mu-indicator-active", "aa-indicator-active");
  });

  if (muPrevEl && muPrev === 4) muPrevEl.classList.add("mu-indicator-active");
  if (muCurrEl && muCurr === 4) muCurrEl.classList.add("mu-indicator-active");
  if (muNextEl && muNext === 4) muNextEl.classList.add("mu-indicator-active");

  if (nasEl && nasState === 3) nasEl.classList.add("aa-indicator-active");
  if (chasEl && chasState === 3) chasEl.classList.add("aa-indicator-active");
}

// --- Лента времени ---

function renderTimebar() {
  const container = document.getElementById("timebar_container");
  const info = document.getElementById("timebar_info");
  container.innerHTML = "";
  if (!lastTimeline.length) {
    info.textContent = "Шаг: —";
    return;
  }

  info.textContent = "Шаг: " + (selectedIndex + 1) + " из " + lastTimeline.length;

  lastTimeline.forEach((row, idx) => {
    const seg = document.createElement("div");
    seg.classList.add("timebar-segment");
    if (row.lz_state) seg.classList.add("timebar-segment-lz");

    const flags = row.flags || [];
    if (
      flags.includes("llz_v1_open") ||
      flags.includes("llz_v2_open") ||
      flags.includes("llz_v3_open") ||
      flags.includes("llz_v6_open") ||
      flags.includes("llz_v8_open") ||
      flags.includes("lls_v1_open") ||
      flags.includes("lls_v2_open") ||
      flags.includes("lls_v4_open") ||
      flags.includes("lls_v9_open")
    ) {
      seg.classList.add("timebar-segment-open");
    }

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

    if (flags.some((f) => f.startsWith("lz_suppressed:"))) {
      seg.classList.add("timebar-segment-suppressed");
    }

    if (idx === selectedIndex) seg.classList.add("timebar-segment-selected");

    seg.title = "t=" + row.t + ", variant=" + row.variant;
    seg.addEventListener("click", () => {
      selectedIndex = idx;
      updateSelectionHighlight();
    });

    container.appendChild(seg);
  });
}

function moveSelection(delta) {
  if (!lastTimeline.length) return;
  selectedIndex = Math.min(
    lastTimeline.length - 1,
    Math.max(0, selectedIndex + delta),
  );
  updateSelectionHighlight();
}

function scrollToRow(idx) {
  const tbody = document.querySelector("#timeline_table tbody");
  const rows = tbody.querySelectorAll("tr");
  if (rows[idx]) rows[idx].scrollIntoView({ block: "nearest" });
}

function updateSelectionHighlight() {
  renderTimebar();
  timelineRows.forEach((tr, i) => {
    tr.classList.toggle("selected-row", i === selectedIndex);
  });
  if (selectedIndex >= 0 && lastTimeline[selectedIndex]) {
    updateTrackScheme(lastTimeline[selectedIndex]);
    scrollToRow(selectedIndex);
  }
}

function renderTimeline(timeline) {
  lastTimeline = timeline || [];
  selectedIndex = lastTimeline.length ? 0 : -1;
  timelineRows = [];
  renderTimebar();

  const tbody = document.querySelector("#timeline_table tbody");
  tbody.innerHTML = "";

  lastTimeline.forEach((row, idx) => {
    const tr = document.createElement("tr");
    timelineRows.push(tr);

    const rcStates = row.rc_states || {};
    const swStates = row.switch_states || {};

    const prevId = row.effective_prev_rc || "10-12SP";
    const currId = "1P";
    const nextId = row.effective_next_rc || "1-7SP";

    const prevState = prevId ? rcStates[prevId] ?? "" : "";
    const currState = rcStates[currId] ?? "";
    const nextState = nextId ? rcStates[nextId] ?? "" : "";

    const sw10State = swStates["Sw10"] ?? "";
    const sw1State = swStates["Sw1"] ?? "";
    const sw5State = swStates["Sw5"] ?? "";

    const tdT = document.createElement("td");
    tdT.textContent =
      row.step_duration !== undefined && row.step_duration !== null
        ? row.step_duration
        : "";
    tr.appendChild(tdT);

    const tdLZ = document.createElement("td");
    tdLZ.textContent = row.lz_state ? "1" : "0";
    tr.appendChild(tdLZ);

    const tdVar = document.createElement("td");
    tdVar.textContent = row.variant;
    tr.appendChild(tdVar);

    const tdPrev = document.createElement("td");
    tdPrev.textContent = prevId;
    tr.appendChild(tdPrev);

    const tdPrevState = document.createElement("td");
    tdPrevState.textContent = prevState;
    applyRcStateClass(tdPrevState, prevState);
    tr.appendChild(tdPrevState);

    const tdSw10 = document.createElement("td");
    tdSw10.textContent = sw10State;
    tdSw10.classList.add(swClassForValue(sw10State));
    tr.appendChild(tdSw10);

    const tdCtrl = document.createElement("td");
    tdCtrl.textContent = currId;
    tr.appendChild(tdCtrl);

    const tdCtrlState = document.createElement("td");
    tdCtrlState.textContent = currState;
    applyRcStateClass(tdCtrlState, currState);
    tr.appendChild(tdCtrlState);

    const tdNext = document.createElement("td");
    tdNext.textContent = nextId;
    tr.appendChild(tdNext);

    const tdNextState = document.createElement("td");
    tdNextState.textContent = nextState;
    applyRcStateClass(tdNextState, nextState);
    tr.appendChild(tdNextState);

    const tdSw1 = document.createElement("td");
    tdSw1.textContent = sw1State;
    tdSw1.classList.add(swClassForValue(sw1State));
    tr.appendChild(tdSw1);

    const tdSw5 = document.createElement("td");
    tdSw5.textContent = sw5State;
    tdSw5.classList.add(swClassForValue(sw5State));
    tr.appendChild(tdSw5);

    const tdMuPrev = document.createElement("td");
    tdMuPrev.textContent = row.mu_state_prev ?? "";
    tr.appendChild(tdMuPrev);

    const tdMuCurr = document.createElement("td");
    tdMuCurr.textContent = row.mu_state ?? "";
    tr.appendChild(tdMuCurr);

    const tdMuNext = document.createElement("td");
    tdMuNext.textContent = row.mu_state_next ?? "";
    tr.appendChild(tdMuNext);

    const tdDsp = document.createElement("td");
    tdDsp.textContent = row.dsp_state ?? "";
    tr.appendChild(tdDsp);

    const tdNas = document.createElement("td");
    tdNas.textContent = row.nas_state ?? "";
    tr.appendChild(tdNas);

    const tdChas = document.createElement("td");
    tdChas.textContent = row.chas_state ?? "";
    tr.appendChild(tdChas);

    const tdFlags = document.createElement("td");
    tdFlags.textContent = (row.flags || []).join(", ");
    tr.appendChild(tdFlags);

    const tdDesc = document.createElement("td");
    tdDesc.textContent = describeFlags(row.flags || []);
    tr.appendChild(tdDesc);

    tr.addEventListener("click", () => {
      selectedIndex = idx;
      updateSelectionHighlight();
    });

    tbody.appendChild(tr);
  });

  if (selectedIndex >= 0 && lastTimeline[selectedIndex]) {
    updateSelectionHighlight();
  }
}

// --- Расшифровка флагов ---

function describeFlags(flags) {
  if (!flags || !flags.length) return "";

  const desc = [];

  // ЛЗ v1
  if (flags.includes("llz_v1_open")) desc.push("Открытие ДС ЛЛЗ (вариант 1)");
  if (flags.includes("llz_v1_closed")) desc.push("Завершение ДС ЛЛЗ (вариант 1)");
  if (flags.includes("llz_v1")) desc.push("ДС ЛЛЗ (вариант 1) активно");

  // ЛЗ v2
  if (flags.includes("llz_v2_open")) desc.push("Открытие ДС ЛЛЗ (вариант 2)");
  if (flags.includes("llz_v2_closed")) desc.push("Завершение ДС ЛЛЗ (вариант 2)");
  if (flags.includes("llz_v2")) desc.push("ДС ЛЛЗ (вариант 2) активно");

  // ЛЗ v3
  if (flags.includes("llz_v3_open")) desc.push("Открытие ДС ЛЛЗ (вариант 3)");
  if (flags.includes("llz_v3_closed")) desc.push("Завершение ДС ЛЛЗ (вариант 3)");
  if (flags.includes("llz_v3")) desc.push("ДС ЛЛЗ (вариант 3) активно");

  // ЛЗ v6
  if (flags.includes("llz_v6_open")) desc.push("Открытие ДС ЛЛЗ (вариант 6)");
  if (flags.includes("llz_v6_closed")) desc.push("Завершение ДС ЛЛЗ (вариант 6)");
  if (flags.includes("llz_v6")) desc.push("ДС ЛЛЗ (вариант 6) активно");

  // ЛЗ v8
  if (flags.includes("llz_v8_open")) desc.push("Открытие ДС ЛЛЗ (вариант 8)");
  if (flags.includes("llz_v8_closed")) desc.push("Завершение ДС ЛЛЗ (вариант 8)");
  if (flags.includes("llz_v8")) desc.push("ДС ЛЛЗ (вариант 8) активно");

  // ЛС v1
  if (flags.includes("lls_v1_open")) desc.push("Открытие ДС ЛС (вариант 1)");
  if (flags.includes("lls_v1_closed")) desc.push("Завершение ДС ЛС (вариант 1)");
  if (flags.includes("lls_v1")) desc.push("ДС ЛС (вариант 1) активно");

  // ЛС v2
  if (flags.includes("lls_v2_open")) desc.push("Открытие ДС ЛС (вариант 2)");
  if (flags.includes("lls_v2_closed")) desc.push("Завершение ДС ЛС (вариант 2)");
  if (flags.includes("lls_v2")) desc.push("ДС ЛС (вариант 2) активно");

  // ЛС v4
  if (flags.includes("lls_v4_open")) desc.push("Открытие ДС ЛС (вариант 4)");
  if (flags.includes("lls_v4_closed")) desc.push("Завершение ДС ЛС (вариант 4)");
  if (flags.includes("lls_v4")) desc.push("ДС ЛС (вариант 4) активно");

  // ЛС v9
  if (flags.includes("lls_v9_open")) desc.push("Открытие ДС ЛС (вариант 9)");
  if (flags.includes("lls_v9_closed")) desc.push("Завершение ДС ЛС (вариант 9)");
  if (flags.includes("lls_v9")) desc.push("ДС ЛС (вариант 9) активно");

  // Общие флаги качества ЛЗ
  if (flags.includes("false_lz")) desc.push("ЛЗ при свободной РЦ");
  if (flags.includes("no_lz_when_occupied")) desc.push("Нет ЛЗ при занятой РЦ");
  if (flags.includes("switch_lost_control_with_lz"))
    desc.push("ЛЗ при потере контроля стрелки");

  // Исключения ЛЗ
  flags
    .filter((f) => f.startsWith("lz_suppressed:"))
    .forEach((f) => {
      if (f === "lz_suppressed:dsp_autoaction_timeout") {
        desc.push("ЛЗ подавлена: истечение ожидания ДСП-автодействия");
      } else if (f === "lz_suppressed:recent_ls_on_adjacent") {
        desc.push("ЛЗ подавлена: недавняя ЛС на смежной РЦ");
      } else if (f === "lz_suppressed:local_mu") {
        desc.push("ЛЗ подавлена: местное управление");
      } else {
        desc.push("ЛЗ подавлена исключением (" + f.slice("lz_suppressed:".length) + ")");
      }
    });

  // Исключения ЛС
  flags
    .filter((f) => f.startsWith("ls_suppressed:"))
    .forEach((f) => {
      if (f === "ls_suppressed:ls_exc_mu") {
        desc.push("ЛС подавлена: местное управление");
      } else if (f === "ls_suppressed:ls_exc_after_lz") {
        desc.push("ЛС подавлена: недавняя ЛЗ");
      } else if (f === "ls_suppressed:ls_exc_dsp_autoaction") {
        desc.push("ЛС подавлена: ДСП-исключение");
      } else {
        desc.push("ЛС подавлена исключением (" + f.slice("ls_suppressed:".length) + ")");
      }
    });

  return desc.join("; ");
}

// --- Хранение тестов через API /tests ---

async function apiLoadTests() {
  try {
    const resp = await fetch("/tests");
    if (!resp.ok) {
      console.error("Failed to fetch tests, status", resp.status);
      return [];
    }
    return await resp.json();
  } catch (e) {
    console.error("Failed to load tests", e);
    return [];
  }
}

async function apiSaveTest(testData) {
  try {
    const resp = await fetch("/tests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(testData),
    });
    if (!resp.ok) {
      alert("Ошибка сохранения теста: " + resp.status);
      return null;
    }
    return await resp.json();
  } catch (e) {
    console.error("Failed to save test", e);
    alert("Не удалось сохранить тест");
    return null;
  }
}

async function apiUpdateTestStatus(testId, status, comment) {
  try {
    const resp = await fetch(`/tests/${encodeURIComponent(testId)}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, comment }),
    });
    if (!resp.ok) {
      alert("Ошибка обновления статуса теста: " + resp.status);
    }
  } catch (e) {
    console.error("Failed to update test status", e);
    alert("Не удалось обновить статус теста");
  }
}

async function apiGetTest(testId) {
  try {
    const resp = await fetch(`/tests/${encodeURIComponent(testId)}`);
    if (!resp.ok) {
      alert("Ошибка загрузки теста: " + resp.status);
      return null;
    }
    return await resp.json();
  } catch (e) {
    console.error("Failed to load full test", e);
    alert("Не удалось загрузить тест");
    return null;
  }
}

let cachedTests = [];

function getSelectedTestId() {
  const select = document.getElementById("tests_select");
  if (!select) return null;
  return select.value || null;
}

function updateSelectedTestInfo() {
  const info = document.getElementById("test_info");
  if (!info) return;
  const id = getSelectedTestId();
  const t = cachedTests.find((x) => x.id === id);
  if (!t) {
    info.textContent = "";
    return;
  }
  info.textContent =
    "Вариант: " +
    (t.variant ?? "-") +
    ", направление: " +
    (t.direction || "-") +
    (t.comment ? " | Комментарий: " + t.comment : "") +
    (t.lastStatus ? " | Статус: " + t.lastStatus.toUpperCase() : "");
}

async function renderTestsList() {
  const select = document.getElementById("tests_select");
  const info = document.getElementById("test_info");
  if (!select) return;

  cachedTests = await apiLoadTests();
  select.innerHTML = "";

  if (!cachedTests.length) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "Нет сохранённых тестов";
    select.appendChild(opt);
    if (info) info.textContent = "";
    return;
  }

  cachedTests.forEach((t) => {
    const opt = document.createElement("option");
    opt.value = t.id;
    const status =
      t.lastStatus === "ok"
        ? "✅"
        : t.lastStatus === "fail"
        ? "❌"
        : " ";
    opt.textContent = status + " " + (t.name || t.id);
    select.appendChild(opt);
  });

  updateSelectedTestInfo();
  select.onchange = updateSelectedTestInfo;
}

async function loadSelectedTest() {
  const sel = document.getElementById("testsselect");
  if (!sel || !sel.value) {
    alert("Выберите тест");
    return;
  }

  try {
    const data = await fetchJson(`/tests/${encodeURIComponent(sel.value)}`);

    // Новый формат: сценарий в поле json
    if (data.json) {
      window.scenario = data.json;
    } else if (data.scenario) {
      // Старый формат
      window.scenario = data.scenario;
    } else {
      // Совсем старый формат: сам объект — сценарий
      window.scenario = data;
    }

    console.log("loadSelectedTest: window.scenario keys =", Object.keys(window.scenario || {}));

    if (typeof rebuildScenarioTableFromScenario === "function") {
      try {
        rebuildScenarioTableFromScenario();
      } catch (e) {
        console.error("rebuildScenarioTableFromScenario error", e);
      }
    }

    if (typeof renderScenarioTextarea === "function") {
      renderScenarioTextarea();
    }

    const info = document.getElementById("testinfo");
    if (info) {
      const status = data.lastStatus || "unknown";
      const comment = data.comment || "";
      info.textContent = `Статус: ${status}${comment ? " | " + comment : ""}`;
    }
  } catch (e) {
    console.error("loadSelectedTest error", e);
    alert("Не удалось загрузить тест");
  }
}
window.loadSelectedTest = loadSelectedTest;

async function saveCurrentAsTest() {
  const area = document.getElementById("scenario_text");
  if (!area) return;
  const text = area.value.trim();
  if (!text) {
    alert("Нет JSON для сохранения");
    return;
  }

  let scen;
  try {
    scen = JSON.parse(text);
  } catch (e) {
    alert("Некорректный JSON сценария");
    return;
  }

  const name = prompt("Имя теста:", "Безымянный тест");
  if (!name) return;

  const variantStr = prompt("Целевой вариант (1,2,3,8 или пусто):", "");
  const variant = variantStr ? parseInt(variantStr, 10) : null;

  const direction = prompt("Направление (L2R/R2L/mixed):", "L2R") || "L2R";
  const comment = prompt("Комментарий (опционально):", "") || "";

  const testObj = {
    id: null,
    name,
    variant,
    direction,
    json: scen,
    comment,
    lastStatus: "unknown",
  };

  const saved = await apiSaveTest(testObj);
  if (saved && saved.id) {
    testObj.id = saved.id;
  }

  await renderTestsList();
}

async function markTestStatus(status) {
  const id = getSelectedTestId();
  if (!id) return;
  const extra = prompt("Комментарий к статусу (опционально):", "") || "";
  await apiUpdateTestStatus(id, status, extra);
  await renderTestsList();
}

// Инициализация
window.addEventListener("load", async () => {
  await loadDefaults(); // дефолты из бэка
  renderTestsList();
  initScenarioTable();
});
