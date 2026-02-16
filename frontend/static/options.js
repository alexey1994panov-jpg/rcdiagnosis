// static/options.js
// Р§С‚РµРЅРёРµ РїР°СЂР°РјРµС‚СЂРѕРІ Р›Р—/Р›РЎ/РёСЃРєР»СЋС‡РµРЅРёР№ РёР· HTML-С„РѕСЂРј Рё Р·Р°РїРёСЃСЊ РІ scenario.options

const LEGACY_TO_CANONICAL_OPTION_KEYS = {
  tmu: "t_mu",
  trecentls: "t_recent_ls",
  tminmaneuverv8: "t_min_maneuver_v8",
  enablelzexcmu: "enable_lz_exc_mu",
  enablelzexcrecentls: "enable_lz_exc_recent_ls",
  enablelzexcdsp: "enable_lz_exc_dsp",
  tlsmu: "t_ls_mu",
  tlsafterlz: "t_ls_after_lz",
  tlsdsp: "t_ls_dsp",
  enablelsexcmu: "enable_ls_exc_mu",
  enablelsexcafterlz: "enable_ls_exc_after_lz",
  enablelsexcdsp: "enable_ls_exc_dsp",
  t_s0101: "ts01_lz1",
  t_lz01: "tlz_lz1",
  t_kon_v1: "tkon_lz1",
  enable_v1: "enable_lz1",
  t_s0102: "ts01_lz2",
  t_s0202: "ts02_lz2",
  t_lz02: "tlz_lz2",
  t_kon_v2: "tkon_lz2",
  enable_v2: "enable_lz2",
  t_s0103: "ts01_lz3",
  t_s0203: "ts02_lz3",
  t_lz03: "tlz_lz3",
  t_kon_v3: "tkon_lz3",
  enable_v3: "enable_lz3",
  t_s0401: "ts01_lz4",
  t_lz04: "tlz_lz4",
  t_kon_v4: "tkon_lz4",
  enable_v4: "enable_lz4",
  t_s05: "ts01_lz5",
  t_lz05: "tlz_lz5",
  t_kon_v5: "tkon_lz5",
  enable_v5: "enable_lz5",
  t_s06: "ts01_lz6",
  t_lz06: "tlz_lz6",
  t_kon_v6: "tkon_lz6",
  enable_v6: "enable_lz6",
  t_s07: "ts01_lz7",
  t_lz07: "tlz_lz7",
  t_kon_v7: "tkon_lz7",
  enable_v7: "enable_lz7",
  t_s0108: "ts01_lz8",
  t_s0208: "ts02_lz8",
  t_lz08: "tlz_lz8",
  t_kon_v8: "tkon_lz8",
  enable_v8: "enable_lz8",
  t_s0109: "ts01_lz9",
  t_lz09: "tlz_lz9",
  t_kon_v9: "tkon_lz9",
  enable_v9: "enable_lz9",
  t_s0110: "ts01_lz10",
  t_s0210: "ts02_lz10",
  t_s0310: "ts03_lz10",
  t_lz10: "tlz_lz10",
  t_kon_v10: "tkon_lz10",
  enable_v10: "enable_lz10",
  t_s11: "ts01_lz11",
  t_lz11: "tlz_lz11",
  t_kon_v11: "tkon_lz11",
  enable_v11: "enable_lz11",
  t_s0112: "ts01_lz12",
  t_s0212: "ts02_lz12",
  t_lz12: "tlz_lz12",
  t_kon_v12: "tkon_lz12",
  enable_v12: "enable_lz12",
  t_s0113: "ts01_lz13",
  t_s0213: "ts02_lz13",
  t_lz13: "tlz_lz13",
  t_kon_v13: "tkon_lz13",
  enable_v13: "enable_lz13",
  t_c0101_ls: "ts01_ls1",
  t_ls01: "tlz_ls1",
  t_kon_ls1: "tkon_ls1",
  t_s0102_ls: "ts01_ls2",
  t_s0202_ls: "ts02_ls2",
  t_ls0102: "tlz_ls2",
  t_kon_ls2: "tkon_ls2",
  t_s0104_ls: "ts01_ls4",
  t_s0204_ls: "ts02_ls4",
  t_ls0104: "tlz01_ls4",
  t_ls0204: "tlz02_ls4",
  t_kon_ls4: "tkon_ls4",
  t_s0105_ls: "ts01_ls5",
  t_ls05: "tlz_ls5",
  t_kon_ls5: "tkon_ls5",
  t_s0106_ls: "ts01_ls6",
  t_ls06: "tlz_ls6",
  t_kon_ls6: "tkon_ls6",
  t_s0109_ls: "ts01_ls9",
  t_ls0109: "tlz_ls9",
  t_kon_ls9: "tkon_ls9",
};

function normalizeOptionsForJson(options) {
  const src = options || {};
  const out = { ...src };
  Object.entries(LEGACY_TO_CANONICAL_OPTION_KEYS).forEach(([legacy, canonical]) => {
    if (legacy in out && !(canonical in out)) out[canonical] = out[legacy];
    if (canonical in out) delete out[legacy];
  });
  [
    "t_s0204_ls",
    "t_s0209_ls",
    "t_ls0209",
    "t_pause_v1", "t_pause_v2", "t_pause_v3", "t_pause_v4", "t_pause_v5", "t_pause_v6", "t_pause_v7",
    "t_pause_v8", "t_pause_v9", "t_pause_v10", "t_pause_v11", "t_pause_v12", "t_pause_v13",
    "t_pause_ls1", "t_pause_ls2", "t_pause_ls4", "t_pause_ls5", "t_pause_ls6", "t_pause_ls9",
  ].forEach((k) => { delete out[k]; });
  return out;
}

// --- РћСЃРЅРѕРІРЅР°СЏ С„СѓРЅРєС†РёСЏ: СЃРѕР±СЂР°С‚СЊ РІСЃРµ РїР°СЂР°РјРµС‚СЂС‹ РёР· С„РѕСЂРј ---
function updateOptionsFromForm() {
  function getVal(id) {
    const el = document.getElementById(id);
    if (!el) return undefined;
    const raw = el.value;
    if (raw === "" || raw == null) return undefined;
    const v = parseFloat(raw);
    return Number.isNaN(v) ? undefined : v;
  }

  function getCheck(id) {
    const el = document.getElementById(id);
    return el ? el.checked : undefined;
  }

  function getSelect(id) {
    const el = document.getElementById(id);
    return el ? el.value : undefined;
  }

  function compact(obj) {
    const out = {};
    Object.entries(obj || {}).forEach(([k, v]) => {
      if (v !== undefined) out[k] = v;
    });
    return out;
  }

  const fromForm = {
    t_s0101: getVal("ts0101"),
    t_lz01: getVal("tlz01"),
    t_kon_v1: getVal("tkonv1"),
    enable_v1: getCheck("enablev1"),

    t_s0102: getVal("ts0102"),
    t_s0202: getVal("ts0202"),
    t_lz02: getVal("tlz02"),
    t_kon_v2: getVal("tkonv2"),
    enable_v2: getCheck("enablev2"),

    t_s0103: getVal("ts0103"),
    t_s0203: getVal("ts0203"),
    t_lz03: getVal("tlz03"),
    t_kon_v3: getVal("tkonv3"),
    enable_v3: getCheck("enablev3"),

    t_s0401: getVal("ts0401"),
    t_lz04: getVal("tlz04"),
    t_kon_v4: getVal("tkonv4"),
    enable_v4: getCheck("enablev4"),

    t_s05: getVal("ts05"),
    t_lz05: getVal("tlz05"),
    t_pk: getVal("tpk"),
    t_kon_v5: getVal("tkonv5"),
    enable_v5: getCheck("enablev5"),

    t_s06: getVal("ts06"),
    t_lz06: getVal("tlz06"),
    t_kon_v6: getVal("tkonv6"),
    enable_v6: getCheck("enablev6"),

    t_s07: getVal("ts07"),
    t_lz07: getVal("tlz07"),
    t_kon_v7: getVal("tkonv7"),
    enable_v7: getCheck("enablev7"),

    t_s0108: getVal("ts0108"),
    t_s0208: getVal("ts0208"),
    t_lz08: getVal("tlz08"),
    t_kon_v8: getVal("tkonv8"),
    enable_v8: getCheck("enablev8"),

    t_s0109: getVal("ts0109"),
    t_lz09: getVal("tlz09"),
    t_kon_v9: getVal("tkonv9"),
    enable_v9: getCheck("enablev9"),

    t_s0110: getVal("ts0110"),
    t_s0210: getVal("ts0210"),
    t_s0310: getVal("ts0310"),
    t_lz10: getVal("tlz10"),
    t_kon_v10: getVal("tkonv10"),
    enable_v10: getCheck("enablev10"),

    t_s11: getVal("ts11"),
    t_lz11: getVal("tlz11"),
    t_kon_v11: getVal("tkonv11"),
    enable_v11: getCheck("enablev11"),

    t_s0112: getVal("ts0112"),
    t_s0212: getVal("ts0212"),
    t_lz12: getVal("tlz12"),
    t_kon_v12: getVal("tkonv12"),
    enable_v12: getCheck("enablev12"),

    t_s0113: getVal("ts0113"),
    t_s0213: getVal("ts0213"),
    t_lz13: getVal("tlz13"),
    t_kon_v13: getVal("tkonv13"),
    enable_v13: getCheck("enablev13"),

    t_c0101_ls: getVal("tc0101ls"),
    t_ls01: getVal("tls01"),
    t_kon_ls1: getVal("tkonls1"),
    t_pause_ls1: getVal("tpausels1"),
    enable_ls1: getCheck("enablels1"),

    t_s0102_ls: getVal("ts0102ls"),
    t_s0202_ls: getVal("ts0202ls"),
    t_ls0102: getVal("tls0102"),
    t_kon_ls2: getVal("tkonls2"),
    t_pause_ls2: getVal("tpausels2"),
    enable_ls2: getCheck("enablels2"),

    t_s0104_ls: getVal("ts0104ls"),
    t_s0204_ls: getVal("ts0204ls"),
    t_ls0104: getVal("tls0104"),
    t_ls0204: getVal("tls0204"),
    t_kon_ls4: getVal("tkonls4"),
    t_pause_ls4: getVal("tpausels4"),
    enable_ls4: getCheck("enablels4"),

    t_s0105_ls: getVal("ts0105ls"),
    t_ls05: getVal("tls05"),
    t_kon_ls5: getVal("tkonls5"),
    t_pause_ls5: getVal("tpausels5"),
    enable_ls5: getCheck("enablels5"),

    t_s0106_ls: getVal("ts0106ls"),
    t_ls06: getVal("tls06"),
    t_kon_ls6: getVal("tkonls6"),
    t_pause_ls6: getVal("tpausels6"),
    enable_ls6: getCheck("enablels6"),

    t_s0109_ls: getVal("ts0109ls"),
    t_s0209_ls: getVal("ts0209ls"),
    t_ls0109: getVal("tls0109"),
    t_ls0209: getVal("tls0209"),
    t_kon_ls9: getVal("tkonls9"),
    t_pause_ls9: getVal("tpausels9"),
    enable_ls9: getCheck("enablels9"),

    t_mu: getVal("tmu"),
    t_recent_ls: getVal("trecentls"),
    t_min_maneuver_v8: getVal("tminmaneuverv8"),
    enable_lz_exc_mu: getCheck("enablelzexcmu"),
    enable_lz_exc_recent_ls: getCheck("enablelzexcrecentls"),
    enable_lz_exc_dsp: getCheck("enablelzexcdsp"),

    t_ls_mu: getVal("tlsmu"),
    t_ls_after_lz: getVal("tlsafterlz"),
    t_ls_dsp: getVal("tlsdsp"),
    enable_ls_exc_mu: getCheck("enablelsexcmu"),
    enable_ls_exc_after_lz: getCheck("enablelsexcafterlz"),
    enable_ls_exc_dsp: getCheck("enablelsexcdsp"),
  };

  // Важно: значения из формы должны побеждать уже существующие canonical-ключи.
  // Поэтому сначала нормализуем только form-патч, затем накладываем его поверх scenario.options.
  const normalizedFormPatch = normalizeOptionsForJson(compact(fromForm));
  scenario.options = normalizeOptionsForJson({
    ...(scenario.options || {}),
    ...normalizedFormPatch,
  });
}
window.updateOptionsFromForm = updateOptionsFromForm;
window.normalizeOptionsForJson = normalizeOptionsForJson;

function fillOptionsFormFromScenario() {
  if (!window.scenario) return;
  window.scenario.options = normalizeOptionsForJson(window.scenario.options || {});

  if (typeof window.applyDefaultsToFragment !== "function") return;

  const loaded = window.loadedFragments || {};
  ["tab-lz-exc", "tab-ls-exc", "tab-exc-config"].forEach((tabId) => {
    if (loaded[tabId]) {
      window.applyDefaultsToFragment(tabId);
    }
  });
}
window.fillOptionsFormFromScenario = fillOptionsFormFromScenario;

async function loadDefaults() {
  const resp = await fetch(`/defaults?_ts=${Date.now()}`, { cache: "no-store" });
  if (!resp.ok) {
    throw new Error(`defaults HTTP ${resp.status}`);
  }
  const defaults = await resp.json();
  scenario.options = normalizeOptionsForJson({
    ...(scenario.options || {}),
    ...(defaults || {}),
  });
  window.scenario = scenario;

  // Apply defaults to already loaded tab fragments.
  if (typeof window.loadedFragments === "object" && window.loadedFragments) {
    ["tab-lz-exc", "tab-ls-exc", "tab-exc-config"].forEach((tabId) => {
      if (window.loadedFragments[tabId] && typeof window.applyDefaultsToFragment === "function") {
        window.applyDefaultsToFragment(tabId);
      }
    });
  }

  if (typeof window.renderScenarioTextarea === "function") {
    window.renderScenarioTextarea();
  }
}

window.loadDefaults = loadDefaults;

