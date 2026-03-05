export function stripTrailingSlash(value: string): string {
  return String(value || "").replace(/\/+$/, "");
}

export function getApiBase(): string {
  const envBase = stripTrailingSlash(import.meta.env.VITE_API_BASE || "");
  if (envBase) {
    return envBase;
  }

  if (typeof window !== "undefined") {
    const host = String(window.location.hostname || "");
    if (host.includes("github.io")) {
      return "https://football-statistics-7wvr.onrender.com";
    }
  }

  return "http://127.0.0.1:10000";
}

export function buildApiUrl(
  path: string,
  query?: Record<string, string | number | boolean | undefined>
): string {
  if (!String(path).startsWith("/")) {
    throw new Error(`API path must start with "/". Received: ${path}`);
  }

  const base = getApiBase();
  const endpoint = `${base}${path}`;
  const url = new URL(endpoint);

  if (query) {
    const params = new URLSearchParams();
    const keys = Object.keys(query);
    let index = 0;
    while (index < keys.length) {
      const key = keys[index];
      const value = query[key];
      if (value !== undefined) {
        params.set(key, String(value));
      }
      index += 1;
    }
    const queryString = params.toString();
    if (queryString) {
      url.search = queryString;
    }
  }

  return url.toString();
}
