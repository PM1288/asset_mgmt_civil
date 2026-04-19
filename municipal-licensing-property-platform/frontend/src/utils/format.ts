export function formatDateTime(value?: string | null): string {
  if (!value) {
    return "Not available";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(parsed);
}

export function formatRelative(value?: string | null): string {
  if (!value) {
    return "Not scheduled";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  const diffMs = parsed.getTime() - Date.now();
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) {
    return "due today";
  }
  if (diffDays > 0) {
    return `due in ${diffDays} day${diffDays === 1 ? "" : "s"}`;
  }
  const overdueDays = Math.abs(diffDays);
  return `${overdueDays} day${overdueDays === 1 ? "" : "s"} overdue`;
}

export function compactNumber(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    notation: value >= 1000 ? "compact" : "standard",
    maximumFractionDigits: 1
  }).format(value);
}
