"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

const filters = ["all", "exceptional", "prototype_candidates", "watch", "archived", "rejected", "resurrected"];

export default function IdeasPage() {
  const [status, setStatus] = useState("all");
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    api.ideas(status).then((d) => setItems(d.items || []));
  }, [status]);

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Ideas</h1>
      <div className="mt-4 flex flex-wrap gap-2">
        {filters.map((f) => (
          <button key={f} onClick={() => setStatus(f)} className={`rounded-full px-3 py-1 text-sm ${status === f ? "bg-ink text-white" : "border border-line"}`}>
            {f.replace("_", " ")}
          </button>
        ))}
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {items.map((idea) => (
          <Link key={idea.id} href={`/ideas/${idea.id}`} className="card p-5 transition hover:-translate-y-0.5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold">{idea.name}</h2>
                <p className="mt-1 text-sm text-mute">{idea.one_liner}</p>
              </div>
              <span className="score-pill">{idea.score?.toFixed?.(0)}</span>
            </div>
            <div className="mt-4 text-xs uppercase tracking-wide text-mute">Mode: {idea.mode} · {idea.status}</div>
          </Link>
        ))}
      </div>
    </Shell>
  );
}
