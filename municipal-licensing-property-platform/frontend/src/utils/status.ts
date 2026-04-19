export function statusTone(status: string): "neutral" | "ok" | "warning" | "critical" | "info" {
  switch (status) {
    case "approved":
    case "active":
    case "ok":
      return "ok";
    case "submitted":
    case "under_review":
    case "pending":
      return "warning";
    case "rejected":
    case "revoked":
    case "critical":
      return "critical";
    case "draft":
      return "neutral";
    default:
      return "info";
  }
}

export function humanStatus(status: string): string {
  return status
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}
