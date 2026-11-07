"use client";

import { useEffect, useState } from "react";
import { IdeaCard } from "@/components/ideas/IdeaCard";
import { Shell } from "@/components/layout/Shell";
import { EmptyState } from "@/components/ui/EmptyState";
import { api } from "@/lib/api";
import type { Idea } from "@/lib/types";

const filters = ["all", "exceptional", "prototype_candidates", "watch", "archived", "rejected", "resurrected"];

export default function IdeasPage() {
  const [status, setStatus] = useState("all");
  const [items, setItems] = useState<Idea[]>([]);

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
          <IdeaCard key={idea.id} idea={idea} />
        ))}
      </div>
      {!items.length && <div className="mt-6"><EmptyState title="No ideas for this filter" detail="Run an experiment or switch filters." /></div>}
    </Shell>
  );
}
