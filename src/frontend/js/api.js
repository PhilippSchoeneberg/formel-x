// Small fetch wrapper for the FastAPI backend. Errors carry the HTTP status and the
// backend's `detail` code (e.g. "group_exists"), which the UI maps to translated messages.

export class ApiError extends Error {
  constructor(status, detail, retryAfter = null) {
    super(typeof detail === "string" ? detail : `HTTP ${status}`);
    this.status = status;
    this.detail = detail;
    this.retryAfter = retryAfter; // seconds, set for 429 responses
  }

  get isConnectionError() {
    return this.status === 0 || this.detail === "connection_error";
  }
}

async function request(method, path, body) {
  const options = { method, headers: {}, credentials: "same-origin" };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`api${path}`, options);
  } catch {
    throw new ApiError(0, "connection_error");
  }

  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const retryAfter = Number(response.headers.get("Retry-After")) || null;
    throw new ApiError(response.status, data?.detail, retryAfter);
  }
  return data;
}

function query(params) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") search.set(key, value);
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

export const api = {
  me: () => request("GET", "/auth/me"),
  login: (email, password) => request("POST", "/auth/login", { email, password }),
  register: (email, password) => request("POST", "/auth/register", { email, password }),
  logout: () => request("POST", "/auth/logout"),

  myGroups: () => request("GET", "/groups/mine"),
  groupByName: (name) => request("GET", `/groups/by-name${query({ name })}`),
  lookupGroups: (ids) => request("POST", "/groups/lookup", { ids }),
  createGroup: (name) => request("POST", "/groups", { name }),
  updateGroup: (id, name) => request("PATCH", `/groups/${id}`, { name }),
  deleteGroup: (id) => request("DELETE", `/groups/${id}`),

  elements: () => request("GET", "/elements"),
  groupElements: (groupId) => request("GET", `/groups/${groupId}/elements`),
  addElement: (groupId, symbol) => request("PUT", `/groups/${groupId}/elements/${encodeURIComponent(symbol)}`),
  removeElement: (groupId, symbol) => request("DELETE", `/groups/${groupId}/elements/${encodeURIComponent(symbol)}`),

  categories: (groupId, type) => request("GET", `/groups/${groupId}/categories${query({ type })}`),
  createCategory: (groupId, name, type) => request("POST", `/groups/${groupId}/categories`, { name, type }),
  updateCategory: (id, name) => request("PATCH", `/categories/${id}`, { name }),
  deleteCategory: (id) => request("DELETE", `/categories/${id}`),

  // kind is "compounds" or "questions"
  entries: (kind, groupId, filters = {}) => request("GET", `/groups/${groupId}/${kind}${query(filters)}`),
  createEntry: (kind, groupId, data) => request("POST", `/groups/${groupId}/${kind}`, data),
  updateEntry: (kind, id, data) => request("PATCH", `/${kind}/${id}`, data),
  deleteEntry: (kind, id) => request("DELETE", `/${kind}/${id}`),
};
