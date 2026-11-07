export function formatScore(value?: number | null): string {
  if (value == null || Number.isNaN(value)) return "—";
  return value.toFixed(0);
}

export function formatUsd(value?: number | null): string {
  if (value == null || Number.isNaN(value)) return "$0";
  return `$${value.toFixed(value < 1 ? 3 : 2)}`;
}

export function formatRuntime(seconds?: number | null): string {
  if (!seconds) return "—";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  return `${Math.round(seconds / 60)} min`;
}

export function titleCase(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
