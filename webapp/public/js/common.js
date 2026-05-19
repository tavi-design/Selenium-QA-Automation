// Redirect to login if not authenticated (call on every protected page)
async function requireAuth() {
  try {
    const res = await fetch("/api/auth/me");
    if (!res.ok) { window.location.href = "/login.html"; return null; }
    return res.json();
  } catch {
    window.location.href = "/login.html";
    return null;
  }
}

async function logout() {
  await fetch("/api/auth/logout", { method: "POST" });
  window.location.href = "/login.html";
}

function priorityBadge(p) {
  const map = { LOW: "badge-low", MEDIUM: "badge-medium", HIGH: "badge-high", CRITICAL: "badge-critical" };
  return `<span class="badge ${map[p] || ""}">${p}</span>`;
}

function statusBadge(s) {
  const map = { TODO: "badge-todo", IN_PROGRESS: "badge-inprogress", DONE: "badge-done", BLOCKED: "badge-blocked" };
  return `<span class="badge ${map[s] || ""}">${s.replace("_", " ")}</span>`;
}
