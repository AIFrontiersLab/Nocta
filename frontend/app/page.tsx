"use client";

import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { HeroInvention } from "@/components/home/HeroInvention";
import { StatGrid } from "@/components/home/StatGrid";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";
import { formatRuntime, formatUsd } from "@/lib/format";

export default function HomePage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.home().then(setData).catch((e) => setError(e.message));
  }, []);

  const winner = data?.hero?.winner;
  const stats = data?.stats;
  const chain = data?.reasoning_chain || [];

  return (
    <Shell>
      {error && <div className="card mb-6 p-4 text-sm text-red-600">API error: {error}. Start backend on :8787</div>}
      <section className="mb-10">
        <p className="kicker">Good morning</p>
        <h1 className="mt-2 font-display text-5xl font-semibold tracking-tight md:text-6xl">
          FutureLab explored the frontier while you slept.
        </h1>
      </section>

      <HeroInvention winner={winner} prototypeStatus={stats?.prototype_status} />

      <StatGrid
        stats={[
          { label: "Tonight's experiment", value: stats?.tonights_experiment },
          { label: "Signals analyzed", value: stats?.signals_analyzed },
          { label: "Ideas generated", value: stats?.ideas_generated },
          { label: "Ideas rejected", value: stats?.ideas_rejected },
          { label: "Finalists", value: stats?.finalists },
          { label: "Prototype status", value: stats?.prototype_status },
          { label: "Runtime", value: formatRuntime(stats?.runtime) },
          { label: "Estimated model cost", value: formatUsd(stats?.estimated_cost) },
        ]}
      />

      <section className="mt-10">
        <div className="mb-4 flex items-center gap-2">
          <Sparkles className="text-electric" size={18} />
          <h3 className="font-display text-2xl font-semibold">Why FutureLab chose this</h3>
        </div>
        <div className="card flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between">
          {chain.map((step: any, idx: number) => (
            <div key={`${step.id}-${idx}`} className="flex items-center gap-4">
              <div className="min-w-[140px]">
                <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-cyan">{step.type}</div>
                <div className="mt-1 text-sm font-medium">{step.label}</div>
              </div>
              {idx < chain.length - 1 && <div className="hidden text-mute md:block">↓</div>}
            </div>
          ))}
        </div>
      </section>
    </Shell>
  );
}
