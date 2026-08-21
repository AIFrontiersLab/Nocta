"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

const categories = ["all", "technology", "research", "market", "business", "developer", "hardware", "security", "regulation"];

export default function SignalsPage() {
  const [category, setCategory] = useState("all");
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    api.signals(category === "all" ? undefined : category).then((d) => setItems(d.items || []));
  }, [category]);

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Signals</h1>
      <div className="mt-4 flex flex-wrap gap-2">
        {categories.map((c) => (
          <button key={c} onClick={() => setCategory(c)} className={`rounded-full px-3 py-1 text-sm capitalize ${category === c ? "bg-ink text-white" : "border border-line"}`}>
            {c}
          </button>
        ))}
      </div>
      <div className="mt-6 grid gap-4">
        {items.map((sig) => (
          <div key={sig.id} className="card p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-lg font-semibold">{sig.title}</h2>
              <span className="text-xs uppercase tracking-wide text-mute">{sig.claim_type}</span>
            </div>
            <p className="mt-2 text-sm text-mute">{sig.summary}</p>
            <div className="mt-4 flex flex-wrap gap-3 text-xs text-mute">
              <span>{sig.source}</span>
              <span>Novelty {sig.novelty_score}</span>
              <span>Momentum {sig.momentum_score}</span>
              <span>Confidence {sig.confidence}</span>
            </div>
          </div>
        ))}
      </div>
    </Shell>
  );
}
