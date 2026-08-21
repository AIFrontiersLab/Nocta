"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function IdeaDetailPage({ params }: { params: { id: string } }) {
  const [idea, setIdea] = useState<any>(null);

  useEffect(() => {
    api.idea(params.id).then(setIdea);
  }, [params.id]);

  if (!idea) return <Shell><div>Loading…</div></Shell>;

  const sections = [
    ["The idea", idea.one_liner],
    ["Human problem", idea.problem],
    ["Future thesis", idea.future_thesis],
    ["Why now", idea.why_now],
    ["Product", idea.product],
    ["First customer", idea.first_customer],
    ["Market", idea.market],
    ["Why this may win", idea.why_may_win],
    ["Why this may fail", idea.why_may_fail],
    ["Architecture", idea.architecture],
    ["MVP", idea.mvp],
  ];

  return (
    <Shell>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="kicker">Idea detail</p>
          <h1 className="font-display text-4xl font-semibold">{idea.name}</h1>
          <p className="mt-2 max-w-3xl text-lg text-mute">{idea.one_liner}</p>
        </div>
        <span className="score-pill text-base">Score {idea.score?.toFixed?.(0)} / 100</span>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {sections.map(([title, body]) => (
          <div key={title} className="card p-5">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-electric">{title}</h2>
            <p className="mt-2 whitespace-pre-wrap text-mute">{body || "—"}</p>
          </div>
        ))}
      </div>

      <section className="mt-8">
        <h2 className="font-display text-2xl font-semibold">Agent debate</h2>
        <div className="mt-4 grid gap-3">
          {(idea.agent_debate || []).map((ev: any) => (
            <div key={ev.id} className="card p-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-cyan">{ev.role}</div>
              <p className="mt-2 font-medium">&ldquo;{ev.quote}&rdquo;</p>
              <p className="mt-2 text-sm text-mute">{ev.full_text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-8">
        <h2 className="font-display text-2xl font-semibold">Feedback</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {["love", "interesting", "maybe", "not_interesting", "never_again"].map((reaction) => (
            <button
              key={reaction}
              className="rounded-full border border-line px-3 py-1 text-sm"
              onClick={() => api.feedback(idea.id, { reaction })}
            >
              {reaction.replace("_", " ")}
            </button>
          ))}
        </div>
      </section>
    </Shell>
  );
}
