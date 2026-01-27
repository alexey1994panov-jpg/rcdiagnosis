// static/tests.js

// Универсальная обёртка над fetch, кидает ошибку только по HTTP-статусу
async function fetchJson(url, options) {
  const resp = await fetch(url, options);
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`);
  }
  return await resp.json();
}

// Заполнить список тестов
async function renderTestsList() {
  try {
    const tests = await fetchJson("/tests");
    const sel = document.getElementById("testsselect");
    const info = document.getElementById("testinfo");
    if (!sel) return;

    sel.innerHTML = "";
    tests.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.id;
      const status =
        t.lastStatus === "ok" ? "✓" :
        t.lastStatus === "fail" ? "✗" : "?";
      opt.textContent = `${status} ${t.name}`;
      sel.appendChild(opt);
    });

    if (info) {
      info.textContent = "";
    }
  } catch (e) {
    console.error("renderTestsList error", e);
    alert("Не удалось загрузить список тестов");
  }
}
window.renderTestsList = renderTestsList;

// Загрузить выбранный тест в сценарий
async function loadSelectedTest() {
  const sel = document.getElementById("testsselect");
  if (!sel || !sel.value) {
    alert("Выберите тест");
    return;
  }

  try {
    const data = await fetchJson(`/tests/${encodeURIComponent(sel.value)}`);

    if (data.json) {
      window.scenario = data.json;
    } else if (data.scenario) {
      window.scenario = data.scenario;
    } else {
      window.scenario = data;
    }

    // Таблица сценария
    if (typeof rebuildScenarioTableFromScenario === "function") {
      try {
        rebuildScenarioTableFromScenario();
      } catch (e) {
        console.error("rebuildScenarioTableFromScenario error", e);
      }
    }

    // Опции в форму
    if (typeof fillOptionsFormFromScenario === "function") {
      fillOptionsFormFromScenario();
    }

    // JSON textarea
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

// Сохранить текущий сценарий как тест
async function saveCurrentAsTest() {
  try {
    const name = prompt("Имя теста:");
    if (!name) return;

    if (typeof updateOptionsFromForm === "function") {
      updateOptionsFromForm();
    }

    const testData = {
      name,
      scenario: window.scenario,
      lastStatus: "unknown",
      comment: "",
    };

    const result = await fetchJson("/tests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(testData),
    });

    await renderTestsList();

    const info = document.getElementById("testinfo");
    if (info) {
      info.textContent = `Сохранён тест ${name} (id=${result.id})`;
    }
  } catch (e) {
    console.error("saveCurrentAsTest error", e);
    alert("Не удалось сохранить тест");
  }
}
window.saveCurrentAsTest = saveCurrentAsTest;

// Отметить статус OK/FAIL с комментарием (опционально)
async function markTestStatus(status) {
  const sel = document.getElementById("testsselect");
  if (!sel || !sel.value) {
    alert("Выберите тест");
    return;
  }

  let comment = "";
  if (status === "fail") {
    comment = prompt("Комментарий к FAIL (опционально):") || "";
  }

  try {
    await fetchJson(`/tests/${encodeURIComponent(sel.value)}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, comment }),
    });

    await renderTestsList();

    const info = document.getElementById("testinfo");
    if (info) {
      info.textContent = `Статус обновлён: ${status}${comment ? " | " + comment : ""}`;
    }
  } catch (e) {
    console.error("markTestStatus error", e);
    alert("Не удалось обновить статус теста");
  }
}
window.markTestStatus = markTestStatus;

// Удалить тест
async function deleteSelectedTest() {
  const sel = document.getElementById("testsselect");
  if (!sel || !sel.value) {
    alert("Выберите тест");
    return;
  }
  if (!confirm("Удалить выбранный тест?")) {
    return;
  }

  try {
    await fetchJson(`/tests/${encodeURIComponent(sel.value)}`, {
      method: "DELETE",
    });

    await renderTestsList();

    const info = document.getElementById("testinfo");
    if (info) {
      info.textContent = "";
    }
  } catch (e) {
    console.error("deleteSelectedTest error", e);
    alert("Не удалось удалить тест");
  }
}
window.deleteSelectedTest = deleteSelectedTest;
