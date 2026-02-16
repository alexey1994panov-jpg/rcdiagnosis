async function loadExceptionsConfig() {
  const status = document.getElementById("exceptions-config-status");
  const area = document.getElementById("exceptionsconfigtext");
  if (!area) return;
  try {
    if (status) status.textContent = "Загрузка...";
    const resp = await fetch("/exceptions-config");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    area.value = JSON.stringify(data, null, 2);
    if (status) status.textContent = "OK";
  } catch (e) {
    if (status) status.textContent = `Ошибка: ${e.message}`;
  }
}

async function saveExceptionsConfig() {
  const status = document.getElementById("exceptions-config-status");
  const area = document.getElementById("exceptionsconfigtext");
  if (!area) return;
  try {
    if (status) status.textContent = "Сохранение...";
    const payload = JSON.parse(area.value || "{}");
    const resp = await fetch("/exceptions-config", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const msg = await resp.text().catch(() => "");
      throw new Error(`HTTP ${resp.status} ${msg}`);
    }
    if (status) status.textContent = "Сохранено";
  } catch (e) {
    if (status) status.textContent = `Ошибка: ${e.message}`;
  }
}

window.loadExceptionsConfig = loadExceptionsConfig;
window.saveExceptionsConfig = saveExceptionsConfig;
