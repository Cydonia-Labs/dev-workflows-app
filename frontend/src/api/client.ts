/**
 * Base HTTP client for API calls.
 *
 * Wraps fetch with the Authorization header from localStorage and
 * consistent error handling. All API functions use this instead
 * of calling fetch directly.
 */

/** Key used to store the JWT in localStorage. */
const TOKEN_KEY = "auth_token";

/** Get the stored JWT token, or null if not logged in. */
export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/** Store a JWT token after login. */
export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/** Remove the stored JWT token on logout. */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Make an authenticated API request.
 *
 * Automatically attaches the Bearer token if available. Throws on
 * non-OK responses with the error detail from the API.
 *
 * @param path - API path (e.g., "/api/docs").
 * @param options - Standard fetch options (method, body, headers).
 * @returns The parsed JSON response.
 * @throws Error with the API error detail on non-OK responses.
 */
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? `HTTP ${response.status}`);
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
