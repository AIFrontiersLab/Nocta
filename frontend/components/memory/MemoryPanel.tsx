import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";

export function MemoryPanel({
  learnings,
}: {
  learnings: Array<{ id?: string; title?: string; detail?: string }>;
}) {
  if (!learnings.length) {
    return <EmptyState title="Memory is empty" detail="Run an experiment to accumulate lab memory." />;
  }
  return (
    <div className="grid gap-4">
      {learnings.map((item, idx) => (
        <Card key={item.id || idx}>
          <h3 className="font-semibold">{item.title || "Learning"}</h3>
          <p className="mt-2 text-sm text-mute">{item.detail}</p>
        </Card>
      ))}
    </div>
  );
}
