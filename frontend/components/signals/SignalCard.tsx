import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { Signal } from "@/lib/types";

export function SignalCard({ signal }: { signal: Signal }) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold">{signal.title}</h3>
          <p className="mt-1 text-sm text-mute">{signal.summary}</p>
        </div>
        <Badge tone="info">{signal.source || "signal"}</Badge>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {(signal.tags || []).slice(0, 4).map((tag) => (
          <Badge key={tag}>{tag}</Badge>
        ))}
      </div>
    </Card>
  );
}
