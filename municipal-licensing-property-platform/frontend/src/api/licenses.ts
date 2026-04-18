import { apiFetch } from "./client";
import type { LicenseRecord } from "../types";

export function listLicenses() {
  return apiFetch<LicenseRecord[]>("/api/v1/licenses");
}

export function createLicense(payload: Record<string, unknown>) {
  return apiFetch<LicenseRecord>("/api/v1/licenses", {
    method: "POST",
    headers: {
      "Idempotency-Key": crypto.randomUUID()
    },
    body: JSON.stringify(payload)
  });
}
