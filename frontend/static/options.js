// static/options.js
// Чтение параметров ЛЗ/ЛС/исключений из HTML-форм и запись в scenario.options

// --- Основная функция: собрать все параметры из форм ---
function updateOptionsFromForm() {
  function getVal(id, defaultVal = 0) {
    const el = document.getElementById(id);
    if (!el) return defaultVal;
    const raw = el.value;
    if (raw === "" || raw == null) return defaultVal;
    const v = parseFloat(raw);
    return Number.isNaN(v) ? defaultVal : v;
  }

  function getCheck(id, defaultVal = false) {
    const el = document.getElementById(id);
    return el ? el.checked : defaultVal;
  }

  function getSelect(id, defaultVal = "") {
    const el = document.getElementById(id);
    return el ? el.value : defaultVal;
  }

  // Собираем все параметры
  scenario.options = {
    // ЛЗ v1
    t_s0101: getVal("ts0101"),
    t_lz01: getVal("tlz01"),
    t_kon_v1: getVal("tkonv1"),
    t_pause_v1: getVal("tpausev1"),
    enable_v1: getCheck("enablev1", true),

    // ЛЗ v2
    t_s0102: getVal("ts0102"),
    t_s0202: getVal("ts0202"),
    t_lz02: getVal("tlz02"),
    t_kon_v2: getVal("tkonv2"),
    t_pause_v2: getVal("tpausev2"),
    enable_v2: getCheck("enablev2", true),

    // ЛЗ v3
    t_s0103: getVal("ts0103"),
    t_s0203: getVal("ts0203"),
    t_lz03: getVal("tlz03"),
    t_kon_v3: getVal("tkonv3"),
    t_pause_v3: getVal("tpausev3"),
    enable_v3: getCheck("enablev3", true),

    // ЛЗ v4
    t_s0401: getVal("ts0401"),
    t_lz04: getVal("tlz04"),
    t_kon_v4: getVal("tkonv4"),
    t_pause_v4: getVal("tpausev4"),
    enable_v4: getCheck("enablev4", true),

    // ЛЗ v5
    t_s05: getVal("ts05"),
    t_lz05: getVal("tlz05"),
    t_pk: getVal("tpk"),
    t_kon_v5: getVal("tkonv5"),
    t_pause_v5: getVal("tpausev5"),
    enable_v5: getCheck("enablev5", false),

    // ЛЗ v6
    t_s06: getVal("ts06"),
    t_lz06: getVal("tlz06"),
    t_kon_v6: getVal("tkonv6"),
    t_pause_v6: getVal("tpausev6"),
    enable_v6: getCheck("enablev6", false),

    // ЛЗ v7
    t_s07: getVal("ts07"),
    t_lz07: getVal("tlz07"),
    t_kон_v7: getVal("tkonv7"),
    t_pause_v7: getVal("tpausev7"),
    enable_v7: getCheck("enablev7", false),

    // ЛЗ v8
    t_s0108: getVal("ts0108"),
    t_s0208: getVal("ts0208"),
    t_lz08: getVal("tlz08"),
    t_kon_v8: getVal("tkonv8"),
    t_pause_v8: getVal("tpausev8"),
    enable_v8: getCheck("enablev8", true),

    // ЛЗ v9
    t_s0109: getVal("ts0109"),
    t_lz09: getVal("tlz09"),
    t_kon_v9: getVal("tkonv9"),
    t_pause_v9: getVal("tpausev9"),
    enable_v9: getCheck("enablev9", true),

    // ЛЗ v10
    t_s0110: getVal("ts0110"),
    t_s0210: getVal("ts0210"),
    t_s0310: getVal("ts0310"),
    t_lz10: getVal("tlz10"),
    t_kon_v10: getVal("tkonv10"),
    t_pause_v10: getVal("tpausev10"),
    enable_v10: getCheck("enablev10", true),

    // ЛЗ v11
    t_s11: getVal("ts11"),
    t_lz11: getVal("tlz11"),
    t_kon_v11: getVal("tkonv11"),
    t_pause_v11: getVal("tpausev11"),
    enable_v11: getCheck("enablev11", true),

    // ЛЗ v12
    t_s0112: getVal("ts0112"),
    t_s0212: getVal("ts0212"),
    t_lz12: getVal("tlz12"),
    t_kon_v12: getVal("tkonv12"),
    t_pause_v12: getVal("tpausev12"),
    enable_v12: getCheck("enablev12", true),

    // ЛЗ v13
    t_s0113: getVal("ts0113"),
    t_s0213: getVal("ts0213"),
    t_lz13: getVal("tlz13"),
    t_kon_v13: getVal("tkonv13"),
    t_pause_v13: getVal("tpausev13"),
    enable_v13: getCheck("enablev13", true),
    // v13_ctrl_rc_id: getSelect("v13ctrlrcid", "10-12SP"),

    // ЛС v1
    t_c0101_ls: getVal("tc0101ls"),
    t_ls01: getVal("tls01"),
    t_kon_ls1: getVal("tkonls1"),
    t_pause_ls1: getVal("tpausels1"),
    enable_ls1: getCheck("enablels1", true),

    // ЛС v2
    t_s0102_ls: getVal("ts0102ls"),
    t_s0202_ls: getVal("ts0202ls"),
    t_ls0102: getVal("tls0102"),
    t_ls0202: getVal("tls0202"),
    t_kon_ls2: getVal("tkonls2"),
    t_pause_ls2: getVal("tpausels2"),
    enable_ls2: getCheck("enablels2", true),

    // ЛС v4
    t_s0104_ls: getVal("ts0104ls"),
    t_s0204_ls: getVal("ts0204ls"),
    t_ls0104: getVal("tls0104"),
    t_ls0204: getVal("tls0204"),
    t_kon_ls4: getVal("tkonls4"),
    t_pause_ls4: getVal("tpausels4"),
    enable_ls4: getCheck("enablels4", true),

    // ЛС v5
    t_s0105_ls: getVal("ts0105ls"),
    t_ls05: getVal("tls05"),
    t_kon_ls5: getVal("tkonls5"),
    t_pause_ls5: getVal("tpausels5"),
    enable_ls5: getCheck("enablels5", true),

    // ЛС v6
    t_s0106_ls: getVal("ts0106ls"),
    t_ls06: getVal("tls06"),
    t_kon_ls6: getVal("tkonls6"),
    t_pause_ls6: getVal("tpausels6"),
    enable_ls6: getCheck("enablels6", true),

    // ЛС v9
    t_s0109_ls: getVal("ts0109ls"),
    t_s0209_ls: getVal("ts0209ls"),
    t_ls0109: getVal("tls0109"),
    t_ls0209: getVal("tls0209"),
    t_kon_ls9: getVal("tkonls9"),
    t_pause_ls9: getVal("tpausels9"),
    enable_ls9: getCheck("enablels9", true),

    // Исключения ЛЗ
    t_mu: getVal("tmu"),
    t_recent_ls: getVal("trecentls"),
    t_min_maneuver_v8: getVal("tminmaneuverv8"),
    enable_lz_exc_mu: getCheck("enablelzexcmu", true),
    enable_lz_exc_recent_ls: getCheck("enablelzexcrecentls", true),
    enable_lz_exc_dsp: getCheck("enablelzexcdsp", true),

    // Исключения ЛС
    t_ls_mu: getVal("tlsmu"),
    t_ls_after_lz: getVal("tlsafterlz"),
    t_ls_dsp: getVal("tlsdsp"),
    enable_ls_exc_mu: getCheck("enablelsexcmu", true),
    enable_ls_exc_after_lz: getCheck("enablelsexcafterlz", true),
    enable_ls_exc_dsp: getCheck("enablelsexcdsp", true),
  };
}

window.updateOptionsFromForm = updateOptionsFromFor
