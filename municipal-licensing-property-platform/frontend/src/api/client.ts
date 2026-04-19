import keycloak from "../auth/keycloak";

export async function authorizedFetch(path: string, init?: RequestInit): Promise<Response> {
  if (!keycloak.authenticated) {
    await keycloak.login();
    throw new Error("Not authenticated");
  }

  if (keycloak.isTokenExpired(30)) {
    await keycloak.updateToken(60);
  }

  const headers = new Headers(init?.headers || {});
  if (!(init?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  headers.set("Authorization", `Bearer ${keycloak.token}`);

  return fetch(path, {
    ...init,
    headers
  });
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await authorizedFetch(path, init);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status} ${response.statusText} ${text}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function apiUpload<T>(path: string, body: FormData): Promise<T> {
  return apiFetch<T>(path, {
    method: "POST",
    body
  });
}

export async function apiDownload(path: string, filename: string): Promise<void> {
  const response = await authorizedFetch(path);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status} ${response.statusText} ${text}`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
