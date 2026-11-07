"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Loading } from "@/components/ui/Loading";
import { formatScore, formatUsd } from "@/lib/format";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8787/api";

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/analytics/overview`)
      .then(async (res) => {
        if (!res.ok) throw new Error(`API ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Analytics</h1>
      <p className="mt-2 text-mute">Lab performance across overnight runs.</p>
      {error && <div className="card mt-6 p-4 text-sm text-red-600">API error: {error}</div>}
      {!data && !error && <div className="mt-6"><Loading /></div>}
      {data && (
        <>
          <section className="mt-8 grid gap-4 md:grid-cols-4">
            <Card className="p-4">
              <div className="text-xs uppercase tracking-wide text-mute">Runs</div>
              <div className="mt-2 text-2xl font-semibold">{data.summary?.runs ?? 0}</div>
            </Card>
            <Card className="p-4">
              <div className="text-xs uppercase tracking-wide text-mute">Avg winner score</div>
              <div className="mt-2 text-2xl font-semibold">{formatScore(data.summary?.avg_winner_score)}</div>
            </Card>
            <Card className="p-4">
              <div className="text-xs uppercase tracking-wide text-mute">Prototype rate</div>
              <div className="mt-2 text-2xl font-semibold">
                {data.summary?.prototype_rate != null
                  ? `${Math.round(data.summary.prototype_rate * 100)}%`
                  : "—"}
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-xs uppercase tracking-wide text-mute">Est. cost</div>
              <div className="mt-2 text-2xl font-semibold">{formatUsd(data.summary?.total_estimated_cost_usd)}</div>
            </Card>
          </section>

          <section className="mt-8 grid gap-6 md:grid-cols-2">
            <Card>
              <h2 className="font-display text-xl font-semibold">Top technologies</h2>
              <div className="mt-4 space-y-2">
                {(data.top_technologies || []).length ? (
                  data.top_technologies.map((row: any) => (
                    <div key={row.label} className="flex items-center justify-between text-sm">
                      <span>{row.label}</span>
                      <span className="text-mute">{row.value}</span>
                    </div>
                  ))
                ) : (
                  <EmptyState title="No technology tags yet" />
                )}
              </div>
            </Card>
            <Card>
              <h2 className="font-display text-xl font-semibold">Recent runs</h2>
              <div className="mt-4 space-y-3">
                {(data.recent_runs || []).map((run: any) => (
                  <div key={run.run_id} className="flex items-center justify-between text-sm">
                    <div>
                      <div className="font-medium">{run.run_id}</div>
                      <div className="text-xs text-mute">{run.mode || "auto"} · {run.status}</div>
                    </div>
                    <div className="score-pill">{formatScore(run.winner_score)}</div>
                  </div>
                ))}
              </div>
            </Card>
          </section>
        </>
      )}
    </Shell>
  );
}
