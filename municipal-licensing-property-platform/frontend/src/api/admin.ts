import { apiFetch } from "./client";
import type { AuditLogRecord, DiagnosticsPayload } from "../types";

export function getAuditLog() {
  return apiFetch<AuditLogRecord[]>("/api/v1/admin/audit");
}

export function getDiagnosticsPayload() {
  return apiFetch<DiagnosticsPayload>("/api/v1/admin/diagnostics/dependencies");
}

export function runBackup() {
  return apiFetch<Record<string, unknown>>("/api/v1/admin/backups/run", {
    method: "POST"
  });
}

export function validateLatestBackup() {
  return apiFetch<Record<string, unknown>>("/api/v1/admin/backups/validate-latest", {
    method: "POST"
  });
}

export function triggerCleanup() {
  return apiFetch<Record<string, unknown>>("/api/v1/admin/maintenance/cleanup", {
    method: "POST"
  });
}
