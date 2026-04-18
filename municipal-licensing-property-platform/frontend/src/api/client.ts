import keycloak from "../auth/keycloak";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  if (!keycloak.authenticated) {
    await keycloak.login();
    throw new Error("Not authenticated");
  }

  if (keycloak.isTokenExpired(30)) {
    await keycloak.updateToken(60);
  }

  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
      Authorization: `Bearer ${keycloak.token}`
    }
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status} ${response.statusText} ${text}`);
  }

  return response.json() as Promise<T>;
}
