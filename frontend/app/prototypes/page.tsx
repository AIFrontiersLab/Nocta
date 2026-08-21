"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function PrototypesPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    api.prototypes().then((d) => setItems(d.items || []));
  }, []);

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Prototypes</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {items.map((p) => (
          <div key={p.id} className="card p-5">
            <h2 className="text-xl font-semibold">{p.name}</h2>
            <div className="mt-2 text-sm text-mute">Status: {p.status}</div>
            <div className="mt-2 text-sm text-mute">Stack: {(p.stack || []).join(", ")}</div>
            {p.github_url && (
              <a
                href={p.github_url}
                target="_blank"
                rel="noreferrer"
                className="mt-3 inline-block text-sm font-semibold text-blue-600 hover:underline"
              >
                View on GitHub →
              </a>
            )}
            <div className="mt-4 rounded-xl bg-slate-50 p-3 text-xs text-mute">{p.local_path}</div>
            {p.launch_command && <div className="mt-2 font-mono text-xs">{p.launch_command}</div>}
          </div>
        ))}
      </div>
    </Shell>
  );
}
