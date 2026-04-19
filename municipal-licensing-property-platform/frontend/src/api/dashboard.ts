import { apiFetch } from "./client";
import type {
  DashboardCompliance,
  DashboardHealthSummary,
  DashboardQueues,
  DashboardRecentActivity,
  DashboardSummary
} from "../types";

export function getDashboardSummary() {
  return apiFetch<DashboardSummary>("/api/v1/dashboard/summary");
}

export function getDashboardQueues() {
  return apiFetch<DashboardQueues>("/api/v1/dashboard/queues");
}

export function getDashboardRecentActivity() {
  return apiFetch<DashboardRecentActivity>("/api/v1/dashboard/recent-activity");
}

export function getDashboardCompliance() {
  return apiFetch<DashboardCompliance>("/api/v1/dashboard/upcoming-renewals");
}

export function getDashboardHealthSummary() {
  return apiFetch<DashboardHealthSummary>("/api/v1/dashboard/health-summary");
}
