import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { formatScore, titleCase } from "@/lib/format";
import type { Idea } from "@/lib/types";

export function IdeaCard({ idea }: { idea: Idea }) {
  return (
    <Link href={`/ideas/${idea.id}`}>
      <Card hover>
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold">{idea.name}</h2>
            <p className="mt-1 text-sm text-mute">{idea.one_liner}</p>
          </div>
          <span className="score-pill">{formatScore(idea.score)}</span>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Badge tone="info">{titleCase(idea.status || "unknown")}</Badge>
          {idea.mode && <Badge>{titleCase(idea.mode)}</Badge>}
          {idea.is_demo && <Badge tone="violet">Demo</Badge>}
        </div>
      </Card>
    </Link>
  );
}
