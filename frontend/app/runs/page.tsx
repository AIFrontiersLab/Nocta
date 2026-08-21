"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function RunsPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    api.runs().then((d) => setItems(d.items || []));
    const t = setInterval(() => api.runs().then((d) => setItems(d.items || [])), 4000);
    return () => clearInterval(t);
  }, []);

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Runs</h1>
      <div className="mt-6 space-y-3">
        {items.map((run) => (
          <Link key={run.id} href={`/runs/${run.id}`} className="card block p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="font-semibold">{run.mode}</div>
                <div className="text-sm text-mute">{run.theme}</div>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-sm">{run.status}</span>
            </div>
          </Link>
        ))}
      </div>
    </Shell>
  );
}
