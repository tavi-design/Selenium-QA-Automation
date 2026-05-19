const express = require("express");
const session = require("express-session");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(
  session({
    secret: "selenium-qa-secret",
    resave: false,
    saveUninitialized: false,
    cookie: { maxAge: 3_600_000 },
  })
);
app.use(express.static(path.join(__dirname, "public")));

// ── In-memory stores ──────────────────────────────────────────────────────────

const USERS = {
  admin: { password: "admin123", name: "Admin User", email: "admin@taskmanager.dev", role: "Admin" },
  testuser: { password: "user123", name: "Test User", email: "tester@taskmanager.dev", role: "QA" },
};

const PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const STATUSES = ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"];
const CATEGORIES = ["Bug", "Feature", "Documentation", "Testing", "DevOps"];

function makeTask(id, title, priority, status, category, dueOffset, assignee, description = "") {
  const due = new Date();
  due.setDate(due.getDate() + dueOffset);
  return {
    id,
    title,
    description: description || `Details for task: ${title}`,
    priority,
    status,
    category,
    assignee,
    dueDate: due.toISOString().split("T")[0],
    createdAt: new Date().toISOString(),
  };
}

let tasks = [
  makeTask(1,  "Fix login redirect bug",           "CRITICAL", "IN_PROGRESS", "Bug",           2,  "admin",    "After login the redirect goes to /home instead of /dashboard"),
  makeTask(2,  "Write smoke tests for auth flow",  "HIGH",     "TODO",        "Testing",        3,  "testuser"),
  makeTask(3,  "Update API documentation",         "MEDIUM",   "TODO",        "Documentation",  7,  "testuser"),
  makeTask(4,  "Containerise CI pipeline",         "HIGH",     "DONE",        "DevOps",        -2,  "admin"),
  makeTask(5,  "Add pagination to task list",      "MEDIUM",   "DONE",        "Feature",       -5,  "admin"),
  makeTask(6,  "Accessibility audit – dashboard",  "LOW",      "TODO",        "Testing",       14,  "testuser"),
  makeTask(7,  "Upgrade Node to v22",              "LOW",      "BLOCKED",     "DevOps",         1,  "admin"),
  makeTask(8,  "Regression suite for task CRUD",   "HIGH",     "IN_PROGRESS", "Testing",        5,  "testuser"),
  makeTask(9,  "Fix date picker on Safari",        "MEDIUM",   "TODO",        "Bug",            4,  "testuser"),
  makeTask(10, "Implement task search endpoint",   "HIGH",     "DONE",        "Feature",       -3,  "admin"),
  makeTask(11, "Performance test – task list",     "MEDIUM",   "TODO",        "Testing",       10,  "testuser"),
  makeTask(12, "Set up Allure reporting",          "HIGH",     "TODO",        "DevOps",         6,  "testuser"),
  makeTask(13, "Cross-browser matrix",             "MEDIUM",   "TODO",        "Testing",        8,  "testuser"),
  makeTask(14, "Seed DB with realistic test data", "LOW",      "DONE",        "Testing",       -7,  "admin"),
  makeTask(15, "Add CSRF protection",              "CRITICAL", "TODO",        "Bug",            1,  "admin"),
  makeTask(16, "Write POM for login page",         "HIGH",     "IN_PROGRESS", "Testing",        2,  "testuser"),
  makeTask(17, "E2E journey: new user onboarding", "HIGH",     "TODO",        "Testing",        9,  "testuser"),
  makeTask(18, "Fix 500 on empty search query",   "CRITICAL", "DONE",        "Bug",           -1,  "admin"),
  makeTask(19, "Document test naming conventions","LOW",      "TODO",        "Documentation",  20,  "testuser"),
  makeTask(20, "Integrate Slack alerts for CI",   "MEDIUM",   "BLOCKED",     "DevOps",         3,  "admin"),
  makeTask(21, "Load test login endpoint",        "MEDIUM",   "TODO",        "Testing",       12,  "testuser"),
  makeTask(22, "Review PR: filter component",     "LOW",      "DONE",        "Feature",       -4,  "admin"),
  makeTask(23, "Add category filter to UI",       "MEDIUM",   "IN_PROGRESS", "Feature",        4,  "admin"),
  makeTask(24, "Fix XSS in task title render",    "CRITICAL", "TODO",        "Bug",            0,  "admin"),
  makeTask(25, "Parametrise API tests",           "HIGH",     "TODO",        "Testing",        7,  "testuser"),
  makeTask(26, "Dark mode toggle",                "LOW",      "TODO",        "Feature",       30,  "admin"),
  makeTask(27, "Profile page – edit email",       "MEDIUM",   "TODO",        "Feature",       15,  "testuser"),
  makeTask(28, "Negative tests: form validation", "HIGH",     "TODO",        "Testing",        3,  "testuser"),
  makeTask(29, "Retire legacy v1 API",            "MEDIUM",   "BLOCKED",     "DevOps",        -2,  "admin"),
  makeTask(30, "Write CONTRIBUTING guide",        "LOW",      "DONE",        "Documentation", -10, "admin"),
];

let nextId = tasks.length + 1;

// ── Auth helpers ──────────────────────────────────────────────────────────────

function requireAuth(req, res, next) {
  if (!req.session.user) return res.status(401).json({ error: "Unauthorized" });
  next();
}

// ── Auth routes ───────────────────────────────────────────────────────────────

app.post("/api/auth/login", (req, res) => {
  const { username, password } = req.body;
  const user = USERS[username];
  if (!user || user.password !== password) {
    return res.status(401).json({ error: "Invalid username or password" });
  }
  req.session.user = { username, name: user.name, email: user.email, role: user.role };
  res.json({ message: "Login successful", user: req.session.user });
});

app.post("/api/auth/logout", (req, res) => {
  req.session.destroy(() => res.json({ message: "Logged out" }));
});

app.get("/api/auth/me", requireAuth, (req, res) => {
  res.json(req.session.user);
});

// ── Task routes ───────────────────────────────────────────────────────────────

app.get("/api/tasks", requireAuth, (req, res) => {
  const { search = "", priority = "", status = "", category = "", page = "1" } = req.query;
  const perPage = 10;

  let filtered = tasks.filter((t) => {
    const matchSearch =
      !search ||
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase());
    const matchPriority = !priority || t.priority === priority;
    const matchStatus   = !status   || t.status   === status;
    const matchCategory = !category || t.category === category;
    return matchSearch && matchPriority && matchStatus && matchCategory;
  });

  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / perPage));
  const currentPage = Math.min(Math.max(1, parseInt(page, 10)), totalPages);
  const data = filtered.slice((currentPage - 1) * perPage, currentPage * perPage);

  res.json({ data, total, page: currentPage, totalPages, perPage });
});

app.post("/api/tasks", requireAuth, (req, res) => {
  const { title, description = "", priority, status, category, assignee, dueDate } = req.body;
  if (!title?.trim())    return res.status(400).json({ error: "Title is required" });
  if (!PRIORITIES.includes(priority)) return res.status(400).json({ error: "Invalid priority" });
  if (!STATUSES.includes(status))     return res.status(400).json({ error: "Invalid status" });
  if (!CATEGORIES.includes(category)) return res.status(400).json({ error: "Invalid category" });

  const task = {
    id: nextId++,
    title: title.trim(),
    description: description.trim(),
    priority,
    status,
    category,
    assignee: assignee || req.session.user.username,
    dueDate: dueDate || null,
    createdAt: new Date().toISOString(),
  };
  tasks.push(task);
  res.status(201).json(task);
});

app.get("/api/tasks/:id", requireAuth, (req, res) => {
  const task = tasks.find((t) => t.id === Number(req.params.id));
  if (!task) return res.status(404).json({ error: "Task not found" });
  res.json(task);
});

app.put("/api/tasks/:id", requireAuth, (req, res) => {
  const idx = tasks.findIndex((t) => t.id === Number(req.params.id));
  if (idx === -1) return res.status(404).json({ error: "Task not found" });
  const { title, description, priority, status, category, assignee, dueDate } = req.body;
  if (title !== undefined && !title.trim()) return res.status(400).json({ error: "Title cannot be empty" });
  if (priority  && !PRIORITIES.includes(priority))  return res.status(400).json({ error: "Invalid priority" });
  if (status    && !STATUSES.includes(status))       return res.status(400).json({ error: "Invalid status" });
  if (category  && !CATEGORIES.includes(category))  return res.status(400).json({ error: "Invalid category" });
  tasks[idx] = { ...tasks[idx], title: title?.trim() ?? tasks[idx].title, description, priority, status, category, assignee, dueDate };
  res.json(tasks[idx]);
});

app.delete("/api/tasks/:id", requireAuth, (req, res) => {
  const before = tasks.length;
  tasks = tasks.filter((t) => t.id !== Number(req.params.id));
  if (tasks.length === before) return res.status(404).json({ error: "Task not found" });
  res.status(204).end();
});

// ── Stats route ───────────────────────────────────────────────────────────────

app.get("/api/stats", requireAuth, (req, res) => {
  const today = new Date().toISOString().split("T")[0];
  res.json({
    total:       tasks.length,
    todo:        tasks.filter((t) => t.status === "TODO").length,
    inProgress:  tasks.filter((t) => t.status === "IN_PROGRESS").length,
    done:        tasks.filter((t) => t.status === "DONE").length,
    blocked:     tasks.filter((t) => t.status === "BLOCKED").length,
    overdue:     tasks.filter((t) => t.dueDate && t.dueDate < today && t.status !== "DONE").length,
    critical:    tasks.filter((t) => t.priority === "CRITICAL" && t.status !== "DONE").length,
  });
});

// ── Profile route ─────────────────────────────────────────────────────────────

app.put("/api/profile", requireAuth, (req, res) => {
  const { name, email } = req.body;
  if (!name?.trim())  return res.status(400).json({ error: "Name is required" });
  if (!email?.trim()) return res.status(400).json({ error: "Email is required" });
  req.session.user.name  = name.trim();
  req.session.user.email = email.trim();
  USERS[req.session.user.username].name  = name.trim();
  USERS[req.session.user.username].email = email.trim();
  res.json(req.session.user);
});

// ── Catch-all: serve index for direct page nav ────────────────────────────────

app.get("*", (_req, res) => res.sendFile(path.join(__dirname, "public", "index.html")));

app.listen(PORT, () => console.log(`Webapp listening on http://localhost:${PORT}`));
