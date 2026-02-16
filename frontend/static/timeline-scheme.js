// static/timeline-scheme.js

let layoutState = {
  loading: null,
  data: null,
  error: null,
};

function svgEl(name, attrs = {}) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", name);
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, String(v)));
  return el;
}

function normRcKey(value) {
  if (!value) return "";
  return String(value)
    .toUpperCase()
    .replace(/&SOL;/g, "/")
    .replace(/\u0421\u041F/g, "SP")
    .replace(/\u0410\u041F/g, "AP")
    .replace(/\u041d\u0414\u041f/g, "NDP")
    .replace(/\u0427\u0414\u041f/g, "CHDP")
    .replace(/\u041d\u041f/g, "NP")
    .replace(/\u0427\u041f/g, "CHP")
    .replace(/\u041f/g, "P")
    .replace(/\u0410/g, "A")
    .replace(/\u041d/g, "N")
    .replace(/\u0427/g, "CH")
    .replace(/\u0414/g, "D")
    .replace(/[^A-Z0-9/_-]+/g, "");
}

function normSwitchKey(value) {
  if (!value) return "";
  return String(value).toUpperCase().replace(/^SW/, "");
}

async function ensureLayoutLoaded() {
  if (layoutState.data || layoutState.error) return;
  if (layoutState.loading) {
    await layoutState.loading;
    return;
  }

  const station = (window.scenario && window.scenario.station) ? window.scenario.station : "Visochino";
  layoutState.loading = fetch(`/station-layout?station=${encodeURIComponent(station)}&_ts=${Date.now()}`, {
    cache: "no-store",
  })
    .then(async (resp) => {
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const data = await resp.json();
      layoutState.data = data;
      window.stationLayoutData = data;
      renderTrackScheme(data);
      if (typeof window.initScenarioTable === "function") {
        window.initScenarioTable();
      }
    })
    .catch((err) => {
      layoutState.error = String(err);
      console.error("Failed to load /station-layout", err);
    })
    .finally(() => {
      layoutState.loading = null;
    });

  await layoutState.loading;
}

function renderTrackScheme(layout) {
  const svg = document.getElementById("track-svg");
  if (!svg || !layout) return;

  const bounds = layout.bounds || {};
  const padding = Number(bounds.padding ?? 40);
  const minX = Number(bounds.min_x ?? 0) - padding;
  const minY = Number(bounds.min_y ?? 0) - padding;
  const width = Number(bounds.width ?? 1) + padding * 2;
  const height = Number(bounds.height ?? 1) + padding * 2;
  svg.setAttribute("viewBox", `${minX} ${minY} ${Math.max(width, 1)} ${Math.max(height, 1)}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

  svg.replaceChildren();

  const gRails = svgEl("g", { id: "dyn-rails" });
  const gSwitches = svgEl("g", { id: "dyn-switches" });
  const gSignals = svgEl("g", { id: "dyn-signals" });
  const gLabels = svgEl("g", { id: "dyn-labels" });

  (layout.rails || []).forEach((rail) => {
    const points = rail.points || [];
    if (points.length < 2) return;
    const poly = svgEl("polyline", {
      points: points.map((p) => `${p[0]},${p[1]}`).join(" "),
      class: "rc-line rc-main",
      "data-rc-id": rail.group_name || "",
      "data-rc-key": rail.group_key || normRcKey(rail.group_name),
    });
    gRails.appendChild(poly);
  });

  (layout.switches || []).forEach((sw) => {
    const swKey = sw.switch_key || normSwitchKey(sw.switch_name);
    const switchToRc = layout.switch_to_rc || {};
    const mappedRcName = switchToRc[String(sw.switch_name || "")] || "";
    const mappedRcKey = normRcKey(mappedRcName);
    const parts = [
      { points: sw.section || [], cls: "rc-line rc-main" },
      { points: sw.plus || [], cls: "rc-line rc-branch" },
      { points: sw.minus || [], cls: "rc-line rc-branch" },
    ];
    parts.forEach((part) => {
      if (!part.points.length) return;
      const poly = svgEl("polyline", {
        points: part.points.map((p) => `${p[0]},${p[1]}`).join(" "),
        class: part.cls,
        "data-switch-id": sw.switch_name || "",
        "data-switch-key": swKey,
        "data-rc-key": mappedRcKey,
      });
      gSwitches.appendChild(poly);
    });

    const label = svgEl("text", {
      x: sw.x,
      y: sw.y,
      class: "sw-label sw-dynamic-label",
      "data-switch-label": sw.switch_name || "",
      "data-switch-key": swKey,
      "text-anchor": "middle",
    });
    label.textContent = sw.switch_name || "";
    gLabels.appendChild(label);
  });

  (layout.signals || []).forEach((sig) => {
    const circle = svgEl("circle", {
      cx: sig.x,
      cy: sig.y,
      r: sig.radius || 7,
      class: "signal-circle",
      "data-signal-id": sig.signal_name || "",
      "data-signal-key": sig.signal_key || "",
    });
    gSignals.appendChild(circle);

    const t = svgEl("text", {
      x: sig.x + 12,
      y: sig.y + 4,
      class: "signal-text",
      "font-size": "11",
    });
    t.textContent = sig.signal_name || "";
    gLabels.appendChild(t);
  });

  (layout.labels || [])
    .filter((x) => (x.text || "").match(/^[0-9]+(?:-[0-9]+)?(?:SP|СП|P|П)?$/))
    .forEach((lbl) => {
      const t = svgEl("text", {
        x: lbl.x,
        y: lbl.y,
        class: "rc-label",
        "font-size": "12",
      });
      t.textContent = lbl.text;
      gLabels.appendChild(t);
    });

  svg.appendChild(gRails);
  svg.appendChild(gSwitches);
  svg.appendChild(gSignals);
  svg.appendChild(gLabels);
}

function highlightRcLine(lineEl, stateValue) {
  if (!lineEl) return;

  lineEl.classList.remove("rc-line-free", "rc-line-locked", "rc-line-occupied");
  const v = Number(stateValue);
  const isFree = [3, 4, 5].includes(v);
  const isOcc = [6, 7, 8].includes(v);
  const isLock = [4, 5, 7, 8].includes(v);

  if (isOcc) {
    lineEl.classList.add("rc-line-occupied");
  } else if (isLock) {
    lineEl.classList.add("rc-line-locked");
  } else if (isFree) {
    lineEl.classList.add("rc-line-free");
  }
}

function decorateSwitchIndicator(el, state) {
  if (!el) return;
  el.classList.remove("sw-indicator-plus", "sw-indicator-minus", "sw-indicator-unknown", "sw-indicator-lost");
  const v = Number(state);
  if ([15, 16, 17, 18, 19, 20].includes(v)) {
    el.classList.add("sw-indicator-lost");
  } else if (v === 21) {
    el.classList.add("sw-indicator-unknown");
  } else if ([3, 4, 5, 6, 7, 8].includes(v)) {
    el.classList.add("sw-indicator-plus");
  } else if ([9, 10, 11, 12, 13, 14].includes(v)) {
    el.classList.add("sw-indicator-minus");
  }
}

function updateTrackScheme(row) {
  if (!row) return;
  if (!layoutState.data && !layoutState.error) {
    ensureLayoutLoaded();
  }

  const rcStates = row.rc_states || row.rcstates || {};
  const swStates = row.switch_states || row.switchstates || {};
  const sigStates = row.signal_states || row.signalstates || {};

  const rcByNorm = new Map();
  Object.entries(rcStates).forEach(([k, v]) => rcByNorm.set(normRcKey(k), v));
  const swByNorm = new Map();
  Object.entries(swStates).forEach(([k, v]) => swByNorm.set(normSwitchKey(k), v));

  document.querySelectorAll("[data-rc-key]").forEach((el) => {
    const key = el.getAttribute("data-rc-key") || "";
    const state = rcByNorm.get(key);
    highlightRcLine(el, state);
  });

  document.querySelectorAll("[data-switch-key]").forEach((el) => {
    const key = el.getAttribute("data-switch-key") || "";
    const state = swByNorm.get(key);
    if (el.classList.contains("sw-dynamic-label")) {
      decorateSwitchIndicator(el, state);
    }
  });

  if (window.applySignalClass) {
    document.querySelectorAll("[data-signal-id]").forEach((el) => {
      const sigId = el.getAttribute("data-signal-id");
      const state = sigStates[sigId] ?? 0;
      const code = String(sigId || "").startsWith("М") ? 3 : 4;
      window.applySignalClass(el, state, code);
    });
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    ensureLayoutLoaded();
  });
} else {
  ensureLayoutLoaded();
}

export { updateTrackScheme, ensureLayoutLoaded };
window.updateTrackScheme = updateTrackScheme;
window.ensureLayoutLoaded = ensureLayoutLoaded;

