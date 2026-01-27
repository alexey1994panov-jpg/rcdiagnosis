// static/scenario.js
// Работа с таблицей сценария: добавление, удаление, применение к JSON

// --- Вспомогательные функции для создания элементов ---

function makeRcInput(value) {
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
    );
    applyRcStateClass(td, v);
  }

  input.addEventListener("change", () => {
    let v = Number(input.value || "0");
    if (Number.isNaN(v)) v = 0;
    if (v < 0) v = 0;
    if (v > 8) v = 8;
    input.value = String(v);
    applyColor();
  });

  td.appendChild(input);
  applyColor();
  return { td, input };
}

// Стрелочный select с полным набором SW_VALID_STATES из app.js
function makeSwitchSelect(value) {
  const td = document.createElement("td");
  const sel = document.createElement("select");

  const states = Array.isArray(window.SW_VALID_STATES)
    ? window.SW_VALID_STATES
    : [0, 1, 2, 3, 4, 5, 6, 7, 8];

  states.forEach((code) => {
    const opt = document.createElement("option");
    opt.value = String(code);
    opt.textContent = String(code);
    sel.appendChild(opt);
  });

  sel.value = value !== undefined && value !== null ? String(value) : "0";

  function applyColor() {
    const v = Number(sel.value || "0");
    td.classList.remove(
      "sw-state-plus",
      "sw-state-minus",
      "sw-state-nocontrol",
    );
    if (window.swClassForValue) {
      td.classList.add(window.swClassForValue(v));
    }
  }

  sel.addEventListener("change", () => {
    applyColor();
  });

  td.appendChild(sel);
  applyColor();
  return { td, sel };
}

// Сигнальный select для поездных (Ч1, НМ1) с общим набором состояний
function makeMainSignalSelect(value) {
  const td = document.createElement("td");
  const sel = document.createElement("select");

  const states = Array.isArray(window.SIGNAL_VALID_STATES)
    ? window.SIGNAL_VALID_STATES
    : [
        0, 1, 2,
        3, 4, 5, 6, 7,
        11, 12, 13, 14,
        15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 27,
      ];

  states.forEach((code) => {
    const opt = document.createElement("option");
    opt.value = String(code);
    opt.textContent = String(code);
    sel.appendChild(opt);
  });

  sel.value = value !== undefined && value !== null ? String(value) : "0";

  function applySignalColor() {
    const v = Number(sel.value || "0");
    td.classList.remove(
      "signal-free",
      "signal-stop",
      "signal-nocontrol",
      "signal-maneuver-forbidden",
      "signal-maneuver-allowed",
      "signal-maneuver-failure",
      "signal-open",
      "signal-closed",
      "signal-warning"
    );

    // 0,1,2 — нет контроля (бирюзовый)
    if (v === 0 || v === 1 || v === 2) {
      td.classList.add("signal-nocontrol");
      return;
    }

    // 15 — закрыт красным
    if (v === 15) {
      td.classList.add("signal-stop");
      return;
    }

    // 19 (отказ), 21 (погашен) — белым
    if (v === 19 || v === 21) {
      td.classList.add("signal-maneuver-allowed"); // белый
      return;
    }

    // Всё остальное >2 и не 15/19/21 — горит зелёным
    td.classList.add("signal-free");
  }

  sel.addEventListener("change", applySignalColor);

  td.appendChild(sel);
  applySignalColor();
  return { td, sel };
}

// Сигнальный select для маневровых (ЧМ1, М1) с допустимыми кодами 3–7
function makeManeuverSignalSelect(value) {
  const td = document.createElement("td");
  const sel = document.createElement("select");

  const states = [0, 1, 2, 3, 4, 5, 6, 7]; // NC + валидные маневровые

  states.forEach((code) => {
    const opt = document.createElement("option");
    opt.value = String(code);
    opt.textContent = String(code);
    sel.appendChild(opt);
  });

  sel.value = value !== undefined && value !== null ? String(value) : "0";

  function applySignalColor() {
    const v = Number(sel.value || "0");
    td.classList.remove(
      "signal-free",
      "signal-stop",
      "signal-nocontrol",
      "signal-maneuver-forbidden",
      "signal-maneuver-allowed",
      "signal-maneuver-failure",
      "signal-open",
      "signal-closed",
      "signal-warning"
    );

    // 0,1,2 — нет контроля (бирюзовый)
    if (v === 0 || v === 1 || v === 2) {
      td.classList.add("signal-nocontrol");
      return;
    }

    // 3 — запрет маневров (синий)
    if (v === 3) {
      td.classList.add("signal-maneuver-forbidden");
      return;
    }

    // 4,5 — маневровое/ускоренные маневры (белый)
    if (v === 4 || v === 5) {
      td.classList.add("signal-maneuver-allowed");
      return;
    }

    // 6 — отказ
    if (v === 6) {
      td.classList.add("signal-maneuver-failure");
      return;
    }

    // 7 — запрещающее поездное показание (красный)
    if (v === 7) {
      td.classList.add("signal-stop");
      return;
    }

    // fallback
    td.classList.add("signal-nocontrol");
  }

  sel.addEventListener("change", applySignalColor);

  td.appendChild(sel);
  applySignalColor();
  return { td, sel };
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

// --- Добавление строки в таблицу (общая функция) ---

function addScenarioRow(tbody, step) {
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

  // РЦ: 10-12SP, 1P, 1-7SP
  const rcPrev = step?.rc_states?.["10-12SP"] ?? 0;
  const rcCtrl = step?.rc_states?.["1P"] ?? 0;
  const rcNext = step?.rc_states?.["1-7SP"] ?? 0;

  const { td: tdPrev } = makeRcInput(rcPrev);
  const { td: tdCtrl } = makeRcInput(rcCtrl);
  const { td: tdNext } = makeRcInput(rcNext);

  tr.appendChild(tdPrev);
  tr.appendChild(tdCtrl);
  tr.appendChild(tdNext);

  // Стрелки: Sw10, Sw1, Sw5
  const sw10 = step?.switch_states?.["Sw10"] ?? 0;
  const sw1  = step?.switch_states?.["Sw1"]  ?? 0;
  const sw5  = step?.switch_states?.["Sw5"]  ?? 0;

  const { td: tdSw10 } = makeSwitchSelect(sw10);
  const { td: tdSw1 }  = makeSwitchSelect(sw1);
  const { td: tdSw5 }  = makeSwitchSelect(sw5);

  tr.appendChild(tdSw10);
  tr.appendChild(tdSw1);
  tr.appendChild(tdSw5);

  // Сигналы: Ч1, НМ1, ЧМ1, М1
  const sigStates = step?.signal_states || {};

  const sigCh1  = sigStates["Ч1"]  ?? 0;  // поездной
  const sigNm1  = sigStates["НМ1"] ?? 0;  // поездной
  const sigChm1 = sigStates["ЧМ1"] ?? 0;  // поездной
  const sigM1   = sigStates["М1"]  ?? 0;  // маневровый

  const { td: tdSigCh1 }  = makeMainSignalSelect(sigCh1);
  const { td: tdSigNm1 }  = makeMainSignalSelect(sigNm1);
  const { td: tdSigChm1 } = makeMainSignalSelect(sigChm1);
  const { td: tdSigM1 }   = makeManeuverSignalSelect(sigM1);


  tr.appendChild(tdSigCh1);
  tr.appendChild(tdSigNm1);
  tr.appendChild(tdSigChm1);
  tr.appendChild(tdSigM1);

  // МУ по РЦ
  const muPrev = step?.mu?.["10-12SP"] ?? 3;
  const muCurr = step?.mu?.["1P"]      ?? 3;
  const muNext = step?.mu?.["1-7SP"]   ?? 3;

  const { td: tdMuPrev } = makeEnumSelect([1, 2, 3, 4], muPrev);
  const { td: tdMuCurr } = makeEnumSelect([1, 2, 3, 4], muCurr);
  const { td: tdMuNext } = makeEnumSelect([1, 2, 3, 4], muNext);

  tr.appendChild(tdMuPrev);
  tr.appendChild(tdMuCurr);
  tr.appendChild(tdMuNext);

  // ДСП, НАС, ЧАС
  const dspVal  = step?.dispatcher_control_state ?? 4;
  const nasVal  = step?.auto_actions?.NAS ?? 4;
  const chasVal = step?.auto_actions?.CHAS ?? 4;

  const { td: tdDsp }  = makeEnumSelect([0, 1, 2, 3, 4], dspVal);
  const { td: tdNas }  = makeEnumSelect([0, 3, 4], nasVal);
  const { td: tdChas } = makeEnumSelect([0, 3, 4], chasVal);

  tr.appendChild(tdDsp);
  tr.appendChild(tdNas);
  tr.appendChild(tdChas);

  // Кнопка удаления строки
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

// --- Инициализация таблицы сценария ---

function initScenarioTable() {
  const tbody = document.querySelector("#scenariotable tbody");
  if (!tbody) return;

  scenarioTableRows = [];
  tbody.innerHTML = "";

  // Заполнение таблицы из scenario.steps
  if (Array.isArray(scenario.steps) && scenario.steps.length > 0) {
    scenario.steps.forEach((s) => addScenarioRow(tbody, s));
  } else {
    addScenarioRow(tbody, null);
  }

  // Привязка кнопок управления
  const addBtn = document.getElementById("addsteprow");
  if (addBtn) {
    addBtn.onclick = () => addScenarioRow(tbody, null);
  }

  const repeatBtn = document.getElementById("repeatprevrow");
  if (repeatBtn) {
    repeatBtn.onclick = () => {
      if (!scenarioTableRows.length) return;
      const lastTr = scenarioTableRows[scenarioTableRows.length - 1];
      const inputs = Array.from(lastTr.querySelectorAll("input,select"));
      const step = extractStepFromRow(inputs);
      if (step) addScenarioRow(tbody, step);
    };
  }

  const applyBtn = document.getElementById("applyscenariotable");
  if (applyBtn) {
    applyBtn.onclick = () => {
      console.log("applyscenariotable clicked");
      applyScenarioTableToJson();
    };
  }
}

window.initScenarioTable = initScenarioTable;

// --- Извлечение данных из строки таблицы ---

function extractStepFromRow(inputs) {
  // Порядок:
  // Δt,
  // 10-12SP, 1P, 1-7SP,
  // Sw10, Sw1, Sw5,
  // Ч1, НМ1, ЧМ1, М1,
  // MU×3, DSP, NAS, CHAS
  const [
    inpDt,
    inpPrev,
    inpCtrl,
    inpNext,
    selSw10,
    selSw1,
    selSw5,
    selSigCh1,
    selSigNm1,
    selSigChm1,
    selSigM1,
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
  const signal_states = {};

  const vPrev = parseInt(inpPrev.value || "0", 10);
  const vCtrl = parseInt(inpCtrl.value || "0", 10);
  const vNext = parseInt(inpNext.value || "0", 10);

  const vSw10 = parseInt(selSw10.value || "0", 10);
  const vSw1  = parseInt(selSw1.value  || "0", 10);
  const vSw5  = parseInt(selSw5.value  || "0", 10);

  if (vPrev || vPrev === 0) rc_states["10-12SP"] = vPrev;
  if (vCtrl || vCtrl === 0) rc_states["1P"]      = vCtrl;
  if (vNext || vNext === 0) rc_states["1-7SP"]   = vNext;

  if (vSw10 || vSw10 === 0) switch_states["Sw10"] = vSw10;
  if (vSw1  || vSw1  === 0) switch_states["Sw1"]  = vSw1;
  if (vSw5  || vSw5  === 0) switch_states["Sw5"]  = vSw5;

  const vMuPrev = parseInt(selMuPrev.value || "3", 10);
  const vMuCurr = parseInt(selMuCurr.value || "3", 10);
  const vMuNext = parseInt(selMuNext.value || "3", 10);

  mu["10-12SP"] = vMuPrev;
  mu["1P"]      = vMuCurr;
  mu["1-7SP"]   = vMuNext;

  const vDsp  = parseInt(selDsp.value || "4", 10);
  const vNas  = parseInt(selNas.value || "4", 10);
  const vChas = parseInt(selChas.value || "4", 10);

  auto_actions.NAS  = vNas;
  auto_actions.CHAS = vChas;

  const vCh1  = parseInt(selSigCh1.value  || "0", 10);
  const vNm1  = parseInt(selSigNm1.value  || "0", 10);
  const vChm1 = parseInt(selSigChm1.value || "0", 10);
  const vM1   = parseInt(selSigM1.value   || "0", 10);

  signal_states["Ч1"]  = vCh1;
  signal_states["НМ1"] = vNm1;
  signal_states["ЧМ1"] = vChm1;
  signal_states["М1"]  = vM1;

  return {
    t,
    rc_states,
    switch_states,
    modes: {},
    mu,
    dispatcher_control_state: vDsp,
    auto_actions,
    signal_states,
  };
}

// --- Удаление строки ---

function deleteRow(tr) {
  const idx = scenarioTableRows.indexOf(tr);
  if (idx === -1) return;

  tr.remove();
  scenarioTableRows.splice(idx, 1);
  applyScenarioTableToJson();
}

// --- Перестроение таблицы из scenario.steps (при загрузке теста) ---

function rebuildScenarioTableFromScenario() {
  const tbody = document.querySelector("#scenariotable tbody");
  if (!tbody) return;

  if (window.scenario) {
    // синхронизуемся с глобалом, как делает tests.js
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

  console.log("Таблица сценария перестроена из", scenario.steps.length, "шагов");
}

window.rebuildScenarioTableFromScenario = rebuildScenarioTableFromScenario;

// --- Применение таблицы к JSON ---

function applyScenarioTableToJson() {
  const tbody = document.querySelector("#scenariotable tbody");
  if (!tbody) return;

  const rows = Array.from(tbody.querySelectorAll("tr"));

  const steps = rows
    .map((tr, idx) => {
      const inputs = Array.from(tr.querySelectorAll("input,select"));
      const step = extractStepFromRow(inputs);
      console.log(
        "applyScenarioTableToJson: row", idx,
        "inputs =", inputs.length,
        "step =", step,
      );
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
    "first step =", steps[0] || null,
  );

  alert("Таблица сценария применена: " + steps.length + " шаг(ов).");
}

window.applyScenarioTableToJson = applyScenarioTableToJson;
