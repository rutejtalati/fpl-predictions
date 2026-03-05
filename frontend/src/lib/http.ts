export class HttpRequestError extends Error {
  url: string;
  status?: number;
  responseBody?: string;
  isNetworkError: boolean;

  constructor(
    message: string,
    options: {
      url: string;
      status?: number;
      responseBody?: string;
      isNetworkError?: boolean;
    }
  ) {
    super(message);
    this.name = "HttpRequestError";
    this.url = options.url;
    this.status = options.status;
    this.responseBody = options.responseBody;
    this.isNetworkError = Boolean(options.isNetworkError);
  }
}

export function getErrorAttemptedUrl(error: unknown): string {
  if (error && typeof error === "object" && "url" in error) {
    const value = (error as { url?: unknown }).url;
    if (typeof value === "string") {
      return value;
    }
  }
  return "";
}

export async function fetchJson(url: string): Promise<any> {
  if (import.meta.env.DEV) {
    console.log("[HTTP] GET", url);
  }

  try {
    const response = await fetch(url, { method: "GET" });
    if (!response.ok) {
      const body = await response.text().catch(function readFail() {
        return "";
      });
      throw new HttpRequestError(`HTTP ${response.status}: ${body || "No response body"}`, {
        url,
        status: response.status,
        responseBody: body,
      });
    }
    return await response.json();
  } catch (error: unknown) {
    if (error instanceof HttpRequestError) {
      throw error;
    }
    if (error instanceof TypeError) {
      throw new HttpRequestError(
        `Network error (likely CORS / wrong URL / backend down) while requesting ${url}`,
        { url, isNetworkError: true }
      );
    }
    const message = error instanceof Error ? error.message : String(error);
    throw new HttpRequestError(`Request failed for ${url}: ${message}`, { url });
  }
}
