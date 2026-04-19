import { apiFetch } from "./client";
import type { WorkflowEventRecord } from "../types";

export function listWorkflowHistory(aggregateType: "property" | "license", aggregateId: string) {
  return apiFetch<WorkflowEventRecord[]>(
    `/api/v1/workflows/${aggregateType}/${aggregateId}/history`
  );
}
