"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function RunDetailPage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const load = () => api.run(params.id).then(setData);
    load();
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, [params.id]);

  if (!data) return <Shell><div>Loading…</div></Shell>;

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Experiment timeline</h1>
      <p className="mt-2 text-mute">{data.run.mode} · {data.run.status}</p>
      <div className="mt-8 space-y-3">
        {(data.timeline || []).map((evt: any) => (
          <div key={evt.id} className="card p-4">
            <div className="text-xs text-mute">{evt.occurred_at}</div>
            <div className="font-medium">{evt.message}</div>
          </div>
        ))}
      </div>
    </Shell>
  );
}
