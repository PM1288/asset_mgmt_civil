import { apiFetch } from "./client";
import type { DocumentRecord, LicenseRecord } from "../types";

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

export function getLicense(licenseId: string) {
  return apiFetch<LicenseRecord>(`/api/v1/licenses/${licenseId}`);
}

export function transitionLicense(
  licenseId: string,
  action: "submit" | "review" | "approve" | "reject" | "revoke",
  payload: Record<string, unknown>
) {
  return apiFetch<LicenseRecord>(`/api/v1/licenses/${licenseId}/${action}`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listLicenseDocuments(licenseId: string) {
  return apiFetch<DocumentRecord[]>(`/api/v1/licenses/${licenseId}/documents`);
}
