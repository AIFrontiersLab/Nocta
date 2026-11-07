import { Card } from "@/components/ui/Card";

export function StatGrid({
  stats,
}: {
  stats: Array<{ label: string; value: string | number | null | undefined }>;
}) {
  return (
    <section className="mt-8 grid gap-4 md:grid-cols-4">
      {stats.map((item) => (
        <Card key={item.label} className="p-4">
          <div className="text-xs uppercase tracking-wide text-mute">{item.label}</div>
          <div className="mt-2 text-xl font-semibold">{item.value ?? "—"}</div>
        </Card>
      ))}
    </section>
  );
}
