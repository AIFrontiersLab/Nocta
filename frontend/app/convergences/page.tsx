"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function ConvergencesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [active, setActive] = useState<any>(null);

  useEffect(() => {
    api.convergences().then((d) => {
      setItems(d.items || []);
      setActive((d.items || [])[0]);
    });
  }, []);

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Convergence map</h1>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        <div className="card min-h-[420px] p-6">
          <div className="flex flex-wrap gap-3">
            {items.flatMap((c) => c.nodes || []).filter((v: string, i: number, a: string[]) => a.indexOf(v) === i).map((node: string) => (
              <button key={node} className="rounded-full border border-line bg-white px-4 py-2 text-sm font-medium">{node}</button>
            ))}
          </div>
          <div className="mt-8 space-y-3">
            {items.map((c) => (
              <button key={c.id} onClick={() => setActive(c)} className={`block w-full rounded-2xl border p-4 text-left ${active?.id === c.id ? "border-electric bg-blue-50/40" : "border-line"}`}>
                <div className="font-semibold">{c.title}</div>
                <div className="text-sm text-mute">Strength {c.strength}</div>
              </button>
            ))}
          </div>
        </div>
        {active && (
          <div className="card p-6">
            <h2 className="font-display text-2xl font-semibold">{active.title}</h2>
            <p className="mt-3 text-mute">{active.why_connect}</p>
            <div className="mt-6">
              <div className="kicker">Possible consequences</div>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-mute">
                {(active.consequences || []).map((x: string) => <li key={x}>{x}</li>)}
              </ul>
            </div>
            <div className="mt-6">
              <div className="kicker">Product opportunities</div>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-mute">
                {(active.opportunities || []).map((x: string) => <li key={x}>{x}</li>)}
              </ul>
            </div>
          </div>
        )}
      </div>
    </Shell>
  );
}
