import { apiFetch } from "./client";
import type { PropertyRecord } from "../types";

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
