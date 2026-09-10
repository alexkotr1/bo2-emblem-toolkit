// BO2 Emblem Toolkit - control panel frontend.
// Plain JS, no build step, no dependencies - keeps the tool easy to run
// for non-technical users.

const modeHints = {
  off: "The proxy is transparent. Nothing is captured or changed.",
  capture: "Open a player's profile or channel on your PS5 - their emblem is saved below automatically.",
  inject: "Open your own emblem editor on the PS5. The selected emblem below loads there, ready to save.",
};

let currentStatus = null;
let currentEmblems = [];

async function getJSON(url) {
  const r = await fetch(url);
  return r.json();
}
async function postJSON(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return r.json();
}

// ---------- network info ----------

async function loadNetworkInfo() {
  const info = await getJSON("/api/network-info");
  const el = document.getElementById("setupValue");
  el.textContent = info.lan_ip
    ? `${info.lan_ip} : ${info.proxy_port}`
    : "couldn't detect - see docs/INSTALL.md";
}

// ---------- mode ----------

function renderMode() {
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === currentStatus.mode);
  });
  document.getElementById("modeHint").textContent = modeHints[currentStatus.mode] || "";
}

async function setMode(mode) {
  await postJSON("/api/mode", { mode });
  await refreshStatus();
}

document.querySelectorAll(".mode-btn").forEach((btn) => {
  btn.addEventListener("click", () => setMode(btn.dataset.mode));
});

// ---------- emblem list (flat, single-select) ----------

function fmtDate(s) {
  if (!s) return "";
  return s.replace(" ", " · ").slice(0, 16);
}

function isSelected(e) {
  const sel = currentStatus.selected;
  return sel && sel.group === e.group && sel.slot === e.slot;
}

function renderEmblems() {
  const list = document.getElementById("emblemList");
  const empty = document.getElementById("emblemsEmpty");
  list.innerHTML = "";
  empty.style.display = currentEmblems.length ? "none" : "";
  document.getElementById("deleteAllBtn").hidden = !currentEmblems.length;

  const tpl = document.getElementById("emblemCardTpl");
  for (const e of currentEmblems) {
    const node = tpl.content.cloneNode(true);
    const card = node.querySelector(".emblem-card");
    card.classList.toggle("selected", isSelected(e));

    node.querySelector(".emblem-thumb").src = `/api/render/${encodeURIComponent(e.group)}/${e.slot}.png`;
    node.querySelector(".emblem-date").textContent = fmtDate(e.captured_at);

    const labelInput = node.querySelector(".emblem-label-input");
    labelInput.value = e.label || `Emblem from ${fmtDate(e.captured_at)}`;
    labelInput.addEventListener("click", (evt) => evt.stopPropagation());
    labelInput.addEventListener("change", async () => {
      await postJSON(`/api/emblems/${encodeURIComponent(e.group)}/${e.slot}/label`, { label: labelInput.value });
    });

    card.addEventListener("click", async () => {
      await postJSON("/api/select", { group: e.group, slot: e.slot });
      await refreshStatus();
    });

    node.querySelector(".emblem-delete").addEventListener("click", async (evt) => {
      evt.stopPropagation(); // don't also select the card
      if (!confirm("Delete this emblem? This can't be undone.")) return;
      const r = await postJSON("/api/delete", { group: e.group, slot: e.slot });
      if (!r.ok) alert(r.error || "Couldn't delete that emblem.");
      await refreshAll();
    });

    list.appendChild(node);
  }
}

document.getElementById("refreshBtn").addEventListener("click", refreshAll);

document.getElementById("deleteAllBtn").addEventListener("click", async () => {
  const n = currentEmblems.length;
  if (!n || !confirm(`Delete all ${n} captured emblem${n === 1 ? "" : "s"}? This can't be undone.`)) return;
  const r = await postJSON("/api/delete-all");
  if (!r.ok) alert(r.error || "Couldn't delete everything.");
  await refreshAll();
});

// ---------- debug log ----------

let debugOn = false;

async function loadDebug() {
  const d = await getJSON("/api/debug");
  debugOn = d.enabled;
  document.getElementById("debugToggle").checked = d.enabled;
  document.getElementById("debugStatus").textContent = d.enabled
    ? `On. Saving to ${d.log_file}`
    : d.log_file ? `Off. Most recent log: ${d.log_file}` : `Off. Logs are saved in ${d.log_dir}`;
}

document.getElementById("debugToggle").addEventListener("change", async (evt) => {
  const r = await postJSON("/api/debug", { enabled: evt.target.checked });
  if (!r.ok) alert(r.error || "Couldn't change the debug log setting.");
  await loadDebug();
});

document.getElementById("openLogsBtn").addEventListener("click", async () => {
  const r = await postJSON("/api/debug/open-folder");
  if (!r.ok) alert(r.error || "Couldn't open the logs folder.");
});

// Errors in this page itself (a script error, a request that failed) go into
// the debug log too, so a "the panel is broken" report comes with the reason.
function reportPanelError(message, detail) {
  if (!debugOn) return;
  fetch("/api/debug/client-error", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: String(message), detail: String(detail || "") }),
  }).catch(() => {}); // the toolkit itself may be what's down
}
window.addEventListener("error", (e) => reportPanelError(e.message, `${e.filename}:${e.lineno}:${e.colno} ${e.error?.stack || ""}`));
window.addEventListener("unhandledrejection", (e) => reportPanelError(e.reason?.message || e.reason, e.reason?.stack));

// ---------- refresh loop ----------

async function refreshStatus() {
  currentStatus = await getJSON("/api/status");
  renderMode();
  if (currentEmblems.length) renderEmblems();
}

async function refreshAll() {
  [currentStatus, currentEmblems] = await Promise.all([
    getJSON("/api/status"),
    getJSON("/api/emblems"),
  ]);
  renderMode();
  renderEmblems();
}

loadNetworkInfo();
loadDebug();
refreshAll();
setInterval(refreshAll, 5000);
