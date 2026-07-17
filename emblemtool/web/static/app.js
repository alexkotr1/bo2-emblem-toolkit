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

    list.appendChild(node);
  }
}

document.getElementById("refreshBtn").addEventListener("click", refreshAll);

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
refreshAll();
setInterval(refreshAll, 5000);
