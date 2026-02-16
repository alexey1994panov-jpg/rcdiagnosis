// static/app.js
// Главный файл - координирует все модули


// Глобальные переменные (доступны всем модулам)
let scenario = {
  station: "Visochino",
  dt: 1,
  options: {},
  steps: [],
};

let lastTimeline = [];
let selectedIndex = -1;
let timelineRows = [];
let scenarioTableRows = [];

// Константы
// РЦ: по ТЗ используются коды 0–8.
const RC_VALID_STATES = [0, 1, 2, 3, 4, 5, 6, 7, 8];

// Стрелки: полный диапазон Uni_State_ID, с которым работает backend
const SW_VALID_STATES = [
  0, 1, 2,
  3, 4, 5, 6, 7, 8,
  9, 10, 11, 12, 13, 14,
  15, 16, 17, 18, 19, 20,
  21,
];

// Сигналы: допустимые Uni_State_ID
const SIGNAL_VALID_STATES = [
  0, 1, 2,
  3, 4, 5, 6, 7,
  11, 12, 13, 14,
  15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 27,
];

// Кеш загруженных фрагментов (используется в tabs.js)
const loadedFragments = {};

// Экспорт глобалов
window.scenario = scenario;
window.lastTimeline = lastTimeline;
window.selectedIndex = selectedIndex;
window.timelineRows = timelineRows;
window.scenarioTableRows = scenarioTableRows;
window.RC_VALID_STATES = RC_VALID_STATES;
window.SW_VALID_STATES = SW_VALID_STATES;
window.SIGNAL_VALID_STATES = SIGNAL_VALID_STATES;
window.loadedFragments = loadedFragments;

// --- Главная инициализация ---
// --- Главная инициализация ---
window.addEventListener("load", async () => {
  console.log("Initializing RC Diagnosis MVP...");

  if (typeof initTabs === "function") {
    initTabs();
  }

  if (typeof loadDefaults === "function") {
    await loadDefaults(); // подтянуть дефолты с бэка в scenario.options и формы
  }

  if (typeof initScenarioTable === "function") {
    await initScenarioTable();
  }

  if (typeof renderTestsList === "function") {
    await renderTestsList();
  }

  console.log("Initialization complete");
});

// Подсветка численных значений РЦ (таблица/подписи)
function applyRcStateClass(element, value) {
  if (!element) return;
  const v = Number(value);
  element.classList.remove("rc-state-free", "rc-state-occupied", "rc-state-nocontrol");
  if ([3, 4, 5].includes(v)) {
    element.classList.add("rc-state-free");
  } else if ([6, 7, 8].includes(v)) {
    element.classList.add("rc-state-occupied");
  } else if ([0, 1, 2].includes(v)) {
    element.classList.add("rc-state-nocontrol");
  }
}

// Классы для стрелок (фон ячеек/подписей)
function swClassForValue(v) {
  const val = Number(v);
  if ([3, 4, 5, 6, 7, 8].includes(val)) return "sw-state-plus";
  if ([9, 10, 11, 12, 13, 14].includes(val)) return "sw-state-minus";
  return "sw-state-nocontrol";
}

// Цвета SVG‑светофоров + раскраска ячеек сценария
function applySignalClass(circleEl, value, code) {
  if (!circleEl) return;
  const v = Number(value);

  circleEl.classList.remove(
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

  // Маневровый светофор (М1: code === 3)
  if (code === 3) {
    if (v === 0 || v === 1 || v === 2) {
      circleEl.classList.add("signal-nocontrol");
      return;
    }
    if (v === 3) {
      circleEl.classList.add("signal-maneuver-forbidden");
      return;
    }
    if (v === 4 || v === 5) {
      circleEl.classList.add("signal-maneuver-allowed");
      return;
    }
    if (v === 6) {
      circleEl.classList.add("signal-maneuver-failure");
      return;
    }
    if (v === 7) {
      circleEl.classList.add("signal-stop");
      return;
    }
    circleEl.classList.add("signal-nocontrol");
    return;
  }

  // Остальные сигналы
  if (v === 0 || v === 1 || v === 2) {
    circleEl.classList.add("signal-nocontrol");
    return;
  }
  if (v === 15) {
    circleEl.classList.add("signal-stop");
    return;
  }
  if (v === 19 || v === 21) {
    circleEl.classList.add("signal-maneuver-allowed");
    return;
  }
  circleEl.classList.add("signal-free");
}
window.applySignalClass = applySignalClass;

window.applyRcStateClass = applyRcStateClass;
window.swClassForValue   = swClassForValue;
window.applySignalClass  = applySignalClass;

// --- Синхронизация JSON ← scenario ---
function renderScenarioTextarea() {
  if (window.scenario) {
    scenario = window.scenario;
  }
  if (typeof window.normalizeOptionsForJson === "function") {
    scenario.options = window.normalizeOptionsForJson(scenario.options || {});
    window.scenario = scenario;
  }

  const area = document.getElementById("scenariotext");
  if (area) {
    area.value = JSON.stringify(scenario, null, 2);
  }

  console.log(
    "renderScenarioTextarea: scenario.steps.length =",
    Array.isArray(scenario.steps) ? scenario.steps.length : "n/a",
  );
}
window.renderScenarioTextarea = renderScenarioTextarea;

// --- Запуск симуляции ---
async function runSimulation() {
  try {
    const area = document.getElementById("scenariotext");
    if (area) {
      const text = area.value.trim();
      if (text) {
        scenario = JSON.parse(text);
        window.scenario = scenario;
        if (typeof rebuildScenarioTableFromScenario === "function") {
          await rebuildScenarioTableFromScenario();
        }
      }
    }

    // Пользователь что-то поменял в формах – забираем актуальные значения
    if (typeof updateOptionsFromForm === "function") {
      updateOptionsFromForm();
    }
    if (typeof applyScenarioTableToJson === "function") {
      applyScenarioTableToJson(true);
    }
    if (typeof renderScenarioTextarea === "function") {
      renderScenarioTextarea();
    }

    const resp = await fetch("/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scenario),
    });

    if (!resp.ok) {
      const msg = await resp.text().catch(() => "");
      console.error("simulate error:", resp.status, msg);
      alert("Ошибка API: " + resp.status);
      return;
    }

    const timelineRaw = await resp.json();
    const timeline =
      Array.isArray(timelineRaw) ? timelineRaw :
      Array.isArray(timelineRaw.timeline) ? timelineRaw.timeline :
      (timelineRaw.data && Array.isArray(timelineRaw.data)) ? timelineRaw.data :
      [];

    lastTimeline = timeline;
    window.lastTimeline = lastTimeline;

    if (timeline.length > 0) {
      console.log("timeline[0] from backend =", timeline[0]);
    }

    timeline.forEach((row, idx) => {
      if (row.flags && row.flags.length) {
        console.log(`step ${idx}: variant=${row.variant}, flags=`, row.flags);
      }
    });

    console.log("runSimulation: rendering timeline, length =", timeline.length);

    if (typeof renderTimeline === "function") {
      renderTimeline(timeline);
    } else {
      console.error("renderTimeline is not defined");
    }
  } catch (e) {
    console.error("runSimulation error", e);
    alert("Ошибка парсинга JSON или вызова API");
  }
}
window.runSimulation = runSimulation;
