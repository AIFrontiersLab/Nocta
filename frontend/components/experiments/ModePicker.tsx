"use client";

import clsx from "clsx";

export function ModePicker({
  modes,
  value,
  onChange,
}: {
  modes: string[];
  value: string;
  onChange: (mode: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {modes.map((mode) => (
        <button
          key={mode}
          type="button"
          onClick={() => onChange(mode)}
          className={clsx(
            "rounded-full px-3 py-1.5 text-sm transition",
            value === mode ? "bg-ink text-white" : "border border-line text-mute hover:bg-slate-50",
          )}
        >
          {mode}
        </button>
      ))}
    </div>
  );
}
