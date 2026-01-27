// static/tabs.js

// Инициализация табов
function initTabs() {
  const buttons = document.querySelectorAll(".tab-button");
  const contents = document.querySelectorAll(".tab-content");

  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const tabId = btn.getAttribute("data-tab");
      // Переключаем активный таб
      buttons.forEach((b) => b.classList.remove("active"));
      contents.forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      const targetContent = document.getElementById(tabId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
      // Ленивая загрузка фрагмента
      await loadTabFragment(tabId);
    });
  });

  // При старте подгружаем первый активный таб
  const activeBtn = document.querySelector(".tab-button.active");
  if (activeBtn) {
    const firstTabId = activeBtn.getAttribute("data-tab");
    loadTabFragment(firstTabId);
  }
}
window.initTabs = initTabs;

// Карта табов и HTML-фрагментов
const fragmentMap = {
    "tab-lz-exc": "static/fragments/lz_all_exc.html",
    "tab-ls-exc": "static/fragments/ls_all_exc.html",
  //"tab-scenario" — статичный, без фрагмента
};

// Ленивая загрузка HTML-фрагмента для таба
async function loadTabFragment(tabId) {
  if (!window.loadedFragments) {
    window.loadedFragments = {};
  }
  if (window.loadedFragments[tabId]) {
    return;
  }

  const url = fragmentMap[tabId];
  if (!url) {
    // tab-scenario и прочие без HTML-фрагмента
    return;
  }

  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      console.error("Failed to load fragment", url, resp.status);
      const container = document.getElementById(tabId);
      if (container) {
        container.innerHTML =
          `<p style="color:red;">Ошибка загрузки фрагмента (${resp.status})</p>`;
      }
      return;
    }

    const html = await resp.text();
    const container = document.getElementById(tabId);
    if (container) {
      container.innerHTML = html;
    }

    window.loadedFragments[tabId] = true;

    // После первой загрузки фрагмента подставляем значения по умолчанию
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

// Подстановка дефолтов с бэка в поля фрагмента
function applyDefaultsToFragment(tabId) {
  const data = (window.scenario && window.scenario.options) || {};
  if (!data) return;

  function setVal(id, key, type = "number") {
    const el = document.getElementById(id);
    if (!el || !(key in data)) return;
    if (type === "checkbox") {
      el.checked = Boolean(data[key]);
    } else if (type === "select") {
      el.value = String(data[key]);
    } else {
      el.value = String(data[key]);
    }
  }
  console.log("applyDefaultsToFragment", tabId, "data =", data);
  // ЛЗ v1–v3
  if (tabId === "tab-lz-exc") {
    // v1
    setVal("ts0101", "t_s0101");
    setVal("tlz01", "t_lz01");
    setVal("tkonv1", "t_kon_v1");
    setVal("tpausev1", "t_pause_v1");
    setVal("enablev1", "enable_v1", "checkbox");
    // v2
    setVal("ts0102", "t_s0102");
    setVal("ts0202", "t_s0202");
    setVal("tlz02", "t_lz02");
    setVal("tkonv2", "t_kon_v2");
    setVal("tpausev2", "t_pause_v2");
    setVal("enablev2", "enable_v2", "checkbox");
    // v3
    setVal("ts0103", "t_s0103");
    setVal("ts0203", "t_s0203");
    setVal("tlz03", "t_lz03");
    setVal("tkonv3", "t_kon_v3");
    setVal("tpausev3", "t_pause_v3");
    setVal("enablev3", "enable_v3", "checkbox");
    // v4
    setVal("ts0401", "t_s0401");
    setVal("tlz04", "t_lz04");
    setVal("tkonv4", "t_kon_v4");
    setVal("tpausev4", "t_pause_v4");
    setVal("enablev4", "enable_v4", "checkbox");
    // v5
    setVal("ts05", "t_s05");
    setVal("tlz05", "t_lz05");
    setVal("tpk", "t_pk");
    setVal("tkonv5", "t_kon_v5");
    setVal("tpausev5", "t_pause_v5");
    setVal("enablev5", "enable_v5", "checkbox");
    // v6
    setVal("ts06", "t_s06");
    setVal("tlz06", "t_lz06");
    setVal("tkonv6", "t_kon_v6");
    setVal("tpausev6", "t_pause_v6");
    setVal("enablev6", "enable_v6", "checkbox");
    // v7
    setVal("ts07", "t_s07");
    setVal("tlz07", "t_lz07");
    setVal("tkonv7", "t_kon_v7");
    setVal("tpausev7", "t_pause_v7");
    setVal("enablev7", "enable_v7", "checkbox");
    // v8
    setVal("ts0108", "t_s0108");
    setVal("ts0208", "t_s0208");
    setVal("tlz08", "t_lz08");
    setVal("tkonv8", "t_kon_v8");
    setVal("tpausev8", "t_pause_v8");
    setVal("enablev8", "enable_v8", "checkbox");
    // v9
    setVal("ts0109", "t_s0109");
    setVal("tlz09", "t_lz09");
    setVal("tkonv9", "t_kon_v9");
    setVal("tpausev9", "t_pause_v9");
    setVal("enablev9", "enable_v9", "checkbox");
    // v10
    setVal("ts0110", "t_s0110");
    setVal("ts0210", "t_s0210");
    setVal("ts0310", "t_s0310");
    setVal("tlz10", "t_lz10");
    setVal("tkonv10", "t_kon_v10");
    setVal("tpausev10", "t_pause_v10");
    setVal("enablev10", "enable_v10", "checkbox");
    // v11
    setVal("ts11", "t_s11");
    setVal("tlz11", "t_lz11");
    setVal("tkonv11", "t_kon_v11");
    setVal("tpausev11", "t_pause_v11");
    setVal("enablev11", "enable_v11", "checkbox");
    // v12
    setVal("ts0112", "t_s0112");
    setVal("ts0212", "t_s0212");
    setVal("tlz12", "t_lz12");
    setVal("tkonv12", "t_kon_v12");
    setVal("tpausev12", "t_pause_v12");
    setVal("enablev12", "enable_v12", "checkbox");
    // v13
    setVal("ts0113", "t_s0113");
    setVal("ts0213", "t_s0213");
    setVal("tlz13", "t_lz13");
    setVal("tkonv13", "t_kon_v13");
    setVal("tpausev13", "t_pause_v13");
    setVal("enablev13", "enable_v13", "checkbox");
    setVal("v13ctrlrcid", "v13_ctrl_rc_id", "select");
    // Исключения ЛЗ
    setVal("tmu", "t_mu");
    setVal("trecentls", "t_recent_ls");
    setVal("tminmaneuverv8", "t_min_maneuver_v8");
    setVal("enablelzexcmu", "enable_lz_exc_mu", "checkbox");
    setVal("enablelzexcrecentls", "enable_lz_exc_recent_ls", "checkbox");
    setVal("enablelzexcdsp", "enable_lz_exc_dsp", "checkbox");
  } else if (tabId === "tab-ls-exc") {
    // LS v1
    setVal("tc0101ls", "t_c0101_ls");
    setVal("tls01", "t_ls01");
    setVal("tkonls1", "t_kon_ls1");
    setVal("tpausels1", "t_pause_ls1");
    setVal("enablels1", "enable_ls1", "checkbox");
    // LS v2
    setVal("ts0102ls", "t_s0102_ls");
    setVal("ts0202ls", "t_s0202_ls");
    setVal("tls0102", "t_ls0102");
    setVal("tls0202", "t_ls0202");
    setVal("tkonls2", "t_kon_ls2");
    setVal("tpausels2", "t_pause_ls2");
    setVal("enablels2", "enable_ls2", "checkbox");
    // LS v4
    setVal("ts0104ls", "t_s0104_ls");
    setVal("ts0204ls", "t_s0204_ls");
    setVal("tls0104", "t_ls0104");
    setVal("tls0204", "t_ls0204");
    setVal("tkonls4", "t_kon_ls4");
    setVal("tpausels4", "t_pause_ls4");
    setVal("enablels4", "enable_ls4", "checkbox");
    // LS v5
    setVal("ts0105ls", "t_s0105_ls");
    setVal("tls05", "t_ls05");
    setVal("tkonls5", "t_kon_ls5");
    setVal("tpausels5", "t_pause_ls5");
    setVal("enablels5", "enable_ls5", "checkbox");
    // LS v6
    setVal("ts0106ls", "t_s0106_ls");
    setVal("tls06", "t_ls06");
    setVal("tkonls6", "t_kon_ls6");
    setVal("tpausels6", "t_pause_ls6");
    setVal("enablels6", "enable_ls6", "checkbox");
    // LS v9
    setVal("ts0109ls", "t_s0109_ls");
    setVal("ts0209ls", "t_s0209_ls");
    setVal("tls0109", "t_ls0109");
    setVal("tls0209", "t_ls0209");
    setVal("tkonls9", "t_kon_ls9");
    setVal("tpausels9", "t_pause_ls9");
    setVal("enablels9", "enable_ls9", "checkbox");
    // Исключения ЛС
    setVal("tlsmu", "t_ls_mu");
    setVal("tlsafterlz", "t_ls_after_lz");
    setVal("tlsdsp", "t_ls_dsp");
    setVal("enablelsexcmu", "enable_ls_exc_mu", "checkbox");
    setVal("enablelsexcafterlz", "enable_ls_exc_after_lz", "checkbox");
    setVal("enablelsexcdsp", "enable_ls_exc_dsp", "checkbox");
  }
}
window.applyDefaultsToFragment = applyDefaultsToFragment;

// Загрузка дефолтов с бэка
async function loadDefaults() {
  try {
    const resp = await fetch("/defaults");
    if (!resp.ok) {
      console.error("Failed to load defaults, status", resp.status);
      return;
    }
    const data = await resp.json();

    if (!window.scenario) window.scenario = {};
    window.scenario.options = data || {};
    console.log("defaults from backend =", data);
    console.log("scenario.options after defaults =", window.scenario.options);
    Object.keys(window.loadedFragments || {}).forEach((tabId) => {
      applyDefaultsToFragment(tabId);
    });
  } catch (e) {
    console.error("Failed to load defaults", e);
  }
}
window.loadDefaults = loadDefaults;