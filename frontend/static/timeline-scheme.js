// static/timeline-scheme.js

function updateTrackScheme(row) {
  if (!row) return;

  // SVG‑лейблы номеров стрелок (индикаторы на схеме)
  const sw10LabelSvg = document.getElementById("sw10-label");
  const sw1LabelSvg  = document.getElementById("sw1-label");
  const sw5LabelSvg  = document.getElementById("sw5-label");

  // SVG‑линии РЦ
  const rcPrevLine = document.getElementById("rc-10-12");
  const rcCurrLine = document.getElementById("rc-1p");
  const rcNextLine = document.getElementById("rc-1-7");

  // Подписи состояний РЦ/стрелок под схемой
  const rcPrevEl = document.getElementById("rcprevstatelbl");
  const rc1pEl   = document.getElementById("rccurrstatelbl");
  const rcNextEl = document.getElementById("rcnextstatelbl");

  const sw10El = document.getElementById("sw10statelbl");
  const sw1El  = document.getElementById("sw1statelbl");
  const sw5El  = document.getElementById("sw5statelbl");

  // SVG‑светофоры
  const sigChm1El = document.getElementById("sig-chm1");
  const sigNm1El  = document.getElementById("sig-nm1");
  const sigCh1El  = document.getElementById("sig-ch1");
  const sigM1El   = document.getElementById("sig-m1");

  const rcStates  = row.rc_states     || row.rcstates     || {};
  const swStates  = row.switch_states || row.switchstates || {};
  const sigStates = row.signal_states || row.signalstates || {};

  const rcPrevState = rcStates["10-12SP"] ?? 0;
  const rcCurrState = rcStates["1P"]      ?? 0;
  const rcNextState = rcStates["1-7SP"]   ?? 0;

  const sw10State = swStates["Sw10"] ?? 0;
  const sw1State  = swStates["Sw1"]  ?? 0;
  const sw5State  = swStates["Sw5"]  ?? 0;

  const chm1State = sigStates["ЧМ1"] ?? 0;
  const nm1State  = sigStates["НМ1"] ?? 0;
  const ch1State  = sigStates["Ч1"]  ?? 0;
  const m1State   = sigStates["М1"]  ?? 0;

  const applyRcStateClass = window.applyRcStateClass;
  const swClassForValue   = window.swClassForValue;

  // --- подсветка линий РЦ на SVG по состоянию ---
  highlightRcLine(rcPrevLine, rcPrevState);
  highlightRcLine(rcCurrLine, rcCurrState);
  highlightRcLine(rcNextLine, rcNextState);

  // --- подписи числом под схемой ---
  if (rcPrevEl) rcPrevEl.textContent = rcPrevState;
  if (rc1pEl)   rc1pEl.textContent   = rcCurrState;
  if (rcNextEl) rcNextEl.textContent = rcNextState;

  if (sw10El) sw10El.textContent = sw10State;
  if (sw1El)  sw1El.textContent  = sw1State;
  if (sw5El)  sw5El.textContent  = sw5State;

  // --- подсветка чисел РЦ под схемой (фон ячеек) ---
  if (applyRcStateClass) {
    applyRcStateClass(rcPrevEl, rcPrevState);
    applyRcStateClass(rc1pEl,   rcCurrState);
    applyRcStateClass(rcNextEl, rcNextState);
  }

  // --- подсветка стрелок: фон + цвет текста (под схемой и на схеме) ---
  if (swClassForValue) {
    if (sw10El) {
      sw10El.classList.remove("sw-state-plus", "sw-state-minus", "sw-state-nocontrol");
      sw10El.classList.add(swClassForValue(sw10State));
      decorateSwitchIndicator(sw10El,       sw10State);
    }
    if (sw1El) {
      sw1El.classList.remove("sw-state-plus", "sw-state-minus", "sw-state-nocontrol");
      sw1El.classList.add(swClassForValue(sw1State));
      decorateSwitchIndicator(sw1El,        sw1State);
    }
    if (sw5El) {
      sw5El.classList.remove("sw-state-plus", "sw-state-minus", "sw-state-nocontrol");
      sw5El.classList.add(swClassForValue(sw5State));
      decorateSwitchIndicator(sw5El,        sw5State);
    }

    // те же индикаторные цвета для SVG-надписей 10/1/5
    decorateSwitchIndicator(sw10LabelSvg, sw10State);
    decorateSwitchIndicator(sw1LabelSvg,  sw1State);
    decorateSwitchIndicator(sw5LabelSvg,  sw5State);
  }

  // --- SVG‑светофоры ---
  if (window.applySignalClass) {
    // Ч1, ЧМ1, НМ1 — поездные; М1 — маневровый
    if (sigChm1El) window.applySignalClass(sigChm1El, chm1State, 4);
    if (sigNm1El)  window.applySignalClass(sigNm1El,  nm1State,  4);
    if (sigCh1El)  window.applySignalClass(sigCh1El,  ch1State,  4);
    if (sigM1El)   window.applySignalClass(sigM1El,   m1State,   3);
  }

  // геометрию стрелок сейчас не трогаем
  // applySvgSwitch(...) закомментирован
}

function highlightRcLine(lineEl, stateValue) {
  if (!lineEl) return;

  lineEl.classList.remove(
    "rc-line-free",
    "rc-line-locked",
    "rc-line-occupied"
  );

  const v = Number(stateValue);

  const isFree = [3, 4, 5].includes(v);
  const isOcc  = [6, 7, 8].includes(v);
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
  el.classList.remove(
    "sw-indicator-plus",
    "sw-indicator-minus",
    "sw-indicator-unknown",
    "sw-indicator-lost"
  );

  const v = Number(state);

  if ([15, 16, 17, 18, 19, 20].includes(v)) {
    // потеряла контроль
    el.classList.add("sw-indicator-lost");
  } else if (v === 21) {
    // положение неизвестно
    el.classList.add("sw-indicator-unknown");
  } else if ([3, 4, 5, 6, 7, 8].includes(v)) {
    // плюс, имеет контроль
    el.classList.add("sw-indicator-plus");
  } else if ([9, 10, 11, 12, 13, 14].includes(v)) {
    // минус, имеет контроль
    el.classList.add("sw-indicator-minus");
  }
}

// applySvgSwitch оставлен на случай, если захочешь вернуть геометрию
function applySvgSwitch(swState, mainId, branchId, pkId) {
  const mainEl   = mainId   ? document.getElementById(mainId)   : null;
  const branchEl = branchId ? document.getElementById(branchId) : null;
  const pkEl     = pkId     ? document.getElementById(pkId)     : null;

  if (!branchEl || !pkEl) return;

  if (mainEl) {
    mainEl.classList.remove("rc-main-thick", "rc-main-thin");
  }
  branchEl.classList.remove("rc-branch-thick", "rc-branch-thin");

  const swClassForValue = window.swClassForValue;
  const swClass = swClassForValue ? swClassForValue(swState) : "";

  if (swClass === "sw-state-plus") {
    if (mainEl) mainEl.classList.add("rc-main-thick");
    branchEl.classList.add("rc-branch-thin");
    pkEl.style.opacity = "1";
  } else if (swClass === "sw-state-minus") {
    if (mainEl) mainEl.classList.add("rc-main-thin");
    branchEl.classList.add("rc-branch-thick");
    pkEl.style.opacity = "0.3";
  } else {
    if (mainEl) mainEl.classList.add("rc-main-thin");
    branchEl.classList.add("rc-branch-thin");
    pkEl.style.opacity = "0.3";
  }
}

// ES‑экспорт
export { updateTrackScheme };
window.updateTrackScheme = updateTrackScheme;
