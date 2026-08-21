"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Shell } from "@/components/layout/Shell";
import { api } from "@/lib/api";

export default function ExperimentsPage() {
  const [modes, setModes] = useState<any[]>([]);
  const [mode, setMode] = useState("auto");
  const [theme, setTheme] = useState("Autonomous AI Agents");
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.modes().then((d) => setModes(d.items || []));
  }, []);

  const start = async () => {
    await api.startRun({ mode, theme, build: false });
    setMessage("Experiment queued. Watch progress on the Runs screen.");
  };

  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Experiments</h1>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="text-lg font-semibold">Start a run</h2>
          <label className="mt-4 block text-sm text-mute">Mode</label>
          <select className="mt-1 w-full rounded-xl border border-line p-3" value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="auto">Auto Discover</option>
            {modes.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
          <label className="mt-4 block text-sm text-mute">Theme</label>
          <input className="mt-1 w-full rounded-xl border border-line p-3" value={theme} onChange={(e) => setTheme(e.target.value)} />
          <button onClick={start} className="mt-4 rounded-full bg-ink px-5 py-2.5 text-sm font-semibold text-white">Start experiment</button>
          {message && <p className="mt-3 text-sm text-signal">{message}</p>}
        </div>
        <div className="card p-6">
          <h2 className="text-lg font-semibold">Modes</h2>
          <div className="mt-4 space-y-3">
            {modes.map((m) => (
              <div key={m.id} className="rounded-xl border border-line p-4">
                <div className="font-medium">{m.name}</div>
                <div className="text-sm text-mute">{m.question}</div>
              </div>
            ))}
          </div>
          <Link href="/runs" className="mt-4 inline-block text-sm font-semibold text-electric">View runs →</Link>
        </div>
      </div>
    </Shell>
  );
}
