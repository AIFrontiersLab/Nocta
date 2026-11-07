export function EmptyState({ title, detail }: { title: string; detail?: string }) {
  return (
    <div className="card p-8 text-center">
      <h3 className="font-display text-xl font-semibold">{title}</h3>
      {detail && <p className="mt-2 text-sm text-mute">{detail}</p>}
    </div>
  );
}
