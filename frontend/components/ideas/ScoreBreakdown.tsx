import { ScoreBar } from "@/components/ui/ScoreBar";

export function ScoreBreakdown({
  dimensions,
}: {
  dimensions: Array<{ key: string; score: number; reason?: string }>;
}) {
  return (
    <div className="space-y-3">
      {dimensions.map((dim) => (
        <div key={dim.key}>
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="font-medium capitalize">{dim.key.replace(/_/g, " ")}</span>
            <span className="text-mute">{dim.score.toFixed(1)}</span>
          </div>
          <ScoreBar score={dim.score} max={10} />
          {dim.reason && <p className="mt-1 text-xs text-mute">{dim.reason}</p>}
        </div>
      ))}
    </div>
  );
}
