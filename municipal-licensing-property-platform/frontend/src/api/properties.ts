import { apiFetch } from "./client";
import type { DocumentRecord, PropertyRecord } from "../types";

export function listProperties() {
  return apiFetch<PropertyRecord[]>("/api/v1/properties");
}

export function createProperty(payload: Record<string, unknown>) {
  return apiFetch<PropertyRecord>("/api/v1/properties", {
    method: "POST",
    headers: {
      "Idempotency-Key": crypto.randomUUID()
    },
    body: JSON.stringify(payload)
  });
}

export function getProperty(propertyId: string) {
  return apiFetch<PropertyRecord>(`/api/v1/properties/${propertyId}`);
}

export function updateProperty(propertyId: string, payload: Record<string, unknown>) {
  return apiFetch<PropertyRecord>(`/api/v1/properties/${propertyId}`, {
    method: "PUT",
    headers: {
      "Idempotency-Key": crypto.randomUUID()
    },
    body: JSON.stringify(payload)
  });
}

export function listPropertyDocuments(propertyId: string) {
  return apiFetch<DocumentRecord[]>(`/api/v1/properties/${propertyId}/documents`);
}
