import type { HealthEnvelope, Subject } from "../types";
import { apiFetch } from "./client";

export function getReadyHealth() {
  return apiFetch<HealthEnvelope>("/health/ready");
}

export function getCurrentSubject() {
  return apiFetch<Subject>("/api/v1/auth/me");
}

export function getDiagnostics() {
  return apiFetch<Record<string, unknown>>("/api/v1/admin/diagnostics/dependencies");
}
