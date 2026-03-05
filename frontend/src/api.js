const DEFAULT_BASE = "http://localhost:8000";

function normalizeBase(baseUrl) {
  return String(baseUrl || "").trim().replace(/\/+$/, "");
}

export function getApiBaseUrl() {
  const envValue = import.meta.env.VITE_API_BASE_URL;
  if (envValue && String(envValue).trim()) {
    return normalizeBase(envValue);
  }
  return DEFAULT_BASE;
}

export function buildApiUrl(path, query = {}) {
  if (!String(path).startsWith("/")) {
    throw new Error(`Path must start with '/': ${path}`);
  }

  const base = getApiBaseUrl();
  const url = new URL(`${base}${path}`);

  const params = new URLSearchParams();
  const keys = Object.keys(query);
  for (const key of keys) {
    const value = query[key];
    if (value === undefined || value === null || value === "") {
      continue;
    }
    params.set(key, String(value));
  }

  const queryString = params.toString();
  if (queryString) {
    url.search = queryString;
  }

  return url.toString();
}

export async function fetchJson(url) {
  const response = await fetch(url, { method: "GET" });
  if (!response.ok) {
    const body = await response.text().catch(function readFail() {
      return "";
    });
    throw new Error(`HTTP ${response.status} ${response.statusText}: ${body}`);
  }
  return response.json();
}
