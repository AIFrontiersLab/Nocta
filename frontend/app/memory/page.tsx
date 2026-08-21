"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function MemoryPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.memory().then(setData);
  }, []);

  if (!data) return <Shell><div>Loading…</div></Shell>;

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Memory</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-4">
        {Object.entries(data.metrics || {}).map(([k, v]) => (
          <div key={k} className="card p-4">
            <div className="text-xs uppercase tracking-wide text-mute">{k.replaceAll("_", " ")}</div>
            <div className="mt-2 text-2xl font-semibold">{String(v)}</div>
          </div>
        ))}
      </div>
      <section className="mt-10">
        <h2 className="font-display text-2xl font-semibold">FutureLab has learned</h2>
        <div className="mt-4 space-y-3">
          {(data.learnings || []).map((item: any) => (
            <div key={item.id} className="card p-5">
              <p className="font-medium">&ldquo;{item.learning}&rdquo;</p>
              <p className="mt-2 text-sm text-mute">Evidence: {(item.evidence || []).join(" · ")}</p>
            </div>
          ))}
        </div>
      </section>
    </Shell>
  );
}
