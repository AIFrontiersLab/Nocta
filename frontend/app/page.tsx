"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

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
        <h1 className="mt-2 font-display text-5xl font-semibold tracking-tight md:text-6xl">FutureLab explored the frontier while you slept.</h1>
      </section>

      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="card relative overflow-hidden p-8 md:p-10"
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.08),transparent_45%),radial-gradient(circle_at_bottom_left,rgba(8,145,178,0.08),transparent_40%)]" />
        <div className="relative">
          <div className="kicker">Last night&apos;s invention</div>
          <h2 className="mt-3 font-display text-4xl font-semibold md:text-5xl">{winner?.name || "Awaiting first run"}</h2>
          <p className="mt-3 max-w-3xl text-lg text-mute">{winner?.one_liner}</p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <span className="score-pill">FutureLab Score {winner?.score?.toFixed?.(0) || "—"} / 100</span>
            <span className="rounded-full border border-line px-3 py-1 text-sm text-mute">
              Prototype: {stats?.prototype_status === "built" ? "BUILT" : stats?.prototype_status || "—"}
            </span>
            {winner?.is_demo && <span className="rounded-full bg-violet/10 px-3 py-1 text-sm text-violet">Demo data</span>}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            {winner && (
              <Link href={`/ideas/${winner.id}`} className="inline-flex items-center gap-2 rounded-full bg-ink px-5 py-2.5 text-sm font-semibold text-white">
                Explore Invention <ArrowRight size={16} />
              </Link>
            )}
            <Link href="/prototypes" className="inline-flex items-center gap-2 rounded-full border border-line px-5 py-2.5 text-sm font-semibold">
              View Prototype
            </Link>
          </div>
          {winner?.why_now && (
            <div className="mt-8 rounded-2xl border border-line bg-white/70 p-5">
              <div className="kicker">Why now</div>
              <p className="mt-2 text-mute">{winner.why_now}</p>
            </div>
          )}
        </div>
      </motion.section>

      <section className="mt-8 grid gap-4 md:grid-cols-4">
        {[
          ["Tonight's experiment", stats?.tonights_experiment],
          ["Signals analyzed", stats?.signals_analyzed],
          ["Ideas generated", stats?.ideas_generated],
          ["Ideas rejected", stats?.ideas_rejected],
          ["Finalists", stats?.finalists],
          ["Prototype status", stats?.prototype_status],
          ["Runtime", stats?.runtime ? `${Math.round(stats.runtime / 60)} min` : "—"],
          ["Estimated model cost", stats?.estimated_cost != null ? `$${stats.estimated_cost}` : "$0"],
        ].map(([label, value]) => (
          <div key={label} className="card p-4">
            <div className="text-xs uppercase tracking-wide text-mute">{label}</div>
            <div className="mt-2 text-xl font-semibold">{value ?? "—"}</div>
          </div>
        ))}
      </section>

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
