"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function ResurrectionsPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    api.resurrections().then((d) => setItems(d.items || []));
  }, []);

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Ideas whose time may have come</h1>
      <div className="mt-6 grid gap-4">
        {items.map((idea) => (
          <div key={idea.id} className="card p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-xl font-semibold">{idea.name}</h2>
              <span className="score-pill">{idea.original_score ?? "—"} → {idea.score?.toFixed?.(0)}</span>
            </div>
            <p className="mt-2 text-sm text-mute">{idea.one_liner}</p>
            <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-mute">
              {(idea.resurrection?.what_changed || ["Conditions changed since original rejection"]).map((x: string) => <li key={x}>{x}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </Shell>
  );
}
