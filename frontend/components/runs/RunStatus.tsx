import { Badge } from "@/components/ui/Badge";

const toneMap: Record<string, "success" | "warn" | "danger" | "info" | "default"> = {
  completed: "success",
  ok: "success",
  running: "info",
  failed: "danger",
  error: "danger",
  pending: "warn",
};

export function RunStatus({ status }: { status: string }) {
  const tone = toneMap[status?.toLowerCase?.()] || "default";
  return <Badge tone={tone}>{status || "unknown"}</Badge>;
}
