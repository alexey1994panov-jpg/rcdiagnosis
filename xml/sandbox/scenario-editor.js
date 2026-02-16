(function () {
  const ui = {
    svg: document.getElementById("schema-svg"),
    viewport: document.getElementById("schema-viewport"),
    stage: document.getElementById("schema-stage"),
    status: document.getElementById("status"),
    objKind: document.getElementById("obj-kind"),
    objName: document.getElementById("obj-name"),
    eventTime: document.getElementById("event-time"),
    eventState: document.getElementById("event-state"),
    stateHelp: document.getElementById("state-help"),
    playTime: document.getElementById("play-time"),
    stepsTotal: document.getElementById("steps-total"),
    stepViewTime: document.getElementById("step-view-time"),
    stepEventsBody: document.querySelector("#step-events-table tbody"),
    json: document.getElementById("scenario-json"),
    presetSelect: document.getElementById("preset-select"),
    btnLoadPreset: document.getElementById("btn-load-preset"),
    btnCopyPresetJson: document.getElementById("btn-copy-preset-json"),
    eventsBody: document.querySelector("#events-table tbody"),
    btnLoad: document.getElementById("btn-load"),
    btnClear: document.getElementById("btn-clear"),
    btnExport: document.getElementById("btn-export"),
    btnImport: document.getElementById("btn-import"),
    btnZoomIn: document.getElementById("btn-zoom-in"),
    btnZoomOut: document.getElementById("btn-zoom-out"),
    btnZoomReset: document.getElementById("btn-zoom-reset"),
    btnPanMode: document.getElementById("btn-pan-mode"),
    zoomValue: document.getElementById("zoom-value"),
    btnStage: document.getElementById("btn-stage"),
    btnNextStep: document.getElementById("btn-next-step"),
    btnDupPrevStep: document.getElementById("btn-dup-prev-step"),
    btnApplyBatch: document.getElementById("btn-apply-batch"),
    draftStepTime: document.getElementById("draft-step-time"),
    draftEventsBody: document.querySelector("#draft-events-table tbody"),
    btnPrevEvent: document.getElementById("btn-prev-event"),
    btnNextEvent: document.getElementById("btn-next-event"),
    btnReset: document.getElementById("btn-reset"),
  };

  const SIGNAL_VALID_STATES_TRAIN = [
    0, 1, 2,
    3, 4, 5, 6, 7,
    11, 12, 13, 14,
    15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 27,
  ];
  const SIGNAL_VALID_STATES_MANEUVER = [0, 1, 2, 3, 4, 5, 6, 7];

  const stateOptions = {
    rc: [0, 1, 2, 3, 4, 5, 6, 7, 8, 100],
    switch: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 100],
    signal: Array.from(new Set([...SIGNAL_VALID_STATES_TRAIN, ...SIGNAL_VALID_STATES_MANEUVER])).sort((a, b) => a - b),
    indicator: [3, 4],
  };

  const stateLabels = {
    rc: {
      0: "0 - Неопределенное состояние (отсутствие ТС)",
      1: "1 - Неопределенное состояние (несоответствие ТС)",
      2: "2 - Объект законсервирован",
      3: "3 - РЦ свободна, не замкнута",
      4: "4 - РЦ свободна, замкнута",
      5: "5 - РЦ свободна, замкнута, искусственно размыкается",
      6: "6 - РЦ занята, не замкнута",
      7: "7 - РЦ занята, замкнута",
      8: "8 - РЦ занята, замкнута, искусственно размыкается",
      100: "100 - Состояние не предусмотрено",
    },
    switch: {
      0: "0 - Неопределенное состояние (отсутствие ТС)",
      1: "1 - Неопределенное состояние (несоответствие ТС)",
      2: "2 - Объект законсервирован",
      3: "3 - +, свободна, не замкнута",
      4: "4 - +, свободна, замкнута",
      5: "5 - +, свободна, замкнута, искусственно размыкается",
      6: "6 - +, занята, не замкнута",
      7: "7 - +, занята, замкнута",
      8: "8 - +, занята, замкнута, искусственно размыкается",
      9: "9 - -, свободна, не замкнута",
      10: "10 - -, свободна, замкнута",
      11: "11 - -, свободна, замкнута, искусственно размыкается",
      12: "12 - -, занята, не замкнута",
      13: "13 - -, занята, замкнута",
      14: "14 - -, занята, замкнута, искусственно размыкается",
      15: "15 - Потеря контроля, свободна, не замкнута",
      16: "16 - Потеря контроля, свободна, замкнута",
      17: "17 - Потеря контроля, занята, не замкнута",
      18: "18 - Потеря контроля, занята, замкнута",
      19: "19 - Потеря контроля, свободна, замкнута, искусственно размыкается",
      20: "20 - Потеря контроля, занята, замкнута, искусственно размыкается",
      21: "21 - Контроль есть, положение неизвестно, свободна, не замкнута",
      100: "100 - Состояние не предусмотрено",
    },
    indicator: {
      3: "3 - Индикатор не горит",
      4: "4 - Индикатор горит красным",
    },
    signal_train: {
      0: "0 - Поездной: неопределенное состояние (отсутствие ТС)",
      1: "1 - Поездной: неопределенное состояние (несоответствие ТС)",
      2: "2 - Поездной: объект законсервирован",
      3: "3 - Поездной сигнал: состояние 3",
      4: "4 - Поездной сигнал: состояние 4",
      5: "5 - Поездной сигнал: состояние 5",
      6: "6 - Поездной сигнал: состояние 6",
      7: "7 - Поездной сигнал: состояние 7",
      11: "11 - Поездной сигнал: состояние 11",
      12: "12 - Поездной сигнал: состояние 12",
      13: "13 - Поездной сигнал: состояние 13",
      14: "14 - Поездной сигнал: состояние 14",
      15: "15 - Поездной сигнал: состояние 15",
      16: "16 - Поездной сигнал: состояние 16",
      17: "17 - Поездной сигнал: состояние 17",
      18: "18 - Поездной сигнал: состояние 18",
      19: "19 - Поездной сигнал: состояние 19",
      20: "20 - Поездной сигнал: состояние 20",
      21: "21 - Поездной сигнал: состояние 21",
      22: "22 - Поездной сигнал: состояние 22",
      23: "23 - Поездной сигнал: состояние 23",
      24: "24 - Поездной сигнал: состояние 24",
      27: "27 - Поездной сигнал: состояние 27",
    },
    signal_maneuver: {
      0: "0 - Маневровый: неопределенное состояние (отсутствие ТС)",
      1: "1 - Маневровый: неопределенное состояние (несоответствие ТС)",
      2: "2 - Маневровый: объект законсервирован",
      3: "3 - Маневровый сигнал: состояние 3",
      4: "4 - Маневровый сигнал: состояние 4",
      5: "5 - Маневровый сигнал: состояние 5",
      6: "6 - Маневровый сигнал: состояние 6",
      7: "7 - Маневровый сигнал: состояние 7",
    },
  };

  const app = {
    station: "Visochino",
    geom: null,
    switchTopologyByName: new Map(),
    switchToSectionByName: new Map(),
    signalKindByName: new Map(),
    linkedIndicatorNames: new Set(),
    selected: null,
    events: [],
    staged: [],
    stagedStepT: null,
    nextStagedId: 1,
    nextEventId: 1,
    currentT: 0,
    zoom: 1,
    panMode: false,
    panModeUser: false,
    spaceHold: false,
    panX: 0,
    panY: 0,
    drag: null,
    timer: null,
    allNames: { rc: [], switch: [], signal: [], indicator: [] },
    presets: [
      "01_sw1_minus_unreachable_occupied.json",
      "02_sw1_minus_unreachable_locked.json",
      "03_sw1_minus_unreachable_free.json",
      "04_sw1_plus_reachable_branch.json",
      "05_sw1_toggle_minus_plus.json",
      "06_rc_3p_independent_section.json",
      "07_indicator_linked_basic.json",
      "08_complex_mix_sw1_sw5_and_rc.json",
      "09_lz13_ctrl_rc_baseline.json",
      "10_1p_pulse_baseline.json",
    ],
  };

  function setStatus(text) {
    if (!ui.status) return;
    const mode = app.panMode ? "Рука" : "Курсор";
    ui.status.textContent = `${text} | режим: ${mode}`;
  }

  function applyViewTransform() {
    if (!ui.stage) return;
    const z = Math.max(0.5, Math.min(3, Number(app.zoom || 1)));
    app.zoom = z;
    ui.stage.style.transform = `translate(${app.panX}px, ${app.panY}px) scale(${z})`;
    if (ui.zoomValue) ui.zoomValue.textContent = `${Math.round(z * 100)}%`;
    if (ui.btnZoomReset) ui.btnZoomReset.textContent = "100%";
    try { localStorage.setItem("sandbox_zoom", String(z)); } catch (_) { /* noop */ }
    try { localStorage.setItem("sandbox_pan", JSON.stringify({ x: app.panX, y: app.panY })); } catch (_) { /* noop */ }
  }

  function applyPanMode(enabled, persist = true) {
    app.panMode = Boolean(enabled);
    if (persist) app.panModeUser = app.panMode;
    if (ui.btnPanMode) {
      ui.btnPanMode.textContent = app.panMode ? "Рука" : "Курсор";
      ui.btnPanMode.classList.toggle("active", app.panMode);
    }
    if (ui.viewport) ui.viewport.style.cursor = app.panMode ? "grab" : "default";
    if (ui.stage) ui.stage.style.pointerEvents = app.panMode ? "none" : "auto";
    if (persist) {
      try { localStorage.setItem("sandbox_pan_mode", app.panMode ? "1" : "0"); } catch (_) { /* noop */ }
    }
  }

  function centerStage() {
    if (!ui.viewport) return;
    const vw = Number(ui.viewport.clientWidth || 0);
    const vh = Number(ui.viewport.clientHeight || 0);
    const sw = 2400 * Number(app.zoom || 1);
    const sh = 1100 * Number(app.zoom || 1);
    app.panX = Math.round((vw - sw) / 2);
    app.panY = Math.round((vh - sh) / 2);
    applyViewTransform();
    setStatus("Схема центрирована");
  }

  function bindViewportDrag() {
    if (!ui.viewport) return;
    ui.viewport.addEventListener("pointerdown", (e) => {
      if (!app.panMode) return;
      if (e.button !== 0) return;
      app.drag = {
        startX: e.clientX,
        startY: e.clientY,
        baseX: app.panX,
        baseY: app.panY,
      };
      ui.viewport.classList.add("dragging");
      try { ui.viewport.setPointerCapture(e.pointerId); } catch (_) { /* noop */ }
    });
    ui.viewport.addEventListener("pointermove", (e) => {
      if (!app.panMode) return;
      if (!app.drag) return;
      const dx = e.clientX - app.drag.startX;
      const dy = e.clientY - app.drag.startY;
      app.panX = app.drag.baseX + dx;
      app.panY = app.drag.baseY + dy;
      applyViewTransform();
    });
    const finish = () => {
      app.drag = null;
      ui.viewport.classList.remove("dragging");
    };
    ui.viewport.addEventListener("pointerup", finish);
    ui.viewport.addEventListener("pointercancel", finish);
    ui.viewport.addEventListener("pointerleave", (e) => {
      if (e.buttons === 0) finish();
    });
    ui.viewport.addEventListener("dblclick", () => centerStage());
  }

  async function loadPresetContent(fileName) {
    const name = String(fileName || "").trim();
    if (!name) throw new Error("Не выбран preset");
    const url = `/xml/sandbox/test_scenarios/${encodeURIComponent(name)}?_ts=${Date.now()}`;
    const resp = await fetch(url, { cache: "no-store" });
    if (!resp.ok) throw new Error(`preset HTTP ${resp.status}`);
    return await resp.text();
  }

  function fillPresetSelect() {
    if (!ui.presetSelect) return;
    ui.presetSelect.innerHTML = "";
    app.presets.forEach((p) => {
      const o = document.createElement("option");
      o.value = p;
      o.textContent = p;
      ui.presetSelect.appendChild(o);
    });
  }

  function normalizeObjName(v) {
    return String(v || "").trim().replace(/&sol;/g, "/").toUpperCase();
  }

  function normalizeSwitchName(v) {
    const s = String(v || "").trim();
    if (!s) return "";
    if (/^sw/i.test(s)) return `SW${s.slice(2)}`.toUpperCase();
    return `SW${s}`.toUpperCase();
  }

  function isManeuverSignalName(name) {
    const s = normalizeObjName(name);
    return s.startsWith("М");
  }

  function signalKind(name) {
    const key = normalizeObjName(name);
    const byMeta = app.signalKindByName.get(key);
    if (byMeta === "maneuver" || byMeta === "train") return byMeta;
    return isManeuverSignalName(name) ? "maneuver" : "train";
  }

  function allowedStatesFor(kind, name) {
    if (kind === "signal") return signalKind(name) === "maneuver" ? SIGNAL_VALID_STATES_MANEUVER : SIGNAL_VALID_STATES_TRAIN;
    return stateOptions[kind] || [];
  }

  function labelMapFor(kind, name) {
    if (kind === "signal") return signalKind(name) === "maneuver" ? (stateLabels.signal_maneuver || {}) : (stateLabels.signal_train || {});
    return stateLabels[kind] || {};
  }

  function extractObjNameFromRef(ref) {
    const raw = String(ref || "");
    const idx = raw.lastIndexOf("/");
    const name = idx >= 0 ? raw.slice(idx + 1) : raw;
    return normalizeObjName(name);
  }

  function parseLooseJson(text) {
    const raw = String(text || "");
    const noComments = raw
      .replace(/\/\*[\s\S]*?\*\//g, "")
      .replace(/^\s*\/\/.*$/gm, "")
      .replace(/^\s*#.*$/gm, "");
    const firstObj = noComments.indexOf("{");
    const lastObj = noComments.lastIndexOf("}");
    const sliced = firstObj >= 0 && lastObj > firstObj ? noComments.slice(firstObj, lastObj + 1) : noComments;
    const noTrailingCommas = sliced.replace(/,\s*([}\]])/g, "$1");
    return JSON.parse(noTrailingCommas || "{}");
  }

  function orderedPoints(points) {
    return (Array.isArray(points) ? points : []).filter((p) => Number.isFinite(Number(p.x)) && Number.isFinite(Number(p.y)));
  }

  function pathFrom(points) {
    const pts = orderedPoints(points);
    if (!pts.length) return "";
    let d = `M ${Number(pts[0].x)} ${Number(pts[0].y)}`;
    for (let i = 1; i < pts.length; i += 1) d += ` L ${Number(pts[i].x)} ${Number(pts[i].y)}`;
    return d;
  }

  function parseStationGeometry(xmlText) {
    const doc = new DOMParser().parseFromString(xmlText, "application/xml");
    const groups = Array.from(doc.getElementsByTagName("GOGROUP"));
    const rails = [];
    const switches = [];
    const signals = [];
    const indicators = [];

    function directGOs(group, cls) {
      return Array.from(group.children || []).filter((el) => el.tagName === "GO" && String(el.getAttribute("CLASS") || "") === cls);
    }

    function objName(group) {
      const obj = String(group.getAttribute("Obj") || "");
      const idx = obj.lastIndexOf("/");
      return idx >= 0 ? obj.slice(idx + 1) : String(group.getAttribute("NAME") || "");
    }

    groups.forEach((g) => {
      directGOs(g, "DrawRailChain").forEach((goRail) => {
        const v = goRail.querySelector("VISION");
        const from = String((v && v.getAttribute("FROM")) || "");
        if (!from.endsWith("/Section")) return;
        const c = goRail.querySelector("Const");
        if (!c) return;
        const points = Array.from(c.querySelectorAll("Point")).map((p) => ({ x: Number(p.getAttribute("X")), y: Number(p.getAttribute("Y")) }));
        if (points.length < 2) return;

        const txtGo = directGOs(g, "DrawText").find((t) => String(t.getAttribute("NAME") || "").includes("Имя РЦ"));
        let label = objName(g);
        let labelX = points[0].x + 2;
        let labelY = points[0].y - 2;
        if (txtGo) {
          const tc = txtGo.querySelector("Const");
          if (tc) {
            label = String(tc.getAttribute("Text") || label);
            labelX = Number(tc.getAttribute("X") || labelX);
            labelY = Number(tc.getAttribute("Y") || labelY);
          }
        }
        rails.push({ name: label, d: pathFrom(points), labelX, labelY });
      });

      const swGo = directGOs(g, "DrawSwitch")[0];
      if (swGo) {
        const c = swGo.querySelector("Const");
        if (c) {
          const root = { x: Number(c.getAttribute("X")), y: Number(c.getAttribute("Y")) };
          const minus = Array.from(c.querySelectorAll("Minus > Point")).map((p) => ({ x: Number(p.getAttribute("X")), y: Number(p.getAttribute("Y")) }));
          const plus = Array.from(c.querySelectorAll("Plus > Point")).map((p) => ({ x: Number(p.getAttribute("X")), y: Number(p.getAttribute("Y")) }));
          const section = Array.from(c.querySelectorAll("Section > Point")).map((p) => ({ x: Number(p.getAttribute("X")), y: Number(p.getAttribute("Y")) }));

          const txtGo = directGOs(g, "DrawText").find((t) => {
            const v = t.querySelector("VISION");
            const from = String((v && v.getAttribute("FROM")) || "");
            const n = String(t.getAttribute("NAME") || "");
            return from.includes("SwitchNameTest") || n.includes("Название стрелки");
          });

          let label = objName(g);
          let labelX = root.x + 6;
          let labelY = root.y - 6;
          if (txtGo) {
            const tc = txtGo.querySelector("Const");
            if (tc) {
              label = String(tc.getAttribute("Text") || label);
              labelX = Number(tc.getAttribute("X") || labelX);
              labelY = Number(tc.getAttribute("Y") || labelY);
            }
          }
          if (!/^sw/i.test(label)) label = `Sw${label}`;
          switches.push({
            name: label,
            plusD: plus.length ? pathFrom([root, ...plus]) : "",
            minusD: minus.length ? pathFrom([root, ...minus]) : "",
            sectionD: section.length ? pathFrom([root, ...section]) : "",
            labelX,
            labelY,
          });
        }
      }

      directGOs(g, "DrawSignal").forEach((goSig) => {
        const c = goSig.querySelector("Const");
        if (!c) return;
        signals.push({
          name: objName(g),
          x: Number(c.getAttribute("X")),
          y: Number(c.getAttribute("Y")),
          r: Number(c.getAttribute("Radius") || 7),
          orientation: Number(c.getAttribute("Orientation") || 0),
        });
      });

      directGOs(g, "DrawTextBox").forEach((goInd) => {
        const c = goInd.querySelector("Const");
        if (!c) return;
        indicators.push({
          name: objName(g),
          text: String(c.getAttribute("Text") || objName(g) || ""),
          x: Number(c.getAttribute("X")),
          y: Number(c.getAttribute("Y")),
          w: Number(c.getAttribute("Width") || 20),
          h: Number(c.getAttribute("Height") || 12),
        });
      });
    });

    return { rails, switches, signals, indicators };
  }

  function parseObjectsMeta(xmlText) {
    const doc = new DOMParser().parseFromString(xmlText, "application/xml");
    const objects = Array.from(doc.getElementsByTagName("Object"));
    const topo = new Map();
    const linkedIndicators = new Set();
    const signalKinds = new Map();

    objects.forEach((obj) => {
      const type = String(obj.getAttribute("Type") || "");
      const name = normalizeObjName(obj.getAttribute("Name") || obj.getAttribute("NAME"));
      if (!name) return;

      if (type.startsWith("1000.2.")) {
        const sw = normalizeSwitchName(name);
        let section = "";
        let nextSwMi = "";
        let nextSwPl = "";
        let mainSwitch = "";
        Array.from(obj.getElementsByTagName("ObjData")).forEach((d) => {
          const n = String(d.getAttribute("NAME") || d.getAttribute("Name") || "").toLowerCase();
          if (n === "swsection") section = extractObjNameFromRef(d.getAttribute("Ref"));
          if (n === "nextswmi") nextSwMi = normalizeSwitchName(extractObjNameFromRef(d.getAttribute("Ref")));
          if (n === "nextswpl") nextSwPl = normalizeSwitchName(extractObjNameFromRef(d.getAttribute("Ref")));
          if (n === "main") mainSwitch = normalizeSwitchName(extractObjNameFromRef(d.getAttribute("Ref")));
        });
        topo.set(sw, { section, nextSwMi, nextSwPl, mainSwitch });
      }

      if (type.startsWith("1000.9.")) {
        let hasPrev = false;
        let hasNext = false;
        Array.from(obj.getElementsByTagName("ObjData")).forEach((d) => {
          const n = String(d.getAttribute("NAME") || d.getAttribute("Name") || "").toLowerCase();
          if (n === "prevsec") hasPrev = true;
          if (n === "nextsec") hasNext = true;
        });
        if (hasPrev || hasNext) linkedIndicators.add(name);
      }

      if (type.startsWith("1000.3.")) {
        signalKinds.set(name, "maneuver");
      } else if (type.startsWith("1000.4.")) {
        signalKinds.set(name, "train");
      }
    });

    return { topo, linkedIndicators, signalKinds };
  }

  function switchPositionByState(state) {
    const s = Number(state);
    if (s >= 3 && s <= 8) return "plus";
    if (s >= 9 && s <= 14) return "minus";
    if (s >= 15 && s <= 20) return "none";
    return "";
  }

  function composeSwitchState(position, rcState) {
    const r = Number(rcState);
    const validRc = [3, 4, 5, 6, 7, 8];
    if (!validRc.includes(r)) {
      if (position === "plus") return 3;
      if (position === "minus") return 9;
      if (position === "none") return 15;
      return undefined;
    }
    if (position === "plus") return r;
    if (position === "minus") return r + 6;
    if (position === "none") {
      if (r === 3) return 15;
      if (r === 4) return 16;
      if (r === 5) return 19;
      if (r === 6) return 17;
      if (r === 7) return 18;
      if (r === 8) return 20;
    }
    return undefined;
  }

  function rcStateFromSwitchState(swState) {
    const s = Number(swState);
    if (s >= 3 && s <= 8) return s; // plus: rc maps directly
    if (s >= 9 && s <= 14) return s - 6; // minus: back to rc 3..8
    if (s === 15) return 3;
    if (s === 16) return 4;
    if (s === 17) return 6;
    if (s === 18) return 7;
    if (s === 19) return 5;
    if (s === 20) return 8;
    if (s === 21) return 3;
    return undefined;
  }

  function upsertRcEventFromSwitchAtTime(t, switchName, switchState) {
    const sw = normalizeSwitchName(switchName);
    const topo = app.switchTopologyByName.get(sw);
    const rcName = normalizeObjName(topo && topo.section);
    const rcState = rcStateFromSwitchState(switchState);
    if (!rcName || !Number.isFinite(Number(rcState))) return;

    const existing = app.events.find(
      (e) => Number(e.t) === Number(t) && String(e.kind) === "rc" && normalizeObjName(e.name) === rcName
    );
    if (existing) {
      existing.state = Number(rcState);
      existing.name = rcName;
      return;
    }
    app.events.push({
      id: app.nextEventId++,
      t: Number(t),
      kind: "rc",
      name: rcName,
      state: Number(rcState),
    });
  }

  function deriveSwitchStates(swRaw, rcStates) {
    const swStates = { ...(swRaw || {}) };
    if (!app.switchTopologyByName.size) return swStates;

    const graph = new Map();
    function addEdge(a, b) {
      if (!a || !b) return;
      if (!graph.has(a)) graph.set(a, new Set());
      if (!graph.has(b)) graph.set(b, new Set());
      graph.get(a).add(b);
      graph.get(b).add(a);
    }

    app.switchTopologyByName.forEach((topo, sw) => addEdge(sw, normalizeSwitchName(topo.mainSwitch)));

    const seen = new Set();
    graph.forEach((_, start) => {
      if (seen.has(start)) return;
      const stack = [start];
      const fam = [];
      while (stack.length) {
        const cur = stack.pop();
        if (!cur || seen.has(cur)) continue;
        seen.add(cur);
        fam.push(cur);
        const n = graph.get(cur);
        if (n) n.forEach((x) => !seen.has(x) && stack.push(x));
      }
      let pos = "";
      fam.forEach((sw) => {
        if (!pos) pos = switchPositionByState(swStates[sw]);
      });
      if (!pos) return;
      fam.forEach((sw) => {
        const topo = app.switchTopologyByName.get(sw);
        const sec = normalizeObjName(topo && topo.section);
        const composed = composeSwitchState(pos, sec ? rcStates[sec] : undefined);
        if (Number.isFinite(Number(composed))) swStates[sw] = Number(composed);
      });
    });

    Object.keys(swStates).forEach((sw) => {
      const topo = app.switchTopologyByName.get(sw);
      const sec = normalizeObjName(topo && topo.section);
      const pos = switchPositionByState(swStates[sw]);
      if (!sec || !pos) return;
      const composed = composeSwitchState(pos, rcStates[sec]);
      if (Number.isFinite(Number(composed))) swStates[sw] = Number(composed);
    });

    return swStates;
  }

  function computeReachableSwitchesBySection(swStates) {
    const switchesBySection = new Map();
    const incomingBySection = new Map();
    const sectionReach = new Map();

    app.switchTopologyByName.forEach((topo, swName) => {
      const sec = normalizeObjName(topo && topo.section);
      if (!sec) return;
      if (!switchesBySection.has(sec)) switchesBySection.set(sec, new Set());
      switchesBySection.get(sec).add(swName);
    });

    app.switchTopologyByName.forEach((topo) => {
      const sec = normalizeObjName(topo && topo.section);
      if (!sec || !switchesBySection.has(sec)) return;
      const inSec = switchesBySection.get(sec);
      const mi = normalizeSwitchName(topo && topo.nextSwMi);
      const pl = normalizeSwitchName(topo && topo.nextSwPl);
      if (!incomingBySection.has(sec)) incomingBySection.set(sec, new Set());
      const incoming = incomingBySection.get(sec);
      if (mi && inSec.has(mi)) incoming.add(mi);
      if (pl && inSec.has(pl)) incoming.add(pl);
    });

    switchesBySection.forEach((swSet, sec) => {
      const incoming = incomingBySection.get(sec) || new Set();
      const roots = Array.from(swSet).filter((sw) => !incoming.has(sw));
      const seed = roots.length ? roots : Array.from(swSet);
      const visited = new Set();
      const queue = seed.slice();

      while (queue.length) {
        const sw = queue.shift();
        if (!sw || visited.has(sw)) continue;
        visited.add(sw);
        const topo = app.switchTopologyByName.get(sw);
        const state = Number(swStates && swStates[sw]);
        const isPlus = state >= 3 && state <= 8;
        const isMinus = state >= 9 && state <= 14;
        const next = isPlus ? normalizeSwitchName(topo.nextSwPl) : (isMinus ? normalizeSwitchName(topo.nextSwMi) : "");
        if (next && swSet.has(next) && !visited.has(next)) queue.push(next);
      }

      sectionReach.set(sec, visited);
    });

    return sectionReach;
  }

  function rcStrokeByState(state) {
    const s = Number(state);
    if ([6, 7, 8].includes(s)) return "#ff4040"; // occupied
    if ([4, 5].includes(s)) return "#f5f5f5"; // locked
    if ([3].includes(s)) return "#8a8f99"; // free
    if ([0, 1, 2, 100].includes(s)) return "#555a63"; // no control / unknown
    return "#8a8f99";
  }

  function switchStrokeByState(state) {
    const s = Number(state);
    if ([6, 7, 8, 12, 13, 14, 17, 18, 20].includes(s)) return "#ff4040"; // occupied
    if ([4, 5, 10, 11, 16, 19].includes(s)) return "#f5f5f5"; // free+locked
    if ([3, 9, 15, 21].includes(s)) return "#8a8f99"; // free+not locked
    if ([0, 1, 2, 100].includes(s)) return "#555a63";
    return "#8a8f99";
  }

  function switchNameColorByState(state) {
    const s = Number(state);
    if (s >= 3 && s <= 8) return "#49d26b"; // plus control
    if (s >= 9 && s <= 14) return "#ffdd57"; // minus control
    if (s >= 15 && s <= 20) return "#ff4040"; // loss of control
    if ([0, 1, 2, 100].includes(s)) return "#00d6de"; // undefined/conserved/unknown
    return "#00d6de";
  }

  function signalFillByState(state) {
    const s = Number(state);
    if (s === 15) return "#ff4a4a";
    if ([3, 7].includes(s)) return "#3a7bff";
    if ([4, 5].includes(s)) return "#f2f2f2";
    if ([0, 1, 2, 100].includes(s)) return "#666";
    return "#48d26b";
  }

  function indicatorFillByState(state) {
    return Number(state) === 4 ? "#ff4a4a" : "none";
  }

  function stateMapsAt(t) {
    const rc = {};
    const sw = {};
    const sig = {};
    const ind = {};
    app.allNames.rc.forEach((n) => { rc[normalizeObjName(n)] = 0; });
    app.allNames.switch.forEach((n) => { sw[normalizeSwitchName(n)] = 0; });
    app.allNames.signal.forEach((n) => { sig[normalizeObjName(n)] = 0; });
    // Default indicator states only for linked indicators (PrevSec/NextSec).
    app.allNames.indicator.forEach((n) => {
      const key = normalizeObjName(n);
      if (app.linkedIndicatorNames.has(key)) ind[key] = 0;
    });
    const sorted = app.events.slice().sort((a, b) => a.t - b.t || a.id - b.id);
    sorted.forEach((ev) => {
      if (Number(ev.t) > Number(t)) return;
      const key = normalizeObjName(ev.name);
      if (ev.kind === "rc") rc[key] = Number(ev.state);
      if (ev.kind === "switch") sw[normalizeSwitchName(ev.name)] = Number(ev.state);
      if (ev.kind === "signal") sig[key] = Number(ev.state);
      if (ev.kind === "indicator" && app.linkedIndicatorNames.has(key)) ind[key] = Number(ev.state);
    });
    const swDerived = deriveSwitchStates(sw, rc);
    return { rc, sw: swDerived, sig, ind };
  }

  function eventTimes() {
    return Array.from(new Set(app.events.map((e) => Number(e.t) || 0))).sort((a, b) => a - b);
  }

  function updateStepsInfo() {
    if (!ui.stepsTotal) return;
    ui.stepsTotal.value = String(eventTimes().length);
  }

  function stepWindows() {
    const times = eventTimes();
    if (!times.length) return [];
    const out = [];
    for (let i = 0; i < times.length; i += 1) {
      const start = times[i];
      const end = i < times.length - 1 ? times[i + 1] : (start + 1);
      out.push({ start, end, dt: end - start });
    }
    return out;
  }

  function clearSvg() {
    while (ui.svg.firstChild) ui.svg.removeChild(ui.svg.firstChild);
  }

  function drawPath(d, stroke, width, onClick, selected) {
    if (!d) return;
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", d);
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", stroke);
    p.setAttribute("stroke-width", String(width || 3));
    p.setAttribute("stroke-linecap", "round");
    p.setAttribute("stroke-linejoin", "round");
    if (selected) p.classList.add("selected-glow");
    if (onClick) p.addEventListener("click", onClick);
    ui.svg.appendChild(p);
  }

  function drawHitPath(d, width, onClick) {
    if (!d || !onClick) return;
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", d);
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", "rgba(0,0,0,0.001)");
    p.setAttribute("stroke-width", String(width || 10));
    p.setAttribute("stroke-linecap", "round");
    p.setAttribute("stroke-linejoin", "round");
    p.setAttribute("pointer-events", "stroke");
    p.addEventListener("click", onClick);
    ui.svg.appendChild(p);
  }

  function drawText(x, y, text, fill, anchor) {
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", String(x));
    t.setAttribute("y", String(y));
    t.setAttribute("fill", fill);
    t.setAttribute("font-size", "10");
    t.setAttribute("pointer-events", "none");
    if (anchor) t.setAttribute("text-anchor", anchor);
    t.textContent = text;
    ui.svg.appendChild(t);
  }

  function render() {
    if (!app.geom) return;
    const maps = stateMapsAt(app.currentT);
    clearSvg();

    const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    bg.setAttribute("x", "0");
    bg.setAttribute("y", "0");
    bg.setAttribute("width", "2400");
    bg.setAttribute("height", "1100");
    bg.setAttribute("fill", "#090b10");
    ui.svg.appendChild(bg);

    app.geom.rails.forEach((r) => {
      const key = normalizeObjName(r.name);
      const stroke = rcStrokeByState(maps.rc[key]);
      const selected = app.selected && app.selected.kind === "rc" && normalizeObjName(app.selected.name) === key;
      drawPath(r.d, stroke, 5, () => selectObject("rc", r.name), selected);
      drawHitPath(r.d, 14, () => selectObject("rc", r.name));
      drawText(r.labelX, r.labelY, r.name, "#f5f5f5");
    });

    const reachBySection = computeReachableSwitchesBySection(maps.sw);

    app.geom.switches.forEach((s) => {
      const swKey = normalizeSwitchName(s.name);
      const topo = app.switchTopologyByName.get(swKey);
      const secKey = normalizeObjName(topo && topo.section);
      const secState = secKey ? maps.rc[secKey] : undefined;
      const secOcc = [6, 7, 8].includes(Number(secState));
      const secReach = secKey ? reachBySection.get(secKey) : null;
      const switchReachableInSection = !secReach || secReach.has(swKey);
      const swState = maps.sw[swKey];
      const isPlus = Number(swState) >= 3 && Number(swState) <= 8;
      const isMinus = Number(swState) >= 9 && Number(swState) <= 14;
      const hasKnownPos = isPlus || isMinus;

      const occ = rcStrokeByState(secState);
      const base = "#8a8f99";
      const pos = switchStrokeByState(swState);
      const selected = app.selected && app.selected.kind === "switch" && normalizeSwitchName(app.selected.name) === swKey;
      const rcColor = rcStrokeByState(secState);

      if (!switchReachableInSection) {
        // Unreachable switch parts (for current switch positions inside one RC)
        // must stay neutral for any RC/switch state.
        drawPath(s.sectionD, base, 3, () => selectObject("switch", s.name), selected);
        drawPath(s.plusD, base, 3, () => selectObject("switch", s.name), selected);
        drawPath(s.minusD, base, 3, () => selectObject("switch", s.name), selected);
      } else if (secOcc && hasKnownPos) {
        drawPath(s.sectionD, rcColor, 3, () => selectObject("switch", s.name), selected);
        drawPath(s.plusD, isMinus ? base : rcColor, 3, () => selectObject("switch", s.name), selected);
        drawPath(s.minusD, isPlus ? base : rcColor, 3, () => selectObject("switch", s.name), selected);
      } else {
        // For free/locked RC, section color must still follow RC state (3/4/5 etc).
        drawPath(s.sectionD, rcColor, 3, () => selectObject("switch", s.name), selected);
        if (isMinus) {
          drawPath(s.plusD, base, 3, () => selectObject("switch", s.name), selected);
          drawPath(s.minusD, rcColor, 3, () => selectObject("switch", s.name), selected);
        } else if (isPlus) {
          drawPath(s.plusD, rcColor, 3, () => selectObject("switch", s.name), selected);
          drawPath(s.minusD, base, 3, () => selectObject("switch", s.name), selected);
        } else {
          drawPath(s.plusD, pos, 3, () => selectObject("switch", s.name), selected);
          drawPath(s.minusD, pos, 3, () => selectObject("switch", s.name), selected);
        }
      }
      drawText(s.labelX, s.labelY - 6, s.name, switchNameColorByState(swState));
    });

    app.geom.signals.forEach((sg) => {
      const key = normalizeObjName(sg.name);
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("cx", String(sg.x));
      c.setAttribute("cy", String(sg.y));
      c.setAttribute("r", String(Math.max(6, sg.r || 7)));
      c.setAttribute("fill", signalFillByState(maps.sig[key]));
      c.setAttribute("stroke", "#250000");
      c.setAttribute("stroke-width", "1");
      if (app.selected && app.selected.kind === "signal" && normalizeObjName(app.selected.name) === key) c.classList.add("selected-glow");
      c.addEventListener("click", () => selectObject("signal", sg.name));
      ui.svg.appendChild(c);
      const side = Number(sg.orientation) >= 90 ? "end" : "start";
      drawText(sg.x + (side === "start" ? 12 : -12), sg.y + 3, sg.name, "#f5f5f5", side);
    });

    app.geom.indicators.forEach((it) => {
      const key = normalizeObjName(it.name);
      if (!app.linkedIndicatorNames.has(key)) return;
      const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      r.setAttribute("x", String(it.x));
      r.setAttribute("y", String(it.y));
      r.setAttribute("width", String(Math.max(8, it.w || 12)));
      r.setAttribute("height", String(Math.max(8, it.h || 10)));
      const indFill = indicatorFillByState(maps.ind[key]);
      // Keep off indicators visually empty, but preserve a clickable interior area.
      r.setAttribute("fill", indFill === "none" ? "rgba(0,0,0,0.001)" : indFill);
      r.setAttribute("stroke", "#8dd6ff");
      r.setAttribute("stroke-width", "1");
      r.setAttribute("pointer-events", "all");
      if (app.selected && app.selected.kind === "indicator" && normalizeObjName(app.selected.name) === key) r.classList.add("selected-glow");
      r.addEventListener("click", () => selectObject("indicator", it.name));
      ui.svg.appendChild(r);
      drawText(it.x + Math.max(8, it.w || 12) / 2, it.y + Math.max(8, it.h || 10) / 2 + 1, it.text || it.name, "#8dd6ff", "middle");
    });

    setStatus(`t=${app.currentT}s, событий: ${app.events.length}`);
  }

  function selectObject(kind, name) {
    app.selected = { kind, name };
    ui.objKind.value = kind;
    ui.objName.value = name;
    fillStateOptions(kind);
    render();
  }

  function fillStateOptions(kind) {
    const objName = ui.objName.value || "";
    const opts = allowedStatesFor(kind, objName);
    ui.eventState.innerHTML = "";
    const labels = labelMapFor(kind, objName);
    opts.forEach((v) => {
      const o = document.createElement("option");
      o.value = String(v);
      o.textContent = labels[v] || String(v);
      ui.eventState.appendChild(o);
    });
    updateStateHelp();
  }

  function updateStateHelp() {
    if (!ui.stateHelp) return;
    const kind = ui.objKind.value || "rc";
    const objName = ui.objName.value || "";
    const state = Number(ui.eventState.value);
    const labels = labelMapFor(kind, objName);
    ui.stateHelp.textContent = labels[state] || "";
  }

  function sortEvents() {
    app.events.sort((a, b) => Number(a.t) - Number(b.t) || Number(a.id) - Number(b.id));
  }

  function compactEvents() {
    const byKey = new Map();
    app.events.forEach((ev) => {
      const key = `${Number(ev.t)}|${String(ev.kind)}|${normalizeObjName(ev.name)}`;
      byKey.set(key, ev);
    });
    app.events = Array.from(byKey.values());
    sortEvents();
  }

  function renderEventsTable() {
    compactEvents();
    updateStepsInfo();
    ui.eventsBody.innerHTML = "";
    sortEvents();
    const byT = new Map();
    app.events.forEach((ev) => {
      const t = Number(ev.t);
      if (!byT.has(t)) byT.set(t, []);
      byT.get(t).push(ev);
    });
    const windows = stepWindows();
    let currentT = null;
    app.events.forEach((ev) => {
      if (currentT !== ev.t) {
        currentT = ev.t;
        const win = windows.find((w) => Number(w.start) === Number(ev.t));
        const tStart = win ? win.start : Number(ev.t);
        const tEnd = win ? win.end : (Number(ev.t) + 1);
        const dt = win ? win.dt : 1;
        const groupRow = document.createElement("tr");
        groupRow.innerHTML = `
          <td colspan="5" style="background:#101726;color:#9fb1d6;font-weight:600;">
            Шаг t=${ev.t} | t_start=${tStart.toFixed(1)}s, t_end=${tEnd.toFixed(1)}s, Δt=${dt.toFixed(1)}s
            <button data-step-act="jump-step" data-step-t="${ev.t}" style="margin-left:8px;">Jump</button>
            <button data-step-act="dup-step" data-step-t="${ev.t}" style="margin-left:4px;">Dup step</button>
          </td>`;
        ui.eventsBody.appendChild(groupRow);
      }
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td></td>
        <td>${ev.kind}</td>
        <td>${ev.name}</td>
        <td>${ev.state}</td>
        <td>
          <button data-act="jump" data-id="${ev.id}">Jump</button>
          <button data-act="edit" data-id="${ev.id}">Edit</button>
          <button data-act="dup" data-id="${ev.id}">Dup</button>
          <button data-act="del" data-id="${ev.id}">Del</button>
        </td>`;
      ui.eventsBody.appendChild(tr);
    });
    ui.eventsBody.querySelectorAll("button").forEach((b) => {
      b.addEventListener("click", () => {
        const id = Number(b.getAttribute("data-id"));
        const act = b.getAttribute("data-act");
        const ev = app.events.find((x) => x.id === id);
        if (!ev) return;
        if (act === "jump") {
          app.currentT = Number(ev.t);
          ui.playTime.value = String(app.currentT);
          render();
        }
        if (act === "dup") {
          app.events.push({ ...ev, id: app.nextEventId++, t: Number(ev.t) + 1 });
          renderEventsTable();
          renderCurrentStepPanel();
          render();
        }
        if (act === "edit") {
          if (!editEventStateInline(ev)) return;
          renderEventsTable();
          renderCurrentStepPanel();
          render();
        }
        if (act === "del") {
          app.events = app.events.filter((x) => x.id !== id);
          renderEventsTable();
          renderCurrentStepPanel();
          render();
        }
      });
    });
    ui.eventsBody.querySelectorAll("button[data-step-act]").forEach((b) => {
      b.addEventListener("click", () => {
        const t = Number(b.getAttribute("data-step-t"));
        const act = b.getAttribute("data-step-act");
        if (!Number.isFinite(t)) return;
        if (act === "jump-step") {
          app.currentT = t;
          ui.playTime.value = String(app.currentT);
          ui.eventTime.value = String(t);
          renderCurrentStepPanel();
          render();
          return;
        }
        if (act === "dup-step") {
          duplicateStepToDraft(t);
        }
      });
    });
  }

  function compactStaged() {
    const byKey = new Map();
    app.staged.forEach((ev) => {
      const key = `${Number(ev.t)}|${String(ev.kind)}|${normalizeObjName(ev.name)}`;
      byKey.set(key, ev);
    });
    app.staged = Array.from(byKey.values()).sort((a, b) => Number(a.sid || 0) - Number(b.sid || 0));
    if (!app.staged.length) app.stagedStepT = null;
  }

  function renderDraftStepPanel() {
    if (!ui.draftEventsBody) return;
    compactStaged();
    if (ui.draftStepTime) {
      const fallbackT = Math.max(0, Number(ui.eventTime.value || 0));
      ui.draftStepTime.value = Number.isFinite(Number(app.stagedStepT)) ? String(app.stagedStepT) : String(fallbackT);
    }
    ui.draftEventsBody.innerHTML = "";
    app.staged.forEach((ev) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${ev.kind}</td>
        <td>${ev.name}</td>
        <td>${ev.state}</td>
        <td>
          <button data-draft-act="edit" data-sid="${ev.sid}">Edit</button>
          <button data-draft-act="del" data-sid="${ev.sid}">Del</button>
        </td>`;
      ui.draftEventsBody.appendChild(tr);
    });
    ui.draftEventsBody.querySelectorAll("button[data-draft-act]").forEach((b) => {
      b.addEventListener("click", () => {
        const sid = Number(b.getAttribute("data-sid"));
        const act = b.getAttribute("data-draft-act");
        const ev = app.staged.find((x) => Number(x.sid) === sid);
        if (!ev) return;
        if (act === "edit") {
          if (!editEventStateInline(ev)) return;
          compactStaged();
          renderDraftStepPanel();
          return;
        }
        if (act === "del") {
          app.staged = app.staged.filter((x) => Number(x.sid) !== sid);
          compactStaged();
          renderDraftStepPanel();
        }
      });
    });
  }

  function editEventStateInline(ev) {
    const allowed = allowedStatesFor(ev.kind, ev.name);
    const nextRaw = window.prompt(`Новое state для ${ev.kind}:${ev.name}\nДопустимо: ${allowed.join(", ")}`, String(ev.state));
    if (nextRaw == null) return false;
    const nextState = Number(nextRaw);
    if (!Number.isFinite(nextState) || (allowed.length && !allowed.includes(nextState))) {
      setStatus("Недопустимое состояние для выбранного типа объекта");
      return false;
    }
    ev.state = nextState;
    if (ev.kind === "switch") {
      upsertRcEventFromSwitchAtTime(ev.t, ev.name, nextState);
    }
    return true;
  }

  function renderCurrentStepPanel() {
    if (!ui.stepEventsBody) return;
    const t = Math.max(1, Number(ui.eventTime.value || 1));
    if (ui.stepViewTime) ui.stepViewTime.value = String(t);
    ui.stepEventsBody.innerHTML = "";
    const list = app.events.filter((e) => Number(e.t) === t).sort((a, b) => Number(a.id) - Number(b.id));
    list.forEach((ev) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${ev.kind}</td>
        <td>${ev.name}</td>
        <td>${ev.state}</td>
        <td>
          <button data-step-ev-act="edit" data-id="${ev.id}">Edit</button>
          <button data-step-ev-act="del" data-id="${ev.id}">Del</button>
        </td>`;
      ui.stepEventsBody.appendChild(tr);
    });
    ui.stepEventsBody.querySelectorAll("button[data-step-ev-act]").forEach((b) => {
      b.addEventListener("click", () => {
        const id = Number(b.getAttribute("data-id"));
        const act = b.getAttribute("data-step-ev-act");
        const ev = app.events.find((x) => x.id === id);
        if (!ev) return;
        if (act === "edit") {
          if (!editEventStateInline(ev)) return;
          compactEvents();
          renderEventsTable();
          renderCurrentStepPanel();
          render();
          return;
        }
        if (act === "del") {
          app.events = app.events.filter((x) => x.id !== id);
          compactEvents();
          renderEventsTable();
          renderCurrentStepPanel();
          render();
        }
      });
    });
  }

  function addEventFromForm(andApply) {
    if (!app.selected) {
      setStatus("Сначала выберите объект на схеме");
      return;
    }
    const t = Math.max(1, Number(ui.eventTime.value || 1));
    const state = Number(ui.eventState.value);
    if (!Number.isFinite(state)) {
      setStatus("Выберите состояние");
      return;
    }
    app.events.push({ id: app.nextEventId++, t, kind: app.selected.kind, name: app.selected.name, state });
    if (app.selected.kind === "switch") {
      const sw = normalizeSwitchName(app.selected.name);
      const topo = app.switchTopologyByName.get(sw);
      const rcName = normalizeObjName(topo && topo.section);
      const rcState = rcStateFromSwitchState(state);
      if (rcName && Number.isFinite(Number(rcState))) {
        app.events.push({ id: app.nextEventId++, t, kind: "rc", name: rcName, state: Number(rcState) });
      }
    }
    renderEventsTable();
    renderCurrentStepPanel();
    if (andApply) {
      app.currentT = t;
      ui.playTime.value = String(app.currentT);
    }
    render();
  }

  function stageEventFromForm() {
    if (!app.selected) {
      setStatus("Сначала выберите объект на схеме");
      return;
    }
    const tForm = Math.max(1, Number(ui.eventTime.value || 1));
    let t = tForm;
    if (!Number.isFinite(Number(app.stagedStepT))) {
      app.stagedStepT = tForm;
    } else if (Number(app.stagedStepT) !== tForm) {
      t = Number(app.stagedStepT);
      ui.eventTime.value = String(t);
      setStatus(`Черновик уже открыт на t=${t}. Событие добавлено в этот шаг.`);
    }
    const state = Number(ui.eventState.value);
    if (!Number.isFinite(state)) {
      setStatus("Выберите состояние");
      return;
    }
    app.staged.push({ sid: app.nextStagedId++, t, kind: app.selected.kind, name: app.selected.name, state });
    if (app.selected.kind === "switch") {
      const sw = normalizeSwitchName(app.selected.name);
      const topo = app.switchTopologyByName.get(sw);
      const rcName = normalizeObjName(topo && topo.section);
      const rcState = rcStateFromSwitchState(state);
      if (rcName && Number.isFinite(Number(rcState))) {
        app.staged.push({ sid: app.nextStagedId++, t, kind: "rc", name: rcName, state: Number(rcState) });
      }
    }
    renderDraftStepPanel();
    setStatus(`Добавлено в шаг: ${app.selected.kind} ${app.selected.name}=${state} @t=${t}`);
  }

  function applyBatch() {
    if (!app.staged.length) return;
    app.staged.forEach((x) => {
      app.events.push({ id: app.nextEventId++, t: x.t, kind: x.kind, name: x.name, state: x.state });
    });
    app.staged = [];
    app.stagedStepT = null;
    compactEvents();
    renderDraftStepPanel();
    renderEventsTable();
    renderCurrentStepPanel();
    updateStepsInfo();
    render();
  }

  function clearEvents() {
    app.events = [];
    app.staged = [];
    app.stagedStepT = null;
    app.nextEventId = 1;
    app.currentT = 0;
    ui.playTime.value = "0";
    if (ui.eventTime) ui.eventTime.value = "1";
    renderDraftStepPanel();
    renderEventsTable();
    renderCurrentStepPanel();
    updateStepsInfo();
    render();
  }

  function maxTimelineT() {
    if (!app.events.length) return 0;
    return Math.max(...app.events.map((e) => Number(e.t) || 0));
  }

  function setNextStepTime() {
    const nextT = Math.max(1, maxTimelineT() + 1);
    app.staged = [];
    app.stagedStepT = null;
    ui.eventTime.value = String(nextT);
    renderDraftStepPanel();
    renderCurrentStepPanel();
    updateStepsInfo();
    setStatus(`Новый шаг: t=${nextT}`);
  }

  function duplicateStepToNext(srcT) {
    const src = app.events.filter((e) => Number(e.t) === Number(srcT));
    if (!src.length) return;
    const times = eventTimes();
    const nextCandidate = Math.max(...times, 0) + 1;
    src.forEach((e) => {
      app.events.push({
        id: app.nextEventId++,
        t: nextCandidate,
        kind: e.kind,
        name: e.name,
        state: e.state,
      });
    });
    ui.eventTime.value = String(nextCandidate);
    renderEventsTable();
    renderCurrentStepPanel();
    updateStepsInfo();
    render();
    setStatus(`Шаг t=${srcT} продублирован в t=${nextCandidate}`);
  }

  function duplicateStepToDraft(srcT) {
    const src = app.events.filter((e) => Number(e.t) === Number(srcT));
    if (!src.length) {
      setStatus(`Шаг t=${srcT} пуст, нечего дублировать`);
      return;
    }
    const times = eventTimes();
    const nextCandidate = Math.max(...times, 0) + 1;
    app.staged = [];
    app.stagedStepT = nextCandidate;
    src.forEach((e) => {
      app.staged.push({
        sid: app.nextStagedId++,
        t: nextCandidate,
        kind: e.kind,
        name: e.name,
        state: e.state,
      });
    });
    compactStaged();
    ui.eventTime.value = String(nextCandidate);
    renderDraftStepPanel();
    renderCurrentStepPanel();
    setStatus(`Шаг t=${srcT} скопирован в добавляемый шаг t=${nextCandidate}`);
  }

  function duplicateDraftToNextStep() {
    if (!app.staged.length) {
      setStatus("Добавляемый шаг пуст, нечего клонировать");
      return;
    }
    const maxEventT = maxTimelineT();
    const baseT = Number.isFinite(Number(app.stagedStepT)) ? Number(app.stagedStepT) : 0;
    const nextCandidate = Math.max(maxEventT, baseT) + 1;
    app.staged = app.staged.map((e) => ({
      sid: app.nextStagedId++,
      t: nextCandidate,
      kind: e.kind,
      name: e.name,
      state: e.state,
    }));
    app.stagedStepT = nextCandidate;
    ui.eventTime.value = String(nextCandidate);
    compactStaged();
    renderDraftStepPanel();
    setStatus(`Добавляемый шаг клонирован в новый t=${nextCandidate}`);
  }

  function resetDraftStatesByKind() {
    if (!app.staged.length) {
      setStatus("Добавляемый шаг пуст");
      return;
    }
    const resetByKind = {
      rc: 0,
      signal: 0,
      switch: 3,
      indicator: 3,
    };
    app.staged.forEach((e) => {
      const nextState = resetByKind[e.kind];
      if (Number.isFinite(Number(nextState))) e.state = Number(nextState);
    });
    compactStaged();
    renderDraftStepPanel();
    setStatus("Состояния добавляемого шага сброшены по типам");
  }

  function duplicatePreviousStep() {
    const times = eventTimes();
    if (!times.length) {
      setStatus("Нет шагов для дублирования");
      return;
    }
    duplicateStepToDraft(times[times.length - 1]);
  }

  function stepForward() {
    app.currentT = Math.min(maxTimelineT(), Number(app.currentT) + 1);
    ui.playTime.value = String(app.currentT);
    render();
  }

  function jumpPrevEventTime() {
    const times = eventTimes();
    if (!times.length) return;
    const cur = Number(app.currentT);
    let target = times[0];
    for (let i = 0; i < times.length; i += 1) {
      if (times[i] < cur) target = times[i];
      else break;
    }
    app.currentT = target;
    ui.playTime.value = String(app.currentT);
    render();
  }

  function jumpNextEventTime() {
    const times = eventTimes();
    if (!times.length) return;
    const cur = Number(app.currentT);
    const target = times.find((t) => t > cur);
    if (target == null) return;
    app.currentT = target;
    ui.playTime.value = String(app.currentT);
    render();
  }

  function play() {
    if (app.timer) return;
    const times = eventTimes();
    if (!times.length) return;
    app.timer = setInterval(() => {
      const next = times.find((t) => t > app.currentT);
      if (next == null) {
        pause();
        return;
      }
      app.currentT = next;
      ui.playTime.value = String(app.currentT);
      render();
    }, 500);
  }

  function pause() {
    if (!app.timer) return;
    clearInterval(app.timer);
    app.timer = null;
  }

  function resetPlay() {
    app.currentT = 0;
    ui.playTime.value = "0";
    render();
  }

  function exportScenario() {
    sortEvents();
    const payload = {
      station: app.station,
      dt: 1,
      options: {},
      events: app.events.map((e) => ({ t: e.t, kind: e.kind, name: e.name, state: e.state })),
      steps: scenarioStepsFromEvents(),
    };
    ui.json.value = JSON.stringify(payload, null, 2);
    setStatus("Сценарий экспортирован в поле JSON");
  }

  function scenarioStepsFromEvents() {
    if (!app.events.length) return [];
    const ts = Array.from(new Set(app.events.map((e) => Number(e.t) || 0))).sort((a, b) => a - b);
    let prevT = ts[0];
    const steps = [];
    ts.forEach((t, idx) => {
      const maps = stateMapsAt(t);
      const dt = idx === 0 ? t : t - prevT;
      const linkedInd = {};
      Object.keys(maps.ind || {}).forEach((k) => {
        const nk = normalizeObjName(k);
        if (app.linkedIndicatorNames.has(nk)) linkedInd[nk] = Number(maps.ind[k]);
      });
      steps.push({
        t: dt,
        rc_states: maps.rc,
        switch_states: maps.sw,
        signal_states: maps.sig,
        indicator_states: linkedInd,
      });
      prevT = t;
    });
    return steps;
  }

  function importScenario() {
    let parsed;
    try {
      parsed = parseLooseJson(ui.json.value || "{}");
    } catch (e) {
      setStatus(`Ошибка JSON: ${e.message}`);
      return;
    }

    const imported = [];
    if (Array.isArray(parsed.events)) {
      parsed.events.forEach((e) => {
        if (!e) return;
        imported.push({
          id: app.nextEventId++,
          t: Number(e.t || 0),
          kind: String(e.kind || ""),
          name: String(e.name || ""),
          state: Number(e.state),
        });
      });
    } else if (Array.isArray(parsed.steps)) {
      let accT = 0;
      const prev = { rc: {}, sw: {}, sig: {}, ind: {} };
      parsed.steps.forEach((s) => {
        accT += Number((s && s.t) || 0);
        const cur = {
          rc: { ...(prev.rc || {}), ...((s && s.rc_states) || {}) },
          sw: { ...(prev.sw || {}), ...((s && s.switch_states) || {}) },
          sig: { ...(prev.sig || {}), ...((s && s.signal_states) || {}) },
          ind: { ...(prev.ind || {}), ...((s && s.indicator_states) || {}) },
        };

        function pushDiff(kind, mapPrev, mapCur) {
          Object.keys(mapCur).forEach((k) => {
            if (Number(mapPrev[k]) === Number(mapCur[k])) return;
            imported.push({
              id: app.nextEventId++,
              t: accT,
              kind,
              name: k,
              state: Number(mapCur[k]),
            });
          });
        }

        pushDiff("rc", prev.rc, cur.rc);
        pushDiff("switch", prev.sw, cur.sw);
        pushDiff("signal", prev.sig, cur.sig);
        pushDiff("indicator", prev.ind, cur.ind);

        prev.rc = cur.rc;
        prev.sw = cur.sw;
        prev.sig = cur.sig;
        prev.ind = cur.ind;
      });
    } else {
      setStatus("Нет events/steps для импорта");
      return;
    }

    app.events = imported;
    app.staged = [];
    app.stagedStepT = null;
    sortEvents();
    app.currentT = 0;
    ui.playTime.value = "0";
    renderDraftStepPanel();
    renderEventsTable();
    renderCurrentStepPanel();
    updateStepsInfo();
    render();
    setStatus(`Импортировано событий: ${app.events.length}`);
  }

  async function loadScheme() {
    try {
      setStatus("Загрузка схемы...");
      const [stationResp, objectsResp] = await Promise.all([
        fetch("/xml/Station.xml"),
        fetch("/xml/Objects.xml"),
      ]);
      if (!stationResp.ok) throw new Error(`Station.xml: ${stationResp.status}`);
      if (!objectsResp.ok) throw new Error(`Objects.xml: ${objectsResp.status}`);
      const stationXml = await stationResp.text();
      const objectsXml = await objectsResp.text();

      app.geom = parseStationGeometry(stationXml);
      const meta = parseObjectsMeta(objectsXml);
      app.switchTopologyByName = meta.topo;
      app.linkedIndicatorNames = meta.linkedIndicators;
      app.signalKindByName = meta.signalKinds || new Map();
      app.switchToSectionByName = new Map();
      app.switchTopologyByName.forEach((topo, sw) => {
        if (topo && topo.section) app.switchToSectionByName.set(sw, normalizeObjName(topo.section));
      });

      if (!app.selected) {
        selectObject("rc", app.geom.rails[0] ? app.geom.rails[0].name : "");
      }
      app.allNames = {
        rc: app.geom.rails.map((x) => x.name),
        switch: app.geom.switches.map((x) => x.name),
        signal: app.geom.signals.map((x) => x.name),
        indicator: app.geom.indicators.map((x) => x.name),
      };
      renderEventsTable();
      renderDraftStepPanel();
      renderCurrentStepPanel();
      updateStepsInfo();
      render();
      setStatus(`Схема загружена. РЦ: ${app.geom.rails.length}, Стрелки: ${app.geom.switches.length}, Сигналы: ${app.geom.signals.length}, Индикаторы: ${app.geom.indicators.length}`);
    } catch (e) {
      setStatus(`Ошибка: ${e.message}`);
      // eslint-disable-next-line no-console
      console.error(e);
    }
  }

  function bind() {
    const on = (el, ev, handler) => {
      if (el) el.addEventListener(ev, handler);
    };
    bindViewportDrag();
    on(ui.btnPanMode, "click", () => {
      applyPanMode(!app.panModeUser, true);
      setStatus("Режим изменен");
    });
    on(ui.btnZoomIn, "click", () => {
      app.zoom = Math.min(3, Number(app.zoom || 1) + 0.1);
      applyViewTransform();
    });
    on(ui.btnZoomOut, "click", () => {
      app.zoom = Math.max(0.5, Number(app.zoom || 1) - 0.1);
      applyViewTransform();
    });
    on(ui.btnZoomReset, "click", () => {
      app.zoom = 1;
      applyViewTransform();
    });
    on(ui.btnLoad, "click", loadScheme);
    on(ui.btnClear, "click", clearEvents);
    on(ui.btnNextStep, "click", setNextStepTime);
    on(ui.btnDupPrevStep, "click", duplicatePreviousStep);
    on(ui.btnStage, "click", stageEventFromForm);
    on(ui.btnApplyBatch, "click", applyBatch);
    on(ui.btnPrevEvent, "click", jumpPrevEventTime);
    on(ui.btnNextEvent, "click", jumpNextEventTime);
    on(ui.btnReset, "click", resetPlay);
    on(ui.eventTime, "change", renderCurrentStepPanel);
    on(ui.eventTime, "input", renderCurrentStepPanel);
    on(ui.eventTime, "change", renderDraftStepPanel);
    on(ui.eventTime, "input", renderDraftStepPanel);
    on(ui.btnExport, "click", exportScenario);
    on(ui.btnImport, "click", importScenario);
    on(ui.btnLoadPreset, "click", async () => {
      try {
        const txt = await loadPresetContent(ui.presetSelect.value);
        ui.json.value = txt;
        importScenario();
        setStatus(`Загружен preset: ${ui.presetSelect.value}`);
      } catch (e) {
        setStatus(`Ошибка preset: ${e.message}`);
      }
    });
    on(ui.btnCopyPresetJson, "click", async () => {
      try {
        const txt = await loadPresetContent(ui.presetSelect.value);
        ui.json.value = txt;
        setStatus(`Preset вставлен в JSON: ${ui.presetSelect.value}`);
      } catch (e) {
        setStatus(`Ошибка preset: ${e.message}`);
      }
    });
    on(ui.playTime, "change", () => {
      app.currentT = Math.max(0, Number(ui.playTime.value || 0));
      render();
    });
    on(ui.eventState, "change", updateStateHelp);
    window.addEventListener("keydown", (e) => {
      if (e.code !== "Space") return;
      const tag = String((e.target && e.target.tagName) || "").toUpperCase();
      const editable = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (e.target && e.target.isContentEditable);
      if (editable) return;
      if (app.spaceHold) return;
      app.spaceHold = true;
      if (!app.panMode) {
        applyPanMode(true, false);
        setStatus("Временный режим: Рука (Space)");
      }
      e.preventDefault();
    });
    window.addEventListener("keyup", (e) => {
      if (e.code !== "Space") return;
      if (!app.spaceHold) return;
      app.spaceHold = false;
      applyPanMode(app.panModeUser, false);
      setStatus("Возврат в основной режим");
      e.preventDefault();
    });
  }

  function init() {
    bind();
    fillPresetSelect();
    try {
      const pm = localStorage.getItem("sandbox_pan_mode");
      applyPanMode(pm === "1", true);
    } catch (_) {
      applyPanMode(false, true);
    }
    try {
      const z = Number(localStorage.getItem("sandbox_zoom") || "1");
      app.zoom = Number.isFinite(z) ? z : 1;
    } catch (_) {
      app.zoom = 1;
    }
    try {
      const p = JSON.parse(localStorage.getItem("sandbox_pan") || "{\"x\":0,\"y\":0}");
      app.panX = Number.isFinite(Number(p.x)) ? Number(p.x) : 0;
      app.panY = Number.isFinite(Number(p.y)) ? Number(p.y) : 0;
    } catch (_) {
      app.panX = 0;
      app.panY = 0;
    }
    applyViewTransform();
    fillStateOptions("rc");
    ui.json.value = JSON.stringify({
      station: "Visochino",
      dt: 1,
      options: {},
      events: [],
      steps: [],
    }, null, 2);
    if (ui.eventTime) ui.eventTime.value = "1";
    updateStepsInfo();
    setStatus("Нажмите 'Загрузить схему'");
  }

  init();
})();
