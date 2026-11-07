import type { TimelineEvent } from "@/lib/types";

export function Timeline({ events }: { events: TimelineEvent[] }) {
  if (!events.length) {
    return <p className="text-sm text-mute">No timeline events yet.</p>;
  }
  return (
    <ol className="space-y-4 border-l border-line pl-4">
      {events.map((event) => (
        <li key={event.id} className="relative">
          <span className="absolute -left-[1.4rem] top-1.5 h-2.5 w-2.5 rounded-full bg-cyan" />
          <div className="text-xs uppercase tracking-wide text-mute">{event.stage}</div>
          <div className="mt-1 text-sm font-medium">{event.message}</div>
          {event.agent && <div className="mt-1 text-xs text-mute">Agent: {event.agent}</div>}
        </li>
      ))}
    </ol>
  );
}
