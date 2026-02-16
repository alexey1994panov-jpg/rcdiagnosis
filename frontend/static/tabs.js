// static/tabs.js

function initTabs() {
  const buttons = document.querySelectorAll(".tab-button");
  const contents = document.querySelectorAll(".tab-content");

  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const tabId = btn.getAttribute("data-tab");
      buttons.forEach((b) => b.classList.remove("active"));
      contents.forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      const targetContent = document.getElementById(tabId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
      await loadTabFragment(tabId);
    });
  });

  const activeBtn = document.querySelector(".tab-button.active");
  if (activeBtn) {
    const firstTabId = activeBtn.getAttribute("data-tab");
    loadTabFragment(firstTabId);
  }
}
window.initTabs = initTabs;

const fragmentMap = {
  "tab-lz-exc": "static/fragments/lz_all_exc.html",
  "tab-ls-exc": "static/fragments/ls_all_exc.html",
  "tab-exc-config": "static/fragments/exceptions_config.html",
};

async function loadTabFragment(tabId) {
  if (!window.loadedFragments) {
    window.loadedFragments = {};
  }

  const runTabInit = async () => {
    if (tabId === "tab-exc-config" && typeof window.loadExceptionsConfig === "function") {
      await window.loadExceptionsConfig();
    }
  };

  if (window.loadedFragments[tabId]) {
    await runTabInit();
    return;
  }

  const url = fragmentMap[tabId];
  if (!url) {
    window.loadedFragments[tabId] = true;
    await runTabInit();
    return;
  }

  try {
    const sep = url.includes("?") ? "&" : "?";
    const bustUrl = `${url}${sep}_ts=${Date.now()}`;
    const resp = await fetch(bustUrl, { cache: "no-store" });
    if (!resp.ok) {
      console.error("Failed to load fragment", url, resp.status);
      const container = document.getElementById(tabId);
      if (container) {
        container.innerHTML = `<p style="color:red;">Ошибка загрузки фрагмента (${resp.status})</p>`;
      }
      return;
    }

    const html = await resp.text();
    const container = document.getElementById(tabId);
    if (container) {
      container.innerHTML = html;
    }

    window.loadedFragments[tabId] = true;
    await runTabInit();

    if (window.scenario && window.scenario.options && Object.keys(window.scenario.options).length > 0) {
      applyDefaultsToFragment(tabId);
    }
  } catch (e) {
    console.error("Error loading fragment", url, e);
    const container = document.getElementById(tabId);
    if (container) {
      container.innerHTML = `<p style="color:red;">${e.message}</p>`;
    }
  }
}

function applyDefaultsToFragment(tabId) {
  const data = (window.scenario && window.scenario.options) || {};
  if (!data) return;
  const legacyToCanonical = {
    t_s0101: "ts01_lz1", t_lz01: "tlz_lz1", t_kon_v1: "tkon_lz1", enable_v1: "enable_lz1",
    t_s0102: "ts01_lz2", t_s0202: "ts02_lz2", t_lz02: "tlz_lz2", t_kon_v2: "tkon_lz2", enable_v2: "enable_lz2",
    t_s0103: "ts01_lz3", t_s0203: "ts02_lz3", t_lz03: "tlz_lz3", t_kon_v3: "tkon_lz3", enable_v3: "enable_lz3",
    t_s0401: "ts01_lz4", t_lz04: "tlz_lz4", t_kon_v4: "tkon_lz4", enable_v4: "enable_lz4",
    t_s05: "ts01_lz5", t_lz05: "tlz_lz5", t_kon_v5: "tkon_lz5", enable_v5: "enable_lz5",
    t_s06: "ts01_lz6", t_lz06: "tlz_lz6", t_kon_v6: "tkon_lz6", enable_v6: "enable_lz6",
    t_s07: "ts01_lz7", t_lz07: "tlz_lz7", t_kon_v7: "tkon_lz7", enable_v7: "enable_lz7",
    t_s0108: "ts01_lz8", t_s0208: "ts02_lz8", t_lz08: "tlz_lz8", t_kon_v8: "tkon_lz8", enable_v8: "enable_lz8",
    t_s0109: "ts01_lz9", t_lz09: "tlz_lz9", t_kon_v9: "tkon_lz9", enable_v9: "enable_lz9",
    t_s0110: "ts01_lz10", t_s0210: "ts02_lz10", t_s0310: "ts03_lz10", t_lz10: "tlz_lz10", t_kon_v10: "tkon_lz10", enable_v10: "enable_lz10",
    t_s11: "ts01_lz11", t_lz11: "tlz_lz11", t_kon_v11: "tkon_lz11", enable_v11: "enable_lz11",
    t_s0112: "ts01_lz12", t_s0212: "ts02_lz12", t_lz12: "tlz_lz12", t_kon_v12: "tkon_lz12", enable_v12: "enable_lz12",
    t_s0113: "ts01_lz13", t_s0213: "ts02_lz13", t_lz13: "tlz_lz13", t_kon_v13: "tkon_lz13", enable_v13: "enable_lz13",
    t_c0101_ls: "ts01_ls1", t_ls01: "tlz_ls1", t_kon_ls1: "tkon_ls1",
    t_s0102_ls: "ts01_ls2", t_s0202_ls: "ts02_ls2", t_ls0102: "tlz_ls2", t_kon_ls2: "tkon_ls2",
    t_s0104_ls: "ts01_ls4", t_s0204_ls: "ts02_ls4", t_ls0104: "tlz01_ls4", t_ls0204: "tlz02_ls4", t_kon_ls4: "tkon_ls4",
    t_s0105_ls: "ts01_ls5", t_ls05: "tlz_ls5", t_kon_ls5: "tkon_ls5",
    t_s0106_ls: "ts01_ls6", t_ls06: "tlz_ls6", t_kon_ls6: "tkon_ls6",
    t_s0109_ls: "ts01_ls9", t_ls0109: "tlz_ls9", t_kon_ls9: "tkon_ls9",
  };
  const canonicalToLegacy = Object.fromEntries(Object.entries(legacyToCanonical).map(([k, v]) => [v, k]));

  function setVal(id, key, type = "number") {
    const el = document.getElementById(id);
    if (!el) return;
    const val = data[key] ?? data[canonicalToLegacy[key]];
    if (val === undefined || val === null) return;
    if (type === "check") el.checked = Boolean(val);
    else el.value = String(val);
  }

  if (tabId === "tab-lz-exc") {
    setVal("tmu", "t_mu");
    setVal("trecentls", "t_recent_ls");
    setVal("tminmaneuverv8", "t_min_maneuver_v8");
    setVal("enablelzexcmu", "enable_lz_exc_mu", "check");
    setVal("enablelzexcrecentls", "enable_lz_exc_recent_ls", "check");
    setVal("enablelzexcdsp", "enable_lz_exc_dsp", "check");
    setVal("tpk", "t_pk");

    setVal("ts0101", "ts01_lz1"); setVal("tlz01", "tlz_lz1"); setVal("tkonv1", "tkon_lz1"); setVal("enablev1", "enable_lz1", "check");
    setVal("ts0102", "ts01_lz2"); setVal("ts0202", "ts02_lz2"); setVal("tlz02", "tlz_lz2"); setVal("tkonv2", "tkon_lz2"); setVal("enablev2", "enable_lz2", "check");
    setVal("ts0103", "ts01_lz3"); setVal("ts0203", "ts02_lz3"); setVal("tlz03", "tlz_lz3"); setVal("tkonv3", "tkon_lz3"); setVal("enablev3", "enable_lz3", "check");
    setVal("ts0401", "ts01_lz4"); setVal("tlz04", "tlz_lz4"); setVal("tkonv4", "tkon_lz4"); setVal("enablev4", "enable_lz4", "check");
    setVal("ts05", "ts01_lz5"); setVal("tlz05", "tlz_lz5"); setVal("tkonv5", "tkon_lz5"); setVal("enablev5", "enable_lz5", "check");
    setVal("ts06", "ts01_lz6"); setVal("tlz06", "tlz_lz6"); setVal("tkonv6", "tkon_lz6"); setVal("enablev6", "enable_lz6", "check");
    setVal("ts07", "ts01_lz7"); setVal("tlz07", "tlz_lz7"); setVal("tkonv7", "tkon_lz7"); setVal("enablev7", "enable_lz7", "check");
    setVal("ts0108", "ts01_lz8"); setVal("ts0208", "ts02_lz8"); setVal("tlz08", "tlz_lz8"); setVal("tkonv8", "tkon_lz8"); setVal("enablev8", "enable_lz8", "check");
    setVal("ts0109", "ts01_lz9"); setVal("tlz09", "tlz_lz9"); setVal("tkonv9", "tkon_lz9"); setVal("enablev9", "enable_lz9", "check");
    setVal("ts0110", "ts01_lz10"); setVal("ts0210", "ts02_lz10"); setVal("ts0310", "ts03_lz10"); setVal("tlz10", "tlz_lz10"); setVal("tkonv10", "tkon_lz10"); setVal("enablev10", "enable_lz10", "check");
    setVal("ts11", "ts01_lz11"); setVal("tlz11", "tlz_lz11"); setVal("tkonv11", "tkon_lz11"); setVal("enablev11", "enable_lz11", "check");
    setVal("ts0112", "ts01_lz12"); setVal("ts0212", "ts02_lz12"); setVal("tlz12", "tlz_lz12"); setVal("tkonv12", "tkon_lz12"); setVal("enablev12", "enable_lz12", "check");
    setVal("ts0113", "ts01_lz13"); setVal("ts0213", "ts02_lz13"); setVal("tlz13", "tlz_lz13"); setVal("tkonv13", "tkon_lz13"); setVal("enablev13", "enable_lz13", "check");
  }

  if (tabId === "tab-ls-exc") {
    setVal("tlsmu", "t_ls_mu");
    setVal("tlsafterlz", "t_ls_after_lz");
    setVal("tlsdsp", "t_ls_dsp");
    setVal("enablelsexcmu", "enable_ls_exc_mu", "check");
    setVal("enablelsexcafterlz", "enable_ls_exc_after_lz", "check");
    setVal("enablelsexcdsp", "enable_ls_exc_dsp", "check");

    setVal("tc0101ls", "ts01_ls1"); setVal("tls01", "tlz_ls1"); setVal("tkonls1", "tkon_ls1"); setVal("enablels1", "enable_ls1", "check");
    setVal("ts0102ls", "ts01_ls2"); setVal("ts0202ls", "ts02_ls2"); setVal("tls0102", "tlz_ls2"); setVal("tkonls2", "tkon_ls2"); setVal("enablels2", "enable_ls2", "check");
    setVal("ts0104ls", "ts01_ls4"); setVal("ts0204ls", "ts02_ls4"); setVal("tls0104", "tlz01_ls4"); setVal("tls0204", "tlz02_ls4"); setVal("tkonls4", "tkon_ls4"); setVal("enablels4", "enable_ls4", "check");
    setVal("ts0105ls", "ts01_ls5"); setVal("tls05", "tlz_ls5"); setVal("tkonls5", "tkon_ls5"); setVal("enablels5", "enable_ls5", "check");
    setVal("ts0106ls", "ts01_ls6"); setVal("tls06", "tlz_ls6"); setVal("tkonls6", "tkon_ls6"); setVal("enablels6", "enable_ls6", "check");
    setVal("ts0109ls", "ts01_ls9"); setVal("tls0109", "tlz_ls9"); setVal("tkonls9", "tkon_ls9"); setVal("enablels9", "enable_ls9", "check");
  }
}
window.applyDefaultsToFragment = applyDefaultsToFragment;
